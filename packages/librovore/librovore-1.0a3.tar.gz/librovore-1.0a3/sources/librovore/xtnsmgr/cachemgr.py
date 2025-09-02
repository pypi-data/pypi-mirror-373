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


''' Cache management for extension packages. '''


from . import __
from . import importation as _importation
from . import installation as _installation


_scribe = __.acquire_scribe( __name__ )


class CacheInfo( __.immut.DataclassObject ):
    ''' Information about cached extension package. '''

    specification: str
    location: __.Path
    ctime: __.datetime.datetime
    ttl: int # hours
    platform_id: str

    @property
    def is_expired( self ) -> bool:
        ''' Checks if cache entry has expired. '''
        return (
            __.datetime.datetime.now( ) - self.ctime
            > __.datetime.timedelta( hours = self.ttl ) )


def calculate_cache_path( specification: str ) -> __.Path:
    ''' Calculates cache path for package specification. '''
    base_dir = __.Path( '.auxiliary/caches/extensions' )
    hasher = __.hashlib.sha256( )
    hasher.update( specification.encode( 'utf-8' ) )
    digest = hasher.hexdigest( )
    platform_id = calculate_platform_id( )
    return base_dir / digest / platform_id


def calculate_platform_id( ) -> str:
    ''' Calculates platform identifier for package cache paths.

        Format: {python_impl}-{python_ver}--{os_name}--{cpu_arch}

        Examples:
            cpython-3.10--linux--x86_64
            pypy-3.10-7.3--darwin--arm64
    '''
    implementation = __.sys.implementation.name
    version = '.'.join( map( str, __.sys.version_info[ : 2 ] ) )
    suffix = ''
    match implementation:
        case 'pypy':
            suffix = '-' + '.'.join(
                map( str, __.sys.pypy_version_info[ : 2 ] ) ) # pyright: ignore
        case 'graalpy':
            # TODO: Add GraalVM version when available
            pass
        case _:
            pass
    os_name = __.platform.system( ).lower( )
    architecture = __.platform.machine( ).lower( )
    return (
        f"{implementation}-{version}{suffix}"
        f"--{os_name}--{architecture}" )


def acquire_cache_info( specification: str ) -> CacheInfo | None:
    ''' Acquires cache information for a package, if it exists. '''
    cache_path = calculate_cache_path( specification )
    metafile = cache_path / '.cache_metadata.json'
    if not metafile.exists( ): return None
    try:
        with metafile.open( 'r', encoding = 'utf-8' ) as f:
            metadata = __.json.load( f )
        return CacheInfo(
            specification = metadata[ 'package_spec' ],
            ctime = __.datetime.datetime.fromisoformat(
                metadata[ 'installed_at' ]
            ),
            ttl = metadata[ 'ttl_hours' ],
            platform_id = metadata[ 'platform_id' ],
            location = cache_path )
    except ( __.json.JSONDecodeError, KeyError, ValueError ) as exc:
        _scribe.warning(
            f"Invalid cache metadata for {specification}: {exc}" )
        return None


def save_cache_info( cache_info: CacheInfo ) -> None:
    ''' Saves cache information to metadata file. '''
    metafile = cache_info.location / '.cache_metadata.json'
    metafile.parent.mkdir( parents = True, exist_ok = True )
    metadata: __.cabc.Mapping[ str, str | int ] = __.immut.Dictionary( {
        'package_spec': cache_info.specification,
        'installed_at': cache_info.ctime.isoformat( ),
        'ttl_hours': cache_info.ttl,
        'platform_id': cache_info.platform_id
    } )
    with metafile.open( 'w', encoding = 'utf-8' ) as f:
        __.json.dump( dict( metadata ), f, indent = 2 )


def cleanup_expired_caches( ttl: int = 24 ) -> None:
    ''' Removes expired cache entries. '''
    base_dir = __.Path( '.auxiliary/caches/extensions' )
    if not base_dir.exists( ): return
    for package_dir in base_dir.iterdir( ):
        if not package_dir.is_dir( ): continue
        for platform_dir in package_dir.iterdir( ):
            if not platform_dir.is_dir( ): continue
            metafile = platform_dir / '.cache_metadata.json'
            if not metafile.exists( ): continue
            try:
                with metafile.open( 'r', encoding = 'utf-8' ) as f:
                    metadata = __.json.load( f )
                installed_at = __.datetime.datetime.fromisoformat(
                    metadata[ 'installed_at' ] )
                cache_ttl = metadata.get( 'ttl_hours', ttl )
                if ( __.datetime.datetime.now( ) - installed_at
                     > __.datetime.timedelta( hours = cache_ttl )
                ):
                    _scribe.info( f"Removing expired cache: {platform_dir}" )
                    __.shutil.rmtree( platform_dir )
            except (
                KeyError, ValueError,
                __.json.JSONDecodeError,
                OSError,
            ) as exc:
                _scribe.warning(
                    f"Error processing cache {platform_dir}: {exc}" )


def clear_package_cache( specification: str ) -> bool:
    ''' Clears cache for specific package. Returns True if found. '''
    cache_path = calculate_cache_path( specification )
    if cache_path.exists( ):
        try:
            __.shutil.rmtree( cache_path )
        except OSError as exc:
            _scribe.error(
                f"Failed to clear cache for {specification}: {exc}" )
            return False
        else:
            _scribe.info( f"Cleared cache for package: {specification}" )
            return True
    return False


async def ensure_package(
    specification: str, *,
    cache_ttl: int = 24,
    retries_max: int = 3
) -> __.typx.Annotated[
    None,
    __.ddoc.Raises( __.ExtensionConfigurationInvalidity, 'Invalid spec.' ),
    __.ddoc.Raises( __.ExtensionInstallFailure, 'Install fails.' ),
]:
    ''' Ensures package is installed and importable. '''
    cache_info = acquire_cache_info( specification )
    if cache_info and not cache_info.is_expired:
        _scribe.debug( f"Using cached package: {specification}." )
        package_path = cache_info.location
    else:
        if cache_info and cache_info.is_expired:
            _scribe.debug( f"Clearing expired cache for: {specification}." )
            clear_package_cache( specification )
        cache_path = calculate_cache_path( specification )
        package_path = await _installation.install_package(
            specification, cache_path, retries_max = retries_max )
        cache_info = CacheInfo(
            specification = specification,
            ctime = __.datetime.datetime.now( ),
            ttl = cache_ttl,
            platform_id = calculate_platform_id( ),
            location = package_path )
        save_cache_info( cache_info )
    _importation.add_package_to_import_path( package_path )


def invalidate(
    specification: str, *,
    clearer: __.Absential[
        __.cabc.Callable[ [ str ], bool ]
    ] = __.absent
) -> None:
    ''' Removes package from cache, forcing reinstall on next ensure. '''
    if __.is_absent( clearer ):
        clearer = clear_package_cache
    clearer( specification )
