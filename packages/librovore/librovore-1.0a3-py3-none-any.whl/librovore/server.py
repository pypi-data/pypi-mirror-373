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


''' MCP server implementation. '''

from mcp.server.fastmcp import FastMCP as _FastMCP

# FastMCP uses Pydantic to generate JSON schemas from function signatures.
from pydantic import Field as _Field

from . import __
from . import exceptions as _exceptions
from . import functions as _functions
from . import interfaces as _interfaces
from . import state as _state


def intercept_errors( 
    func: __.cabc.Callable[ 
        ..., __.cabc.Awaitable[ dict[ str, __.typx.Any ] ] ]
) -> __.cabc.Callable[ ..., __.cabc.Awaitable[ dict[ str, __.typx.Any ] ] ]:
    ''' Decorator for MCP functions to intercept self-rendering exceptions.
    
        Catches Omnierror exceptions and returns their JSON representation
        instead of raising them. Other exceptions are re-raised unchanged.
    '''
    @__.funct.wraps( func )
    async def wrapper( 
        *posargs: __.typx.Any, **nomargs: __.typx.Any 
    ) -> dict[ str, __.typx.Any ]:
        try:
            return await func( *posargs, **nomargs )
        except _exceptions.Omnierror as exc:
            return dict( exc.render_as_json( ) )
        except Exception:
            raise

    return wrapper


@__.dcls.dataclass( kw_only = True, slots = True )
class SearchBehaviorsMutable:
    ''' Mutable version of SearchBehaviors for FastMCP/Pydantic compatibility.

        Note: Fields are manually duplicated from SearchBehaviors to avoid
        immutable dataclass internals leaking into JSON schema generation.
    '''

    match_mode: _interfaces.MatchMode = _interfaces.MatchMode.Fuzzy
    fuzzy_threshold: int = 50


FiltersMutable: __.typx.TypeAlias = dict[ str, __.typx.Any ]
GroupByArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ str ],
    _Field( description = __.access_doctab( 'group by argument' ) ),
]
TermArgument: __.typx.TypeAlias = __.typx.Annotated[
    str, _Field( description = __.access_doctab( 'term argument' ) ) ]
ResultsMax: __.typx.TypeAlias = __.typx.Annotated[
    int, _Field( description = __.access_doctab( 'results max argument' ) ) ]
LocationArgument: __.typx.TypeAlias = __.typx.Annotated[
    str, _Field( description = __.access_doctab( 'location argument' ) ) ]


_filters_default = FiltersMutable( )
_search_behaviors_default = SearchBehaviorsMutable( )

_scribe = __.acquire_scribe( __name__ )



async def serve(
    auxdata: _state.Globals, /, *,
    port: int = 0,
    transport: str = 'stdio',
    extra_functions: bool = False,
) -> None:
    ''' Runs MCP server. '''
    _scribe.debug( "Initializing FastMCP server." )
    mcp = _FastMCP( 'Sphinx MCP Server', port = port )
    _register_server_functions(
        auxdata, mcp, extra_functions = extra_functions )
    match transport:
        case 'sse': await mcp.run_sse_async( mount_path = None )
        case 'stdio': await mcp.run_stdio_async( )
        case _: raise ValueError


def _produce_detect_function( auxdata: _state.Globals ):
    @intercept_errors
    async def detect(
        location: LocationArgument,
        genus: __.typx.Annotated[
            _interfaces.ProcessorGenera,
            _Field( description = "Processor genus (inventory or structure)" ),
        ],
        processor_name: __.typx.Annotated[
            __.typx.Optional[ str ],
            _Field( description = "Optional processor name." ),
        ] = None,
    ) -> dict[ str, __.typx.Any ]:
        nomargs: __.NominativeArguments = { }
        if processor_name is not None:
            nomargs[ 'processor_name' ] = processor_name
        result = await _functions.detect( auxdata, location, genus, **nomargs )
        return dict( result.render_as_json( ) )

    return detect


