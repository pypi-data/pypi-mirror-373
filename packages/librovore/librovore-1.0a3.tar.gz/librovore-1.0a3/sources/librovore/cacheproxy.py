# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' HTTP cache for documentation URL access. '''


from http import HTTPStatus as _HttpStatus
from urllib.parse import ParseResult as _Url
from urllib.robotparser import RobotFileParser as _RobotFileParser

import appcore.generics as _generics
import httpx as _httpx

from . import __
from . import exceptions as _exceptions


HttpClientFactory: __.typx.TypeAlias = (
    __.cabc.Callable[ [ ], _httpx.AsyncClient ] )
ContentResponse: __.typx.TypeAlias = _generics.Result[ bytes, Exception ]
ProbeResponse: __.typx.TypeAlias = _generics.Result[ bool, Exception ]
RobotsResponse: __.typx.TypeAlias = (
    _generics.Result[ _RobotFileParser, Exception ] )


class CacheEntry( __.immut.DataclassObject ):
    ''' Cache entry base. '''

    timestamp: float
    ttl: float

    @property
    def invalid( self ) -> bool:
        ''' Checks if cache entry has exceeded its TTL. '''
        return __.time.time( ) - self.timestamp > self.ttl


class ContentCacheEntry( CacheEntry ):
    ''' Cache entry for URL content with size tracking. '''

    response: ContentResponse
    headers: _httpx.Headers
    size_bytes: int

    @property
    def memory_usage( self ) -> int:
        ''' Calculates total memory usage including metadata. '''
        return self.size_bytes + 100  # Overhead estimate


class ProbeCacheEntry( CacheEntry ):
    ''' Cache entry for URL probe results. '''

    response: ProbeResponse


class RobotsCacheEntry( CacheEntry ):
    ''' Cache entry for robots.txt parser. '''

    response: RobotsResponse


class Cache( __.immut.Object ):
    ''' Cache base with shared configuration attributes. '''

    error_ttl: float = 30.0
    success_ttl: float = 300.0

    def __init__(
        self, *,
        error_ttl: __.Absential[ float ] = __.absent,
        success_ttl: __.Absential[ float ] = __.absent,
        delay_function: __.cabc.Callable[
            [ float ], __.cabc.Awaitable[ None ]
        ] = __.asyncio.sleep
    ) -> None:
        if not __.is_absent( error_ttl ): self.error_ttl = error_ttl
        if not __.is_absent( success_ttl ): self.success_ttl = success_ttl
        self.delay_function = delay_function
        self._request_mutexes: dict[ str, __.asyncio.Lock ] = { }

    @__.ctxl.asynccontextmanager
    async def acquire_mutex_for( self, url: str ):
        ''' Acquires mutex for HTTP request deduplication. '''
        if url not in self._request_mutexes: # pragma: no branch
            self._request_mutexes[ url ] = __.asyncio.Lock( )
        mutex = self._request_mutexes[ url ]
        async with mutex:
            try: yield
            finally: self._request_mutexes.pop( url, None )


