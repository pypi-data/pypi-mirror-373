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


''' Common enumerations and interfaces. '''


from . import __


class FilterCapability( __.immut.DataclassObject ):
    ''' Describes a filter supported by a processor. '''

    name: str
    description: str
    type: str  # "string", "enum", "boolean"
    values: __.typx.Optional[ list[ str ] ] = None  # For enums
    required: bool = False


class DisplayFormat( __.enum.Enum ):
    ''' Enumeration for CLI display formats. '''

    JSON = 'json'
    Markdown = 'markdown'


class ProcessorGenera( __.enum.Enum ):
    ''' Enumeration for processor types/genera. '''

    Inventory = 'inventory'
    Structure = 'structure'


class InventoryQueryDetails( __.enum.IntFlag ):
    ''' Enumeration for inventory query detail levels. '''

    Name =          0               # Object names only (baseline)
    Signature =     __.enum.auto( ) # Include signatures
    Summary =       __.enum.auto( ) # Include brief descriptions
    Documentation = __.enum.auto( ) # Include full documentation


class MatchMode( str, __.enum.Enum ):
    ''' Enumeration for different term matching modes. '''

    Exact = 'exact'
    Regex = 'regex'
    Fuzzy = 'fuzzy'


class SearchBehaviors( __.immut.DataclassObject ):
    ''' Search behavior configuration for the search engine. '''

    match_mode: MatchMode = MatchMode.Fuzzy
    fuzzy_threshold: int = 50


_search_behaviors_default = SearchBehaviors( )
_filters_default = __.immut.Dictionary[ str, __.typx.Any ]( )


class ProcessorCapabilities( __.immut.DataclassObject ):
    ''' Complete capability description for a processor. '''

    processor_name: str
    version: str
    supported_filters: list[ FilterCapability ]
    results_limit_max: __.typx.Optional[ int ] = None
    response_time_typical: __.typx.Optional[ str ] = None  # "fast", etc.
    notes: __.typx.Optional[ str ] = None
