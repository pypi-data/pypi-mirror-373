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


''' Import path management and .pth file processing for extension packages. '''


import importlib as _importlib

from . import __


_added_paths: __.cabc.MutableSequence[ str ] = [ ]
_scribe = __.acquire_scribe( __name__ )


def add_package_to_import_path(
    package_path: __.Path, *,
    path_adder: __.Absential[
        __.cabc.Callable[ [ __.Path ], None ]
    ] = __.absent,
    pth_processor: __.Absential[
        __.cabc.Callable[ [ __.Path ], None ]
    ] = __.absent
) -> None:
    ''' Add package to sys.path and process any .pth files. '''
    if __.is_absent( path_adder ):
        path_adder = _add_path_to_sys_path
    if __.is_absent( pth_processor ):
        pth_processor = process_pth_files
    path_adder( package_path )
    pth_processor( package_path )


def _add_path_to_sys_path( package_path: __.Path ) -> None:
    ''' Add single path to sys.path if not already present. '''
    path_str = str( package_path )
    if path_str not in __.sys.path:
        __.sys.path.insert( 0, path_str )
        _added_paths.append( path_str )
        _scribe.debug( f"Added to sys.path: {path_str}." )
    else:
        _scribe.debug( f"Path already in sys.path: {path_str}." )


def import_processor_module( module_name: str ) -> __.types.ModuleType:
    ''' Import a processor module by name.

        Uses standard Python import machinery. For builtin processors,
        pass f"{__.package_name}.structures.{name}". For external processors,
        pass the module name directly.
    '''
    try:
        _scribe.debug( f"Importing processor module: {module_name}." )
        module = _importlib.import_module( module_name )
    except ImportError as exc:
        _scribe.error( f"Failed to import {module_name}: {exc}." )
        raise
    else:
        _scribe.info( f"Successfully imported: {module_name}." )
        return module


def list_registered_processors( ) -> tuple[ str, ... ]:
    ''' List all currently registered processor names from both registries. '''
    all_processors: dict[ str, __.Processor ] = {
        **__.inventory_processors,
        **__.structure_processors
    }
    return tuple( all_processors.keys( ) )


def get_module_info( module_name: str ) -> dict[ str, __.typx.Any ]:
    ''' Get information about an imported module. '''
    if module_name not in __.sys.modules:
        return { 'imported': False }
    module = __.sys.modules[ module_name ]
    return {
        'imported': True,
        'name': module.__name__,
        'file': getattr( module, '__file__', None ),
        'package': getattr( module, '__package__', None ),
        'version': getattr( module, '__version__', None ),
        'doc': getattr( module, '__doc__', None ),
    }


def process_pth_files(
    package_path: __.Path, *,
    processor: __.Absential[
        __.cabc.Callable[ [ __.Path ], None ]
    ] = __.absent
) -> None:
    ''' Process .pth files in package directory to update sys.path.

        Handles proper encoding, hidden file detection, and security.
    '''
    if not package_path.is_dir( ): return
    try:
        pth_files = (
            file for file in package_path.iterdir( )
            if '.pth' == file.suffix
            and not file.name.startswith( '.' ) )
    except OSError: return
    if __.is_absent( processor ):
        processor = _process_pth_file
    for pth_file in sorted( pth_files ):
        processor( pth_file )


def _acquire_pth_file_content(
    pth_file: __.Path, *,
    encoding_provider: __.Absential[
        __.cabc.Callable[ [ ], str ]
    ] = __.absent
) -> str:
    ''' Read .pth file content with proper encoding handling. '''
    with __.io.open_code( str( pth_file ) ) as stream:
        content_bytes = stream.read( )
    # Accept BOM markers in .pth files - same as with source files
    try: return content_bytes.decode( 'utf-8-sig' )
    except UnicodeDecodeError:
        if __.is_absent( encoding_provider ):
            encoding_provider = __.locale.getpreferredencoding
        return content_bytes.decode( encoding_provider( ) )


def _is_hidden(
    path: __.Path, *, platform: __.Absential[ str ] = __.absent
) -> bool:
    ''' Check if path is hidden via system attributes. '''
    try: inode = path.lstat( )
    except OSError: return False
    if __.is_absent( platform ):
        platform = __.sys.platform
    match platform:
        case 'darwin':
            return bool( getattr( inode, 'st_flags', 0 ) & __.stat.UF_HIDDEN )
        case 'win32':
            # Windows FILE_ATTRIBUTE_HIDDEN constant (0x2)
            return bool(
                getattr( inode, 'st_file_attributes', 0 )
                & getattr( __.stat, 'FILE_ATTRIBUTE_HIDDEN', 0x2 ) )
        case _: return False


def _process_pth_file(
    pth_file: __.Path, *,
    hidden_checker: __.Absential[
        __.cabc.Callable[ [ __.Path ], bool ]
    ] = __.absent,
    content_reader: __.Absential[
        __.cabc.Callable[ [ __.Path ], str ]
    ] = __.absent,
    line_processor: __.Absential[
        __.cabc.Callable[ [ __.Path, str ], None ]
    ] = __.absent
) -> None:
    ''' Process single .pth file. '''
    if __.is_absent( hidden_checker ):
        hidden_checker = _is_hidden
    if __.is_absent( content_reader ):
        content_reader = _acquire_pth_file_content
    if __.is_absent( line_processor ):
        line_processor = _process_pth_file_lines
    if not pth_file.exists( ) or hidden_checker( pth_file ): return
    try: content = content_reader( pth_file )
    except OSError: return
    line_processor( pth_file, content )


def _process_pth_file_lines(
    pth_file: __.Path, content: str, *,
    executor: __.Absential[ __.cabc.Callable[ [ str ], None ] ] = __.absent,
    path_adder: __.Absential[
        __.cabc.Callable[ [ __.Path ], None ]
    ] = __.absent
) -> None:
    ''' Process lines in .pth file content. '''
    if __.is_absent( executor ):
        executor = exec
    if __.is_absent( path_adder ):
        path_adder = _add_path_to_sys_path
    for n, line in enumerate( content.splitlines( ), 1 ):
        if line.startswith( '#' ) or '' == line.strip( ): continue
        if line.startswith( ( 'import ', 'import\t' ) ):
            _scribe.debug( f"Executing import from {pth_file.name}: {line}" )
            try: executor( line )
            except Exception:
                _scribe.exception( f"Error on line {n} of {pth_file}." )
                break
            continue
        # Add directory path relative to .pth file location
        path_to_add = pth_file.parent / line.rstrip( )
        if path_to_add.exists( ):
            path_adder( path_to_add )