class RobotsCache( Cache ):
    ''' Cache manager for robots.txt files with crawl delay tracking. '''

    entries_max: int = 500
    request_timeout: float = 5.0
    ttl: float = 3600.0
    user_agent: str = '*'

    def __init__(
        self, *,
        entries_max: __.Absential[ int ] = __.absent,
        ttl: __.Absential[ float ] = __.absent,
        request_timeout: __.Absential[ float ] = __.absent,
        user_agent: __.Absential[ str ] = __.absent,
        **base_initargs: __.typx.Any
    ) -> None:
        super( ).__init__( **base_initargs )
        if not __.is_absent( entries_max ): self.entries_max = entries_max
        if not __.is_absent( ttl ): self.ttl = ttl
        if not __.is_absent( request_timeout ):
            self.request_timeout = request_timeout
        if not __.is_absent( user_agent ): self.user_agent = user_agent
        self._cache: dict[ str, RobotsCacheEntry ] = { }
        self._recency: __.collections.deque[ str ] = __.collections.deque( )
        self._request_delays: dict[ str, float ] = { }

    @classmethod
    def from_configuration(
        cls, configuration: __.cabc.Mapping[ str, __.typx.Any ]
    ) -> __.typx.Self:
        ''' Creates RobotsCache instance from application configuration. '''
        cache_config = configuration.get( 'cache', { } )
        robots_ttl = cache_config.get( 'robots-ttl', 3600.0 )
        return cls( ttl = robots_ttl )

    async def access( self, domain: str ) -> __.Absential[ _RobotFileParser ]:
        ''' Retrieves cached robots.txt parser if valid. '''
        if domain not in self._cache: return __.absent
        entry = self._cache[ domain ]
        if entry.invalid:
            self._remove( domain )
            return __.absent
        self._record_access( domain )
        return entry.response.extract( )

    def assign_delay( self, domain: str, delay_seconds: float ) -> None:
        ''' Sets next allowed request time for domain. '''
        self._request_delays[ domain ] = __.time.time( ) + delay_seconds

    def calculate_delay_remainder( self, domain: str ) -> float:
        ''' Returns remaining crawl delay time for domain. '''
        allow_at = self._request_delays.get( domain, 0.0 )
        if not allow_at: return 0.0
        remainder = allow_at - __.time.time( )
        return max( 0.0, remainder )

    def determine_ttl( self, response: RobotsResponse ) -> float:
        ''' Determines appropriate TTL based on response type. '''
        if response.is_value( ): return self.ttl
        return self.error_ttl

    async def store(
        self, domain: str, response: RobotsResponse, ttl: float
    ) -> None:
        ''' Stores robots.txt parser in cache. '''
        entry = RobotsCacheEntry(
            response = response, timestamp = __.time.time( ), ttl = ttl )
        self._cache[ domain ] = entry
        self._record_access( domain )
        self._evict_by_count( )

    def _evict_by_count( self ) -> None:
        ''' Evicts oldest entries when cache exceeds max size. '''
        while (
            len( self._cache ) > self.entries_max
            and self._recency
        ):
            lru_domain = self._recency.popleft( )
            if lru_domain in self._cache: # pragma: no branch
                del self._cache[ lru_domain ]

    def _record_access( self, domain: str ) -> None:
        ''' Updates LRU access order for given domain. '''
        with __.ctxl.suppress( ValueError ):
            self._recency.remove( domain )
        self._recency.append( domain )

    def _remove( self, domain: str ) -> None:
        ''' Removes entry from cache. '''
        self._cache.pop( domain, None )
        with __.ctxl.suppress( ValueError ):
            self._recency.remove( domain )


class ContentCache( Cache, instances_mutables = ( '_memory_total', ) ):
    ''' Cache manager for URL content (GET requests) with memory tracking. '''

    memory_max: int = 32 * 1024 * 1024

    def __init__(
        self, *,
        robots_cache: __.Absential[ RobotsCache ] = __.absent,
        memory_max: __.Absential[ int ] = __.absent,
        **base_initargs: __.typx.Any
    ) -> None:
        super( ).__init__( **base_initargs )
        if __.is_absent( robots_cache ):
            self.robots_cache = RobotsCache( **base_initargs )
        else: self.robots_cache = robots_cache
        if not __.is_absent( memory_max ): self.memory_max = memory_max
        self._cache: dict[ str, ContentCacheEntry ] = { }
        self._memory_total = 0
        self._recency: __.collections.deque[ str ] = __.collections.deque( )

    @classmethod
    def from_configuration(
        cls,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        robots_cache: __.Absential[ RobotsCache ] = __.absent
    ) -> __.typx.Self:
        ''' Creates ContentCache instance from application configuration. '''
        cache_config = configuration.get( 'cache', { } )
        content_ttl = cache_config.get( 'content-ttl', 300.0 )
        memory_limit = cache_config.get( 'memory-limit', 33554432 )
        nomargs = {
            'success_ttl': content_ttl,
            'memory_max': memory_limit,
        }
        if not __.is_absent( robots_cache ):
            nomargs[ 'robots_cache' ] = robots_cache
        return cls( **nomargs )

    async def access(
        self, url: str
    ) -> __.Absential[ tuple[ bytes, _httpx.Headers ] ]:
        ''' Retrieves cached content if valid. '''
        if url not in self._cache: return __.absent
        entry = self._cache[ url ]
        if entry.invalid:
            self._remove( url )
            return __.absent
        self._record_access( url )
        return ( entry.response.extract( ), entry.headers )

    def determine_ttl( self, response: ContentResponse ) -> float:
        ''' Determines appropriate TTL based on response type. '''
        if response.is_value( ):
            return self.success_ttl
        # TODO: Inspect exception type for more granular TTL
        return self.error_ttl

    async def retrieve_url(
        self,
        url: _Url, /, *,
        duration_max: float = 30.0,
        client_factory: HttpClientFactory = _httpx.AsyncClient,
    ) -> bytes:
        ''' Convenience method for retrieving URL content. '''
        return await retrieve_url(
            self, url,
            duration_max = duration_max,
            client_factory = client_factory )

    async def store(
        self, url: str, response: ContentResponse,
        headers: _httpx.Headers, ttl: float
    ) -> None:
        ''' Stores content in cache with memory management. '''
        size_bytes = self._calculate_response_size( response )
        entry = ContentCacheEntry(
            response = response,
            headers = headers,
            timestamp = __.time.time( ),
            ttl = ttl,
            size_bytes = size_bytes )
        if old_entry := self._cache.get( url ):
            self._memory_total -= old_entry.memory_usage
        self._cache[ url ] = entry
        self._memory_total += entry.memory_usage
        self._record_access( url )
        self._evict_by_memory( )

    def _calculate_response_size( self, response: ContentResponse ) -> int:
        ''' Calculates memory footprint of cached response. '''
        if response.is_value( ):
            content = response.extract( )
            return len( content )
        return 100  # Conservative estimate for exception overhead

    def _evict_by_memory( self ) -> None:
        ''' Evicts LRU entries until memory usage is under limit. '''
        while (
            self._memory_total > self.memory_max
            and self._recency
        ):
            lru_url = self._recency.popleft( )
            if lru_url in self._cache: # pragma: no branch
                entry = self._cache[ lru_url ]
                self._memory_total -= entry.memory_usage
                del self._cache[ lru_url ]
                _scribe.debug( f"Evicted cache entry: {lru_url}" )

    def _record_access( self, url: str ) -> None:
        ''' Updates LRU access order for given URL. '''
        with __.ctxl.suppress( ValueError ):
            self._recency.remove( url )
        self._recency.append( url )

    def _remove( self, url: str ) -> None:
        ''' Removes entry from cache and updates memory tracking. '''
        if entry := self._cache.pop( url, None ):
            self._memory_total -= entry.memory_usage
            with __.ctxl.suppress( ValueError ):
                self._recency.remove( url )