def _produce_query_content_function( auxdata: _state.Globals ):
    @intercept_errors
    async def query_content(  # noqa: PLR0913
        location: LocationArgument,
        term: TermArgument,
        search_behaviors: __.typx.Annotated[
            SearchBehaviorsMutable,
            _Field( description = "Search behavior configuration" ),
        ] = _search_behaviors_default,
        filters: __.typx.Annotated[
            FiltersMutable,
            _Field( description = "Processor-specific filters" ),
        ] = _filters_default,
        results_max: ResultsMax = 10,
        lines_max: __.typx.Annotated[
            int,
            _Field( description = "Maximum lines to display per result." ),
        ] = 40,
    ) -> dict[ str, __.typx.Any ]:
        immutable_search_behaviors = (
            _to_immutable_search_behaviors( search_behaviors ) )
        immutable_filters = _to_immutable_filters( filters )
        result = await _functions.query_content(
            auxdata, location, term,
            search_behaviors = immutable_search_behaviors,
            filters = immutable_filters,
            results_max = results_max,
            lines_max = lines_max )
        return dict( result.render_as_json( lines_max = lines_max ) )

    return query_content


def _produce_query_inventory_function( auxdata: _state.Globals ):
    @intercept_errors
    async def query_inventory(  # noqa: PLR0913
        location: LocationArgument,
        term: TermArgument,
        search_behaviors: __.typx.Annotated[
            SearchBehaviorsMutable,
            _Field( description = "Search behavior configuration" ),
        ] = _search_behaviors_default,
        filters: __.typx.Annotated[
            FiltersMutable,
            _Field( description = "Processor-specific filters" ),
        ] = _filters_default,
        details: __.typx.Annotated[
            _interfaces.InventoryQueryDetails,
            _Field( description = "Detail level for inventory results" ),
        ] = _interfaces.InventoryQueryDetails.Name,
        results_max: ResultsMax = 5,
    ) -> dict[ str, __.typx.Any ]:
        immutable_search_behaviors = (
            _to_immutable_search_behaviors( search_behaviors ) )
        immutable_filters = _to_immutable_filters( filters )
        result = await _functions.query_inventory(
            auxdata, location, term,
            search_behaviors = immutable_search_behaviors,
            filters = immutable_filters,
            details = details,
            results_max = results_max )
        return dict( result.render_as_json( ) )

    return query_inventory




def _produce_survey_processors_function( auxdata: _state.Globals ):
    @intercept_errors
    async def survey_processors(
        genus: __.typx.Annotated[
            _interfaces.ProcessorGenera,
            _Field( description = "Processor genus (inventory or structure)" ),
        ],
        name: __.typx.Annotated[
            __.typx.Optional[ str ],
            _Field( description = "Optional processor name to filter." )
        ] = None,
    ) -> dict[ str, __.typx.Any ]:
        result = await _functions.survey_processors( auxdata, genus, name )
        return dict( result.render_as_json( ) )

    return survey_processors


def _register_server_functions(
    auxdata: _state.Globals, mcp: _FastMCP, /, *, extra_functions: bool = False
) -> None:
    ''' Registers MCP server tools with closures for auxdata access. '''
    _scribe.debug( "Registering tools." )
    mcp.tool( )( _produce_query_inventory_function( auxdata ) )
    mcp.tool( )( _produce_query_content_function( auxdata ) )
    if extra_functions:
        mcp.tool( )( _produce_detect_function( auxdata ) )
        mcp.tool( )( _produce_survey_processors_function( auxdata ) )
    _scribe.debug( "All tools registered successfully." )


def _to_immutable_filters(
    mutable_filters: FiltersMutable
) -> __.immut.Dictionary[ str, __.typx.Any ]:
    ''' Converts mutable filters dict to immutable dictionary. '''
    return __.immut.Dictionary[ str, __.typx.Any ]( mutable_filters )


def _to_immutable_search_behaviors(
    mutable_behaviors: SearchBehaviorsMutable
) -> _interfaces.SearchBehaviors:
    ''' Converts mutable search behaviors to immutable. '''
    field_values = {
        field.name: getattr( mutable_behaviors, field.name )
        for field in __.dcls.fields( mutable_behaviors )
        if not field.name.startswith( '_' ) }
    return _interfaces.SearchBehaviors( **field_values )
