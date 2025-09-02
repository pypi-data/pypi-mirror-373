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


''' Extension configuration loading and validation. '''


from . import __


ExtensionArguments: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Mapping[ str, __.typx.Any ],
    __.ddoc.Doc( ''' Arguments to pass to extension/processor. ''' )
]
ExtensionConfig: __.typx.TypeAlias = __.typx.Annotated[
    __.cabc.Mapping[ str, __.typx.Any ],
    __.ddoc.Doc( ''' Configuration for a single extension/processor. ''' )
]


def validate_extension( config: ExtensionConfig ) -> None:
    ''' Validates single extension configuration. '''
    name = config.get( 'name' )
    if not name or not isinstance( name, str ):
        raise __.ExtensionConfigurationInvalidity(
            name or '<unnamed>',
            "Required field 'name' must be a non-empty string" )
    enabled = config.get( 'enabled', True )
    if not isinstance( enabled, bool ):
        raise __.ExtensionConfigurationInvalidity(
            name, "Field 'enabled' must be a boolean" )
    package = config.get( 'package' )
    if package is not None and not isinstance( package, str ):
        raise __.ExtensionConfigurationInvalidity(
            name, "Field 'package' must be a string" )
    arguments = config.get( 'arguments', { } )
    if not isinstance( arguments, dict ):
        raise __.ExtensionConfigurationInvalidity(
            name, "Field 'arguments' must be a dictionary" )


def extract_inventory_extensions(
    auxdata: __.Globals
) -> tuple[ ExtensionConfig, ... ]:
    ''' Loads and validates inventory extensions configuration. '''
    return _extract_extension_type( auxdata, 'inventory-extensions' )


def extract_structure_extensions(
    auxdata: __.Globals
) -> tuple[ ExtensionConfig, ... ]:
    ''' Loads and validates structure extensions configuration. '''
    return _extract_extension_type( auxdata, 'structure-extensions' )




def _extract_extension_type(
    auxdata: __.Globals,
    extension_type: str
) -> tuple[ ExtensionConfig, ... ]:
    ''' Loads and validates extensions of specific type. '''
    configuration = auxdata.configuration
    if not configuration: return ( )
    raw = configuration.get( extension_type, [ ] )
    if not isinstance( raw, list ):
        raise __.ExtensionConfigurationInvalidity(
            '<root>', f"Configuration '{extension_type}' must be a list" )
    raw = __.typx.cast( list[ __.typx.Any ], raw )
    extensions: list[ ExtensionConfig ] = [ ]
    for i, config in enumerate( raw ):
        if not isinstance( config, dict ):
            raise __.ExtensionConfigurationInvalidity(
                f'<{extension_type}[{i}]>',
                f"{extension_type.title()} configuration must be dict" )
        typed_config = __.typx.cast( ExtensionConfig, config )
        validate_extension( typed_config )
        extensions.append( typed_config )
    return tuple( extensions )


def select_active_extensions(
    extensions: __.cabc.Sequence[ ExtensionConfig ]
) -> tuple[ ExtensionConfig, ... ]:
    ''' Filters extensions to only enabled ones. '''
    return tuple( ext for ext in extensions if ext.get( 'enabled', True ) )


def select_intrinsic_extensions(
    extensions: __.cabc.Sequence[ ExtensionConfig ]
) -> tuple[ ExtensionConfig, ... ]:
    ''' Filters extensions to only built-in ones (no package field). '''
    return tuple( ext for ext in extensions if ext.get( 'package' ) is None )


def extract_extension_arguments(
    extension: ExtensionConfig
) -> ExtensionArguments:
    ''' Extracts arguments dictionary from extension configuration. '''
    return extension.get( 'arguments', { } )