class ProbeCache( Cache ):
    ''' Cache manager for URL probe results (HEAD requests). '''

    entries_max: int = 1000

    def __init__(
        self, *,
        robots_cache: __.Absential[ RobotsCache ] = __.absent,
        entries_max: __.Absential[ int ] = __.absent,
        **base_initargs: __.typx.Any
    ) -> None:
        super( ).__init__( **base_initargs )
        if __.is_absent( robots_cache ):
            self.robots_cache = RobotsCache( **base_initargs )
        else: self.robots_cache = robots_cache
        if not __.is_absent( entries_max ): self.entries_max = entries_max
        self._cache: dict[ str, ProbeCacheEntry ] = { }
        self._recency: __.collections.deque[ str ] = __.collections.deque( )

    @classmethod
    def from_configuration(
        cls,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        robots_cache: __.Absential[ RobotsCache ] = __.absent
    ) -> __.typx.Self:
        ''' Creates ProbeCache instance from application configuration. '''
        cache_config = configuration.get( 'cache', { } )
        probe_ttl = cache_config.get( 'probe-ttl', 300.0 )
        nomargs = { 'success_ttl': probe_ttl }
        if not __.is_absent( robots_cache ):
            nomargs[ 'robots_cache' ] = robots_cache
        return cls( **nomargs )

    async def access( self, url: str ) -> __.Absential[ bool ]:
        ''' Retrieves cached probe result if valid. '''
        if url not in self._cache: return __.absent
        entry = self._cache[ url ]
        if entry.invalid:
            self._remove( url )
            return __.absent
        self._record_access( url )
        return entry.response.extract( )

    def determine_ttl( self, response: ProbeResponse ) -> float:
        ''' Determines appropriate TTL based on response type. '''
        if response.is_value( ):
            return self.success_ttl
        # TODO: Inspect exception type for more granular TTL
        return self.error_ttl

    async def probe_url(
        self,
        url: _Url, /, *,
        duration_max: float = 10.0,
        client_factory: HttpClientFactory = _httpx.AsyncClient,
    ) -> bool:
        ''' Convenience method for probing URL existence. '''
        return await probe_url(
            self, url,
            duration_max = duration_max,
            client_factory = client_factory )

    async def store(
        self, url: str, response: ProbeResponse, ttl: float
    ) -> None:
        ''' Stores probe result in cache. '''
        entry = ProbeCacheEntry(
            response = response,
            timestamp = __.time.time( ),
            ttl = ttl )
        self._cache[ url ] = entry
        self._record_access( url )
        self._evict_by_count( )

    def _evict_by_count( self ) -> None:
        ''' Evicts oldest entries when cache exceeds max size. '''
        while (
            len( self._cache ) > self.entries_max
            and self._recency
        ):
            lru_url = self._recency.popleft( )
            if lru_url in self._cache: # pragma: no branch
                del self._cache[ lru_url ]

    def _record_access( self, url: str ) -> None:
        ''' Updates LRU access order for given URL. '''
        with __.ctxl.suppress( ValueError ):
            self._recency.remove( url )
        self._recency.append( url )

    def _remove( self, url: str ) -> None:
        ''' Removes entry from cache. '''
        self._cache.pop( url, None )
        with __.ctxl.suppress( ValueError ):
            self._recency.remove( url )


