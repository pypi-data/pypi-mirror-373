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


''' Command-line interface. '''


from . import __
from . import cacheproxy as _cacheproxy
from . import exceptions as _exceptions
from . import functions as _functions
from . import interfaces as _interfaces
from . import results as _results
from . import server as _server
from . import state as _state


_scribe = __.acquire_scribe( __name__ )


def intercept_errors( ) -> __.cabc.Callable[ 
    [ __.cabc.Callable[ ..., __.cabc.Awaitable[ None ] ] ], 
    __.cabc.Callable[ ..., __.cabc.Awaitable[ None ] ] 
]:
    ''' Decorator for CLI handlers to intercept exceptions.
    
        Catches Omnierror exceptions and renders them appropriately.
        Other exceptions are logged and formatted simply.
    '''
    def decorator( 
        func: __.cabc.Callable[ ..., __.cabc.Awaitable[ None ] ]
    ) -> __.cabc.Callable[ ..., __.cabc.Awaitable[ None ] ]:
        @__.funct.wraps( func )
        async def wrapper( 
            self: __.typx.Any,
            auxdata: _state.Globals,
            display: __.DisplayTarget,
            display_format: _interfaces.DisplayFormat,
            *posargs: __.typx.Any,
            **nomargs: __.typx.Any,
        ) -> None:
            stream = await display.provide_stream( )
            try:
                return await func( 
                    self, auxdata, display, display_format, 
                    *posargs, **nomargs )
            except _exceptions.Omnierror as exc:
                match display_format:
                    case _interfaces.DisplayFormat.JSON:
                        serialized = dict( exc.render_as_json( ) )
                        error_message = __.json.dumps( serialized, indent = 2 )
                    case _interfaces.DisplayFormat.Markdown:
                        lines = exc.render_as_markdown( )
                        error_message = '\n'.join( lines )
                print( error_message, file = stream )
                raise SystemExit( 1 ) from None
            except Exception as exc:
                _scribe.error( f"{func.__name__} failed: %s", exc )
                match display_format:
                    case _interfaces.DisplayFormat.JSON:
                        error_data = {
                            "type": "unexpected_error",
                            "title": "Unexpected Error",
                            "message": str( exc ),
                            "suggestion": (
                                "Please report this issue if it persists." ),
                        }
                        error_message = __.json.dumps( error_data, indent = 2 )
                    case _interfaces.DisplayFormat.Markdown:
                        error_message = f"❌ Unexpected error: {exc}"
                print( error_message, file = stream )
                raise SystemExit( 1 ) from None

        return wrapper
    return decorator


GroupByArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ str ],
    __.tyro.conf.arg( help = __.access_doctab( 'group by argument' ) ),
]
PortArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ int ],
    __.tyro.conf.arg( help = __.access_doctab( 'server port argument' ) ),
]
TermArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.tyro.conf.Positional[ str ],
    __.tyro.conf.arg( help = __.access_doctab( 'term argument' ) ),
]
ResultsMax: __.typx.TypeAlias = __.typx.Annotated[
    int,
    __.tyro.conf.arg( help = __.access_doctab( 'results max argument' ) ),
]
LocationArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.tyro.conf.Positional[ str ],
    __.tyro.conf.arg( help = __.access_doctab( 'location argument' ) ),
]
TransportArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ str ],
    __.tyro.conf.arg( help = __.access_doctab( 'transport argument' ) ),
]


_search_behaviors_default = _interfaces.SearchBehaviors( )
_filters_default = __.immut.Dictionary[ str, __.typx.Any ]( )

_MARKDOWN_OBJECT_LIMIT = 10
_MARKDOWN_CONTENT_LIMIT = 200



class _CliCommand(
    __.immut.DataclassProtocol, __.typx.Protocol,
    decorators = ( __.typx.runtime_checkable, ),
):
    ''' CLI command. '''

    @__.abc.abstractmethod
    def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> __.cabc.Awaitable[ None ]:
        ''' Executes command with global state. '''
        raise NotImplementedError


class DetectCommand(
    _CliCommand, decorators = ( __.standard_tyro_class, ),
):
    ''' Detect which processors can handle a documentation source. '''

    location: LocationArgument
    genus: __.typx.Annotated[
        _interfaces.ProcessorGenera,
        __.tyro.conf.arg( help = "Processor genus (inventory or structure)." ),
    ]
    processor_name: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.tyro.conf.arg( help = "Specific processor to use." ),
    ] = None

    @intercept_errors( )
    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        stream = await display.provide_stream( )
        processor_name = (
            self.processor_name if self.processor_name is not None
            else __.absent )
        result = await _functions.detect(
            auxdata, self.location, self.genus,
            processor_name = processor_name )
        match display_format:
            case _interfaces.DisplayFormat.JSON:
                serialized = dict( result.render_as_json( ) )
                output = __.json.dumps( serialized, indent = 2 )
            case _interfaces.DisplayFormat.Markdown:
                lines = result.render_as_markdown( reveal_internals = True )
                output = '\n'.join( lines )
        print( output, file = stream )


