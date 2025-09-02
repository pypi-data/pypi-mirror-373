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


''' Async package installation for extensions. '''


import uv as _uv

from . import __


_scribe = __.acquire_scribe( __name__ )


async def install_package(
    specification: str,
    cache_path: __.Path, *,
    retries_max: int = 3
) -> __.Path:
    ''' Installs package to specified path with retry logic.

        Returns path to installed package for sys.path manipulation.
    '''
    for attempt in range( retries_max + 1 ):
        try: return await _install_with_uv( specification, cache_path )
        except __.ExtensionInstallFailure as exc:  # noqa: PERF203
            if attempt == retries_max:
                _scribe.error(
                    f"Failed to install {specification} after "
                    f"{retries_max + 1} attempts: {exc}" )
                raise
            delay = 2 ** attempt
            _scribe.warning(
                f"Installation attempt {attempt + 1} failed for "
                f"{specification}, retrying in {delay}s: {exc}" )
            await __.asyncio.sleep( delay )
    raise __.ExtensionInstallFailure(
        specification, "Maximum retries exceeded" )


async def _install_with_uv(
    specification: str, cache_path: __.Path
) -> __.Path:
    ''' Installs package using uv to specified directory. '''
    cache_path.mkdir( parents = True, exist_ok = True )
    executable = _get_uv_executable( specification )
    command = _build_uv_command( executable, cache_path, specification )
    _scribe.info( f"Installing {specification} to {cache_path}." )
    stdout, stderr, returncode = await _execute_uv_command(
        command, specification )
    _validate_installation_result( specification, returncode, stderr )
    _scribe.info( f"Successfully installed {specification}." )
    return cache_path




def _get_uv_executable( specification: str ) -> str:
    ''' Gets uv executable path, raising appropriate error if not found. '''
    try: return str( _uv.find_uv_bin( ) )
    except ImportError as exc:
        raise __.ExtensionInstallFailure(
            specification, f"uv not available: {exc}" ) from exc


def _build_uv_command(
    executable: str, cache_path: __.Path, specification: str
) -> list[ str ]:
    ''' Builds uv command for package installation. '''
    return [
        executable, 'pip',
        'install', '--target', str( cache_path ),
        specification
    ]


async def _execute_uv_command(
    command: list[ str ], specification: str
) -> tuple[ bytes, bytes, int ]:
    ''' Executes uv command and returns stdout, stderr, and return code. '''
    try:
        process = await __.asyncio.create_subprocess_exec(
            *command,
            stdout = __.asyncio.subprocess.PIPE,
            stderr = __.asyncio.subprocess.PIPE )
    except OSError as exc:
        raise __.ExtensionInstallFailure(
            specification, f"Process execution failed: {exc}" ) from exc
    try:
        stdout, stderr = await process.communicate( )
    except __.asyncio.TimeoutError as exc:
        raise __.ExtensionInstallFailure(
            specification, f"Installation timed out: {exc}" ) from exc
    returncode = process.returncode
    if returncode is None:
        raise __.ExtensionInstallFailure(
            specification, "Process terminated without exit code" )
    return stdout, stderr, returncode


def _validate_installation_result(
    specification: str, returncode: int, stderr: bytes
) -> None:
    ''' Validates installation result and raises error if failed. '''
    if returncode != 0:
        raise __.ExtensionInstallFailure(
            specification,
            f"uv install failed (exit {returncode}): "
            f"{stderr.decode( 'utf-8' )}" )