_http_success_threshold = 400


_scribe = __.acquire_scribe( __name__ )


def prepare(
    auxdata: __.Globals
) -> tuple[ ContentCache, ProbeCache, RobotsCache ]:
    ''' Prepares cache instances from configuration.

        Returns cache instances constructed from application configuration.
    '''
    configuration = auxdata.configuration
    robots_cache = RobotsCache.from_configuration( configuration )
    return (
        ContentCache.from_configuration( configuration, robots_cache ),
        ProbeCache.from_configuration( configuration, robots_cache ),
        robots_cache,
    )


async def probe_url(
    cache: ProbeCache,
    url: _Url, *,
    duration_max: float = 10.0,
    client_factory: HttpClientFactory = _httpx.AsyncClient,
) -> bool:
    ''' Cached HEAD request to check URL existence. '''
    url_s = url.geturl( )
    match url.scheme:
        case '' | 'file':
            return __.Path( url.path ).exists( )
        case 'http' | 'https':
            result = await cache.access( url_s )
            if not __.is_absent( result ): return result
            async with client_factory( ) as client:
                result = await _probe_url(
                    url, duration_max = duration_max,
                    client = client,
                    probe_cache = cache,
                    robots_cache = cache.robots_cache )
            ttl = cache.determine_ttl( result )
            await cache.store( url_s, result, ttl )
            return result.extract( )
        case _: return False


async def retrieve_url(
    cache: ContentCache,
    url: _Url, *,
    duration_max: float = 30.0,
    client_factory: HttpClientFactory = _httpx.AsyncClient,
) -> bytes:
    ''' Cached GET request to fetch URL content as bytes. '''
    url_s = url.geturl( )
    match url.scheme:
        case '' | 'file':
            location = __.Path( url.path )
            try: return location.read_bytes( )
            except Exception as exc:
                raise _exceptions.DocumentationInaccessibility(
                    url_s, exc ) from exc
        case 'http' | 'https':
            result = await cache.access( url_s )
            if not __.is_absent( result ):
                content_bytes, _ = result
                return content_bytes
            async with client_factory( ) as client:
                result, headers = await _retrieve_url(
                    url,
                    duration_max = duration_max,
                    client = client,
                    content_cache = cache,
                    robots_cache = cache.robots_cache )
            ttl = cache.determine_ttl( result )
            await cache.store( url_s, result, headers, ttl )
            return result.extract( )
        case _:
            raise _exceptions.DocumentationInaccessibility(
                url_s, f"Unsupported scheme: {url.scheme}" )