class QueryInventoryCommand(
    _CliCommand, decorators = ( __.standard_tyro_class, ),
):
    ''' Searches object inventory by name with fuzzy matching. '''

    location: LocationArgument
    term: TermArgument
    details: __.typx.Annotated[
        _interfaces.InventoryQueryDetails,
        __.tyro.conf.arg(
            help = __.access_doctab( 'query details argument' ) ),
    ] = _interfaces.InventoryQueryDetails.Name
    filters: __.typx.Annotated[
        __.cabc.Mapping[ str, __.typx.Any ],
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = lambda: dict( _filters_default ) )
    search_behaviors: __.typx.Annotated[
        _interfaces.SearchBehaviors,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field(
        default_factory = lambda: _interfaces.SearchBehaviors( ) )
    results_max: __.typx.Annotated[
        int,
        __.tyro.conf.arg( help = __.access_doctab( 'results max argument' ) ),
    ] = 5

    @intercept_errors( )
    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        stream = await display.provide_stream( )
        result = await _functions.query_inventory(
            auxdata,
            self.location,
            self.term,
            search_behaviors = self.search_behaviors,
            filters = self.filters,
            results_max = self.results_max,
            details = self.details )
        match display_format:
            case _interfaces.DisplayFormat.JSON:
                output = __.json.dumps(
                    dict( result.render_as_json( ) ), indent = 2 )
            case _interfaces.DisplayFormat.Markdown:
                lines = result.render_as_markdown( reveal_internals = True )
                output = '\n'.join( lines )
        print( output, file = stream )


class QueryContentCommand(
    _CliCommand, decorators = ( __.standard_tyro_class, ),
):
    ''' Searches documentation content with relevance ranking and snippets. '''

    location: LocationArgument
    term: TermArgument
    search_behaviors: __.typx.Annotated[
        _interfaces.SearchBehaviors,
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field(
        default_factory = lambda: _interfaces.SearchBehaviors( ) )
    filters: __.typx.Annotated[
        __.cabc.Mapping[ str, __.typx.Any ],
        __.tyro.conf.arg( prefix_name = False ),
    ] = __.dcls.field( default_factory = lambda: dict( _filters_default ) )
    results_max: ResultsMax = 10
    lines_max: __.typx.Annotated[
        int,
        __.tyro.conf.arg(
            help = "Maximum number of lines to display per result." ),
    ] = 40

    @intercept_errors( )
    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        stream = await display.provide_stream( )
        result = await _functions.query_content(
            auxdata, self.location, self.term,
            search_behaviors = self.search_behaviors,
            filters = self.filters,
            results_max = self.results_max,
            lines_max = self.lines_max )
        match display_format:
            case _interfaces.DisplayFormat.JSON:
                output = __.json.dumps(
                    dict( result.render_as_json( ) ), indent = 2 )
            case _interfaces.DisplayFormat.Markdown:
                if isinstance( result, _results.ContentQueryResult ):
                    lines = result.render_as_markdown(
                        reveal_internals = True, lines_max = self.lines_max )
                else:
                    lines = result.render_as_markdown(
                        reveal_internals = True )
                output = '\n'.join( lines )
        print( output, file = stream )




class SurveyProcessorsCommand(
    _CliCommand, decorators = ( __.standard_tyro_class, ),
):
    ''' List processors for specified genus and their capabilities. '''

    genus: __.typx.Annotated[
        _interfaces.ProcessorGenera,
        __.tyro.conf.arg( help = "Processor genus (inventory or structure)." ),
    ]
    name: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.tyro.conf.arg( help = "Name of processor to describe" ),
    ] = None

    @intercept_errors( )
    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        stream = await display.provide_stream( )
        nomargs: __.NominativeArguments = { 'genus': self.genus }
        if self.name is not None: nomargs[ 'name' ] = self.name
        result = await _functions.survey_processors( auxdata, **nomargs )
        match display_format:
            case _interfaces.DisplayFormat.JSON:
                output = __.json.dumps( 
                    dict( result.render_as_json( ) ), indent = 2 )
            case _interfaces.DisplayFormat.Markdown:
                lines = result.render_as_markdown( reveal_internals = False )
                output = '\n'.join( lines )
        print( output, file = stream )



class ServeCommand(
    _CliCommand, decorators = ( __.standard_tyro_class, ),
):
    ''' Starts MCP server. '''

    port: PortArgument = None
    transport: TransportArgument = None
    extra_functions: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Enable extra functions (detect and survey-processors)." ),
    ] = False
    serve_function: __.typx.Callable[
        [ _state.Globals ], __.cabc.Awaitable[ None ]
    ] = _server.serve
    async def __call__(
        self,
        auxdata: _state.Globals,
        display: __.DisplayTarget,
        display_format: _interfaces.DisplayFormat,
    ) -> None:
        nomargs: __.NominativeArguments = { }
        if self.port is not None: nomargs[ 'port' ] = self.port
        if self.transport is not None: nomargs[ 'transport' ] = self.transport
        nomargs[ 'extra_functions' ] = self.extra_functions
        await self.serve_function( auxdata, **nomargs )


