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


''' Centralized search engine for universal matching across processors. '''


import re as _re

import rapidfuzz as _rapidfuzz

from . import __
from . import interfaces as _interfaces
from . import results as _results


def filter_by_name(
    objects: __.cabc.Sequence[ _results.InventoryObject ],
    query: str, /, *,
    match_mode: _interfaces.MatchMode = _interfaces.MatchMode.Fuzzy,
    fuzzy_threshold: int = 50,
) -> tuple[ _results.SearchResult, ... ]:
    ''' Filter objects by name using specified match mode. '''
    if not query:
        # Empty query returns all objects with neutral score
        return tuple(
            _results.SearchResult.from_inventory_object(
                obj, score = 1.0, match_reasons = [ 'empty query' ] )
            for obj in objects
        )

    query_lower = query.lower( )
    results: list[ _results.SearchResult ] = [ ]

    if match_mode == _interfaces.MatchMode.Exact:
        results = _filter_exact( objects, query_lower )
    elif match_mode == _interfaces.MatchMode.Regex:
        results = _filter_regex( objects, query )
    elif match_mode == _interfaces.MatchMode.Fuzzy:
        results = _filter_fuzzy(
            objects, query_lower, fuzzy_threshold )

    sorted_results = sorted( results, key = lambda r: r.score, reverse = True )
    return tuple( sorted_results )


def _filter_exact(
    objects: __.cabc.Sequence[ _results.InventoryObject ],
    query_lower: str
) -> list[ _results.SearchResult ]:
    ''' Apply exact matching to objects. '''
    results: list[ _results.SearchResult ] = [ ]
    for obj in objects:
        obj_name_lower = obj.name.lower( )
        if query_lower in obj_name_lower:
            # Score based on how well the query matches
            if obj_name_lower == query_lower:
                score = 1.0
                reason = 'exact name match'
            elif obj_name_lower.startswith( query_lower ):
                score = 0.9
                reason = 'name starts with query'
            else:
                score = 0.7
                reason = 'name contains query'

            results.append( _results.SearchResult.from_inventory_object(
                obj, score = score, match_reasons = [ reason ] ) )
    return results


def _filter_regex(
    objects: __.cabc.Sequence[ _results.InventoryObject ],
    query: str
) -> list[ _results.SearchResult ]:
    ''' Apply regex matching to objects. '''
    try:
        pattern = _re.compile( query, _re.IGNORECASE )
    except _re.error:
        # Invalid regex, return no results
        return [ ]

    return [
        _results.SearchResult.from_inventory_object(
            obj, score = 1.0, match_reasons = [ 'regex match' ] )
        for obj in objects if pattern.search( obj.name )
    ]


def _filter_fuzzy(
    objects: __.cabc.Sequence[ _results.InventoryObject ],
    query_lower: str,
    fuzzy_threshold: int
) -> list[ _results.SearchResult ]:
    ''' Apply fuzzy matching to objects using rapidfuzz. '''
    results: list[ _results.SearchResult ] = [ ]

    for obj in objects:
        obj_name = obj.name
        obj_name_lower = obj_name.lower( )

        # Use rapidfuzz ratio for basic fuzzy matching
        ratio = _rapidfuzz.fuzz.ratio( query_lower, obj_name_lower )

        if ratio >= fuzzy_threshold:
            # Normalize score to 0.0-1.0 range
            score = ratio / 100.0
            results.append( _results.SearchResult.from_inventory_object(
                obj,
                score = score,
                match_reasons = [ f'fuzzy match ({ratio}%)' ]
            ) )

    return results