async def retrieve_url_as_text(
    cache: ContentCache,
    url: _Url, *,
    duration_max: float = 30.0,
    charset_default: str = 'utf-8',
    client_factory: HttpClientFactory = _httpx.AsyncClient,
) -> str:
    ''' Cached GET request to fetch URL content as text. '''
    url_s = url.geturl( )
    match url.scheme:
        case '' | 'file':
            location = __.Path( url.path )
            try: content_bytes = location.read_bytes( )
            except Exception as exc:
                raise _exceptions.DocumentationInaccessibility(
                    url_s, exc ) from exc
            mimetype, charset = __.detext.detect_mimetype_and_charset(
                content_bytes, location )
            if not __.detext.is_textual_content( content_bytes ):
                raise _exceptions.DocumentationInaccessibility(
                    url_s, "Content analysis indicates non-textual data" )
            encoding = charset or charset_default
            return content_bytes.decode( encoding )
        case 'http' | 'https':
            result = await cache.access( url_s )
            if not __.is_absent( result ):
                content_bytes, headers = result
                _validate_textual_content(
                    content_bytes, headers, url_s )
                charset = _detect_charset_with_fallback(
                    content_bytes, headers, charset_default )
                return content_bytes.decode( charset )
            async with client_factory( ) as client:
                result, headers = await _retrieve_url(
                    url, duration_max = duration_max,
                    client = client,
                    content_cache = cache,
                    robots_cache = cache.robots_cache )
            ttl = cache.determine_ttl( result )
            await cache.store( url_s, result, headers, ttl )
            content_bytes = result.extract( )
            _validate_textual_content(
                content_bytes, headers, url_s )
            charset = _detect_charset_with_fallback(
                content_bytes, headers, charset_default )
            return content_bytes.decode( charset )
        case _:
            raise _exceptions.DocumentationInaccessibility(
                url_s, f"Unsupported scheme: {url.scheme}" )


async def _apply_request_delay(
    url: _Url,
    client: _httpx.AsyncClient,
    cache: RobotsCache,
) -> None:
    ''' Applies crawl delay to request if specified in robots.txt. '''
    if url.scheme not in ( 'http', 'https' ): return
    domain = _extract_domain( url )
    delay = cache.calculate_delay_remainder( domain )
    if delay > 0: await cache.delay_function( delay )
    parser = await cache.access( domain )
    if __.is_absent( parser ):
        parser = await _retrieve_robots_txt( client, cache, domain )
    if not __.is_absent( parser ):
        try: delay = parser.crawl_delay( cache.user_agent )
        except Exception as exc:
            _scribe.debug( f"Failed to get crawl delay for {domain}: {exc}" )
        else:
            if delay: cache.assign_delay( domain, float( delay ) )


async def _cache_robots_txt_error(
    domain: str, cache: RobotsCache, error: Exception
) -> __.Absential[ _RobotFileParser ]:
    _scribe.debug( f"Failed to fetch/parse robots.txt from {domain}: {error}" )
    result: RobotsResponse = _generics.Error( error )
    return await _cache_robots_txt_result( cache, domain, result )


async def _cache_robots_txt_result(
    cache: RobotsCache, domain: str, result: RobotsResponse
) -> __.Absential[ _RobotFileParser ]:
    ttl = cache.determine_ttl( result )
    await cache.store( domain, result, ttl )
    return result.extract( ) if result.is_value( ) else __.absent


async def _check_robots_txt(
    url: _Url, *,
    client: _httpx.AsyncClient,
    cache: RobotsCache,
) -> bool:
    ''' Checks if URL is allowed by robots.txt. '''
    if url.scheme not in ( 'http', 'https' ): return True
    url_s = url.geturl( )
    domain = _extract_domain( url )
    parser = await cache.access( domain )
    if __.is_absent( parser ):
        parser = await _retrieve_robots_txt( client, cache, domain )
        if __.is_absent( parser ): return True
    try: return parser.can_fetch( cache.user_agent, url_s )
    except Exception as exc:
        _scribe.debug( f"robots.txt check failed for {url_s}: {exc}" )
        return True # if no robots.txt, then assume URL allowed


def _detect_charset_with_fallback(
    content: bytes, headers: _httpx.Headers, default: str
) -> str:
    ''' Detects charset from headers with content-based fallback. '''
    header_charset = _extract_charset_from_headers( headers, '' )
    if header_charset:
        return header_charset
    detected_charset = __.detext.detect_charset( content )
    return detected_charset or default


def _detect_mimetype_with_fallback(
    content: bytes, headers: _httpx.Headers, url: str
) -> str:
    ''' Detects MIME type from headers with content-based fallback. '''
    header_mimetype = _extract_mimetype_from_headers( headers )
    if header_mimetype:
        return header_mimetype
    return __.detext.detect_mimetype( content, url ) or ''


def _extract_charset_from_headers(
    headers: _httpx.Headers, default: str
) -> str:
    ''' Extracts charset from Content-Type header. '''
    content_type = headers.get( 'content-type', '' )
    if isinstance( content_type, str ) and ';' in content_type:
        _, _, params = content_type.partition( ';' )
        if 'charset=' in params:
            charset = params.split( 'charset=' )[ -1 ].strip( )
            return charset.strip( '"\\\'\"' )
    return default