class Cli( __.immut.DataclassObject, decorators = ( __.simple_tyro_class, ) ):
    ''' MCP server CLI. '''

    display: __.DisplayTarget
    display_format: __.typx.Annotated[
        _interfaces.DisplayFormat,
        __.tyro.conf.arg( help = "Output format for command results." ),
    ] = _interfaces.DisplayFormat.Markdown
    command: __.typx.Union[
        __.typx.Annotated[
            DetectCommand,
            __.tyro.conf.subcommand( 'detect', prefix_name = False ),
        ],
        __.typx.Annotated[
            QueryInventoryCommand,
            __.tyro.conf.subcommand( 'query-inventory', prefix_name = False ),
        ],
        __.typx.Annotated[
            QueryContentCommand,
            __.tyro.conf.subcommand( 'query-content', prefix_name = False ),
        ],
        __.typx.Annotated[
            SurveyProcessorsCommand,
            __.tyro.conf.subcommand(
                'survey-processors', prefix_name = False ),
        ],
        __.typx.Annotated[
            ServeCommand,
            __.tyro.conf.subcommand( 'serve', prefix_name = False ),
        ],
    ]
    logfile: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.ddoc.Doc( ''' Path to log capture file. ''' ),
    ] = None

    async def __call__( self ):
        ''' Invokes command after library preparation. '''
        nomargs = self.prepare_invocation_args( )
        async with __.ctxl.AsyncExitStack( ) as exits:
            auxdata = await _prepare( exits = exits, **nomargs )
            from . import xtnsmgr
            await xtnsmgr.register_processors( auxdata )
            await self.command(
                auxdata = auxdata,
                display = self.display,
                display_format = self.display_format )

    def prepare_invocation_args(
        self,
    ) -> __.cabc.Mapping[ str, __.typx.Any ]:
        ''' Prepares arguments for initial configuration. '''
        args: dict[ str, __.typx.Any ] = dict(
            environment = True,
            logfile = self.logfile,
        )
        return args


def execute( ) -> None:
    ''' Entrypoint for CLI execution. '''
    config = (
        __.tyro.conf.HelptextFromCommentsOff,
    )
    with __.warnings.catch_warnings( ):
        __.warnings.filterwarnings(
            'ignore',
            message = r'Mutable type .* is used as a default value.*',
            category = UserWarning,
            module = 'tyro.constructors._struct_spec_dataclass' )
        try: __.asyncio.run( __.tyro.cli( Cli, config = config )( ) )
        except SystemExit: raise
        except BaseException as exc:
            __.report_exceptions( exc, _scribe )
            raise SystemExit( 1 ) from None












async def _prepare(
    environment: __.typx.Annotated[
        bool,
        __.ddoc.Doc( ''' Whether to configure environment. ''' )
    ],
    exits: __.typx.Annotated[
        __.ctxl.AsyncExitStack,
        __.ddoc.Doc( ''' Exit stack for resource management. ''' )
    ],
    logfile: __.typx.Annotated[
        __.typx.Optional[ str ],
        __.ddoc.Doc( ''' Path to log capture file. ''' )
    ],
) -> __.typx.Annotated[
    _state.Globals,
    __.ddoc.Doc( ''' Configured global state. ''' )
]:
    ''' Configures application based on arguments. '''
    nomargs: __.NominativeArguments = {
        'environment': environment,
        'exits': exits,
    }
    if logfile:
        logfile_p = __.Path( logfile ).resolve( )
        ( logfile_p.parent ).mkdir( parents = True, exist_ok = True )
        logstream = exits.enter_context( logfile_p.open( 'w' ) )
        inscription = __.appcore.inscription.Control(
            level = 'debug', target = logstream )
        nomargs[ 'inscription' ] = inscription
    auxdata = await __.appcore.prepare( **nomargs )
    content_cache, probe_cache, robots_cache = _cacheproxy.prepare( auxdata )
    return _state.Globals(
        application = auxdata.application,
        configuration = auxdata.configuration,
        directories = auxdata.directories,
        distribution = auxdata.distribution,
        exits = auxdata.exits,
        content_cache = content_cache,
        probe_cache = probe_cache,
        robots_cache = robots_cache )
