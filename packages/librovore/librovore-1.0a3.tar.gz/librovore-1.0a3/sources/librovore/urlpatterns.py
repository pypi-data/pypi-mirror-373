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


''' URL pattern analysis and extension utilities for documentation. '''


from . import __
from . import cacheproxy as _cacheproxy
from . import state as _state

_Url = __.urlparse.ParseResult


_scribe = __.acquire_scribe( __name__ )


UrlPatternResult: __.typx.TypeAlias = __.immut.Dictionary[ str, __.typx.Any ]


class UrlPatternAnalysis( __.immut.DataclassObject ):
    ''' Analysis of documentation site URL patterns. '''

    base_url: _Url
    site_type: str
    candidate_patterns: tuple[ str, ... ]
    has_version_segment: bool

    @classmethod
    def from_url( cls, url: _Url ) -> __.typx.Self:
        ''' Analyzes URL to determine documentation site pattern. '''
        site_type = detect_documentation_site_type( url )
        candidate_patterns = produce_url_patterns( url, site_type )
        has_version_segment = detect_version_segment( url )
        return cls(
            base_url = url,
            site_type = site_type,
            candidate_patterns = candidate_patterns,
            has_version_segment = has_version_segment,
        )


def detect_documentation_site_type( url: _Url ) -> str:
    ''' Detects documentation hosting platform from URL. '''
    netloc = url.netloc.lower( )
    if 'readthedocs.io' in netloc or 'readthedocs.org' in netloc:
        return 'readthedocs'
    if 'github.io' in netloc:
        return 'github_pages'
    if 'gitlab.io' in netloc:
        return 'gitlab_pages'
    if 'netlify.app' in netloc or 'netlify.com' in netloc:
        return 'netlify'
    if 'vercel.app' in netloc:
        return 'vercel'
    return 'generic'


def detect_version_segment( url: _Url ) -> bool:
    ''' Detects if URL contains version-like path segments. '''
    path_segments = [ 
        segment for segment in url.path.split( '/' ) if segment 
    ]
    return any( _is_version_like( segment ) for segment in path_segments )


def normalize_url_for_patterns( url: _Url ) -> _Url:
    ''' Normalizes URL by removing trailing slashes and fragments. '''
    path = url.path.rstrip( '/' ) if url.path != '/' else ''
    return url._replace( path = path, fragment = '', query = '' )


def produce_url_patterns( url: _Url, site_type: str ) -> tuple[ str, ... ]:
    ''' Produces candidate URL patterns for documentation discovery. '''
    normalized_url = normalize_url_for_patterns( url )
    patterns: list[ str ] = [ ]
    match site_type:
        case 'readthedocs':
            patterns.extend( _produce_readthedocs_patterns( normalized_url ) )
        case 'github_pages':
            patterns.extend( _produce_github_pages_patterns( normalized_url ) )
        case 'gitlab_pages':
            patterns.extend( _produce_gitlab_pages_patterns( normalized_url ) )
        case _:
            patterns.extend( _produce_generic_patterns( normalized_url ) )
    seen: set[ str ] = set( )
    deduplicated: list[ str ] = [ ]
    for pattern in patterns:
        if pattern not in seen:
            seen.add( pattern )
            deduplicated.append( pattern )
    return tuple( deduplicated )


async def probe_url_patterns(
    auxdata: _state.Globals,
    base_url: _Url,
    inventory_path: str
) -> __.Absential[ _Url ]:
    ''' Probes URL patterns to find working inventory URL. '''
    analysis = UrlPatternAnalysis.from_url( base_url )
    tasks: list[ __.cabc.Awaitable[ bool ] ] = [
        _cacheproxy.probe_url(
            auxdata.probe_cache,
            __.urlparse.urlparse( __.urlparse.urlunparse( (
                candidate_url.scheme,
                candidate_url.netloc,
                candidate_url.path + inventory_path,
                candidate_url.params,
                candidate_url.query,
                candidate_url.fragment
            ) ) ) )
        for pattern in analysis.candidate_patterns
        for candidate_url in [ __.urlparse.urlparse( pattern ) ]
    ]
    results = await __.asyncf.gather_async(
        *tasks, return_exceptions = True )
    for i, result in enumerate( results ):
        if __.generics.is_value( result ) and result.value:
            pattern = analysis.candidate_patterns[ i ]
            return __.urlparse.urlparse( pattern )
    return __.absent


def _is_version_like( segment: str ) -> bool:
    ''' Checks if path segment looks like a version identifier. '''
    version_patterns = [
        'latest', 'stable', 'main', 'master', 'dev', 'development',
        'v1', 'v2', 'v3', 'v4', 'v5',
        'en', 'docs',
    ]
    segment_lower = segment.lower( )
    if segment_lower in version_patterns:
        return True
    return bool( _matches_version_pattern( segment ) )


def _matches_version_pattern( segment: str ) -> bool:
    ''' Checks if segment matches common version patterns. '''
    version_regex = __.re.compile(
        r'^v?\d+(\.\d+)*([a-z]\d*)?$', __.re.IGNORECASE )
    return bool( version_regex.match( segment ) )


def _produce_generic_patterns( url: _Url ) -> list[ str ]:
    ''' Produces generic documentation URL patterns. '''
    base_url = url.geturl( )
    patterns = [ base_url ]
    paths = [
        '/en/latest',
        '/latest',
        '/docs',
        '/documentation',
        '/en/stable',
        '/stable',
        '/main',
        '/master',
    ]
    for path in paths:
        pattern_url = url._replace( path = url.path.rstrip( '/' ) + path )
        patterns.append( pattern_url.geturl( ) )
    return patterns


def _produce_github_pages_patterns( url: _Url ) -> list[ str ]:
    ''' Produces GitHub Pages specific URL patterns. '''
    patterns = _produce_generic_patterns( url )
    if url.path and url.path != '/':
        root_url = url._replace( path = '' )
        patterns.insert( 1, root_url.geturl( ) )
    return patterns


def _produce_gitlab_pages_patterns( url: _Url ) -> list[ str ]:
    ''' Produces GitLab Pages specific URL patterns. '''
    return _produce_github_pages_patterns( url )


def _produce_readthedocs_patterns( url: _Url ) -> list[ str ]:
    ''' Produces ReadTheDocs specific URL patterns. '''
    base_url = url.geturl( )
    patterns = [ base_url ]
    readthedocs_paths = [
        '/en/latest',
        '/en/stable',
        '/latest',
        '/stable',
        '/main',
        '/master',
    ]
    for path in readthedocs_paths:
        pattern_url = url._replace( path = path )
        patterns.append( pattern_url.geturl( ) )
    return patterns