def _extract_domain( url: _Url ) -> str:
    ''' Extracts domain from URL for robots.txt caching. '''
    return f"{url.scheme}://{url.netloc}"


def _extract_mimetype_from_headers( headers: _httpx.Headers ) -> str:
    ''' Extracts mimetype from Content-Type header. '''
    content_type = headers.get( 'content-type', '' )
    if isinstance( content_type, str ) and ';' in content_type:
        mimetype, _, _ = content_type.partition( ';' )
        return mimetype.strip( )
    return content_type


async def _probe_url(
    url: _Url, /, *,
    duration_max: float,
    client: _httpx.AsyncClient,
    probe_cache: ProbeCache,
    robots_cache: RobotsCache,
) -> ProbeResponse:
    ''' Makes HEAD request with deduplication. '''
    url_s = url.geturl( )
    if not await _check_robots_txt(
        url, client = client, cache = robots_cache
    ):
        _scribe.debug( f"URL blocked by robots.txt: {url_s}" )
        return _generics.Error( _exceptions.UrlImpermissibility(
            url_s, robots_cache.user_agent ) )
    await _apply_request_delay( url, cache = robots_cache, client = client )
    async with probe_cache.acquire_mutex_for( url_s ):
        try:
            response = await client.head(
                url_s, timeout = duration_max, follow_redirects = True )
        except Exception as exc:
            _scribe.debug( f"HEAD request failed for {url_s}: {exc}" )
            return _generics.Error( exc )
        else:
            return _generics.Value(
                response.status_code < _http_success_threshold )


async def _retrieve_robots_txt(
    client: _httpx.AsyncClient, cache: RobotsCache, domain: str
) -> __.Absential[ _RobotFileParser ]:
    ''' Fetches and parses robots.txt for domain. '''
    robots_url = f"{domain}/robots.txt"
    async with cache.acquire_mutex_for( domain ):
        timeout = cache.request_timeout
        try:
            response = await client.get(
                robots_url, timeout = timeout, follow_redirects = True )
        except Exception as exc:
            return await _cache_robots_txt_error( domain, cache, exc )
        match response.status_code:
            case _HttpStatus.OK: lines = response.text.splitlines( )
            case _HttpStatus.NOT_FOUND: lines = [ ]
            case _:
                try: response.raise_for_status( )
                except Exception as exc:
                    return await _cache_robots_txt_error( domain, cache, exc )
        robots_parser = _RobotFileParser( )
        robots_parser.set_url( robots_url )
        try: robots_parser.parse( lines )
        except Exception as exc:
            return await _cache_robots_txt_error( domain, cache, exc )
        result: RobotsResponse = _generics.Value( robots_parser )
        return await _cache_robots_txt_result( cache, domain, result )


async def _retrieve_url(
    url: _Url, /, *,
    duration_max: float,
    client: _httpx.AsyncClient,
    content_cache: ContentCache,
    robots_cache: RobotsCache,
) -> tuple[ ContentResponse, _httpx.Headers ]:
    ''' Makes GET request with deduplication. '''
    url_s = url.geturl( )
    if not await _check_robots_txt(
        url, cache = robots_cache, client = client
    ):
        return (
            _generics.Error( _exceptions.UrlImpermissibility(
                url_s, robots_cache.user_agent ) ),
            _httpx.Headers( ) )
    await _apply_request_delay( url, cache = robots_cache, client = client )
    async with content_cache.acquire_mutex_for( url_s ):
        try:
            response = await client.get(
                url_s, timeout = duration_max, follow_redirects = True )
            response.raise_for_status( )
        except Exception as exc:
            _scribe.debug( f"GET request failed for {url_s}: {exc}" )
            return _generics.Error( exc ), _httpx.Headers( )
        else: return _generics.Value( response.content ), response.headers


def _validate_textual_content(
    content: bytes, headers: _httpx.Headers, url: str
) -> None:
    ''' Validates that content is textual via headers and content analysis. '''
    mimetype = _detect_mimetype_with_fallback( content, headers, url )
    if mimetype and not __.detext.is_textual_mimetype( mimetype ):
        raise _exceptions.HttpContentTypeInvalidity(
            url, mimetype, "text decoding" )
    if not __.detext.is_textual_content( content ):
        raise _exceptions.HttpContentTypeInvalidity(
            url, mimetype or 'unknown', "content analysis" )
