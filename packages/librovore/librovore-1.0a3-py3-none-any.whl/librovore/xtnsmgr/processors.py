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


''' Processor loading and registration management. '''


from . import __
from . import cachemgr as _cachemgr
from . import configuration as _configuration
from . import importation as _importation


_scribe = __.acquire_scribe( __name__ )


def _raise_registration_error( name: str ) -> None:
    ''' Raises registration error for missing function. '''
    raise __.ExtensionConfigurationInvalidity(
        name, "No registration function found" )


async def register_processors( auxdata: __.Globals ):
    ''' Registers inventory and structure processors from configuration. '''
    await _register_processor_type(
        auxdata, 'inventory', _configuration.extract_inventory_extensions )
    await _register_processor_type(
        auxdata, 'structure', _configuration.extract_structure_extensions )


async def _register_processor_type(
    auxdata: __.Globals,
    processor_type: str,
    extract_func: __.cabc.Callable[ [ __.Globals ], __.typx.Any ]
) -> None:
    ''' Registers processors of specific type based on configuration. '''
    try: extensions = extract_func( auxdata )
    except ( KeyError, ValueError, TypeError ) as exc:
        _scribe.error( f"{processor_type.title()} configuration loading "
                      f"failed: {exc}." )
        return
    active_extensions = _configuration.select_active_extensions( extensions )
    if not active_extensions: return
    intrinsic_extensions = (
        _configuration.select_intrinsic_extensions( active_extensions ) )
    external_extensions = tuple(
        ext for ext in active_extensions
        if ext.get( 'package' ) and ext not in intrinsic_extensions )
    await _ensure_external_packages( external_extensions )
    if not intrinsic_extensions and not external_extensions:
        _scribe.warning( f"No {processor_type} processors could be loaded." )
        return
    for extension in active_extensions:
        _register_extension( extension, processor_type )


async def _ensure_external_packages(
    extensions: __.cabc.Sequence[ _configuration.ExtensionConfig ]
) -> None:
    ''' Ensures external packages are installed and importable in parallel. '''
    if not extensions: return
    specifications = [ ext[ 'package' ] for ext in extensions ]
    count = len( specifications )
    _scribe.info( f"Ensuring {count} external packages available." )
    tasks = [ _cachemgr.ensure_package( spec ) for spec in specifications ]
    await __.asyncf.gather_async(
        *tasks, error_message = "Failed to install external packages." )


def _register_extension(
    extension: _configuration.ExtensionConfig,
    processor_type: str
) -> None:
    ''' Registers extension from configuration to appropriate registry. '''
    name = extension[ 'name' ]
    arguments = _configuration.extract_extension_arguments( extension )
    if 'package' not in extension:
        if processor_type == 'inventory':
            module_name = f"{__.package_name}.inventories.{name}"
        else:
            module_name = f"{__.package_name}.structures.{name}"
    else: module_name = name
    try: module = _importation.import_processor_module( module_name )
    except ( ImportError, ModuleNotFoundError ) as exc:
        _scribe.error( f"Failed to import {processor_type} processor "
                      f"{name}: {exc}" )
        return
    try:
        if hasattr( module, 'register' ):
            module.register( arguments )
        else:
            _raise_registration_error( name )
    except Exception as exc:
        _scribe.error( f"Failed to register {processor_type} processor "
                      f"{name}: {exc}" )
        return
    _scribe.info( f"Registered {processor_type} extension: {name}." )
