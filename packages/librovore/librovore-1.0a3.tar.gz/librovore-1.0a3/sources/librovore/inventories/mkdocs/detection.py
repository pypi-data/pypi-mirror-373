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


''' MkDocs inventory detection implementations. '''


import json as _json

from . import __


_SEARCH_INDEX_PATHS = (
    '/search/search_index.json',
    '/search_index.json',
    '/assets/search/search_index.json',
)

_MINIMUM_DOCUMENT_COUNT = 1
_SUBSTANTIAL_DOCS_THRESHOLD = 10
_MODERATE_DOCS_THRESHOLD = 5
_CONTENT_PREVIEW_LENGTH = 200


class MkDocsInventoryDetection( __.InventoryDetection ):
    ''' Detection result for MkDocs search index inventory sources. '''
    
    inventory_data: __.Absential[ dict[ str, __.typx.Any ] ] = __.absent

    @classmethod
    async def from_source(
        selfclass,
        auxdata: __.ApplicationGlobals,
        processor: __.Processor,
        source: str,
    ) -> __.typx.Self:
        ''' Constructs MkDocs inventory detection from source. '''
        base_url = __.normalize_base_url( source )
        inventory_data, confidence = await probe_search_index(
            auxdata, base_url )
        return selfclass(
            processor = processor,
            confidence = confidence,
            inventory_data = inventory_data )

    async def filter_inventory(
        self,
        auxdata: __.ApplicationGlobals,
        source: str, /, *,
        filters: __.cabc.Mapping[ str, __.typx.Any ],
        details: __.InventoryQueryDetails = (
            __.InventoryQueryDetails.Documentation ),
    ) -> tuple[ __.InventoryObject, ... ]:
        ''' Filters inventory objects from MkDocs search index. '''
        if __.is_absent( self.inventory_data ):
            base_url = __.normalize_base_url( source )
            inventory_data, _ = await probe_search_index( auxdata, base_url )
            if __.is_absent( inventory_data ): return tuple( )
        else: inventory_data = self.inventory_data
        objects = filter_inventory(
            inventory_data, source, filters = filters, details = details )
        return tuple( objects )


def calculate_confidence(
    docs: list[ __.typx.Any ], valid_docs: int
) -> float:
    ''' Calculates confidence score based on search index quality. '''
    if valid_docs == 0: return 0.0
    doc_ratio = valid_docs / len( docs ) if docs else 0.0
    base_confidence = 0.6
    if valid_docs >= _SUBSTANTIAL_DOCS_THRESHOLD: base_confidence = 0.8
    elif valid_docs >= _MODERATE_DOCS_THRESHOLD: base_confidence = 0.7
    return min( base_confidence * doc_ratio, 0.9 )


def filter_inventory(
    inventory_data: dict[ str, __.typx.Any ],
    location_url: str, /, *,
    filters: __.cabc.Mapping[ str, __.typx.Any ],
    details: __.InventoryQueryDetails = (
        __.InventoryQueryDetails.Documentation ),
) -> list[ __.InventoryObject ]:
    ''' Filters inventory objects from parsed search index data. '''
    docs = inventory_data.get( 'docs', [ ] )
    location_pattern = filters.get( 'location', '' ) or __.absent
    title_pattern = filters.get( 'title', '' ) or __.absent
    all_objects: list[ __.InventoryObject ] = [ ]
    for doc in docs:
        if not isinstance( doc, dict ): continue
        typed_doc = __.typx.cast( dict[ str, __.typx.Any ], doc )
        location = str( typed_doc.get( 'location', '' ) )
        title = str( typed_doc.get( 'title', '' ) )
        if not location or not title: continue
        if (
                not __.is_absent( location_pattern )
                and location_pattern not in location
        ): continue
        if (
                not __.is_absent( title_pattern )
                and title_pattern not in title
        ): continue
        obj = format_inventory_object( typed_doc, location_url )
        all_objects.append( obj )
    return all_objects


class MkDocsInventoryObject( __.InventoryObject ):
    ''' MkDocs-specific inventory object with page-aware formatting. '''
    
    def render_specifics_markdown(
        self, /, *,
        reveal_internals: bool = True,
    ) -> tuple[ str, ... ]:
        ''' Renders MkDocs specifics with page information. '''
        lines: list[ str ] = [ ]
        role = self.specifics.get( 'role' )
        if role:
            lines.append( f"- **Type:** {role}" )
        domain = self.specifics.get( 'domain' )
        if domain:
            lines.append( f"- **Domain:** {domain}" )
        return tuple( lines )
    
    def render_specifics_json(
        self
    ) -> __.immut.Dictionary[ str, __.typx.Any ]:
        ''' Renders MkDocs specifics with page format information. '''
        return __.immut.Dictionary(
            role = self.specifics.get( 'role' ),
            domain = self.specifics.get( 'domain' ),
            object_type = self.specifics.get( 'object_type' ),
            content_preview = self.specifics.get( 'content_preview' ),
        )


def format_inventory_object(
    doc: dict[ str, __.typx.Any ],
    location_url: str,
) -> MkDocsInventoryObject:
    ''' Formats MkDocs search index document with attribution. '''
    location = str( doc.get( 'location', '' ) )
    title = str( doc.get( 'title', '' ) )
    text = str( doc.get( 'text', '' ) )
    content_preview = (
        text[ :_CONTENT_PREVIEW_LENGTH ] + '...'
        if len( text ) > _CONTENT_PREVIEW_LENGTH else text )
    return MkDocsInventoryObject(
        name = title,
        uri = location,
        inventory_type = 'mkdocs_search_index',
        location_url = location_url,
        specifics = __.immut.Dictionary(
            domain = 'page',
            role = 'doc', 
            priority = '1',
            object_type = 'page',
            content_preview = content_preview ) )


async def probe_search_index(
    auxdata: __.ApplicationGlobals,
    base_url: __.typx.Any,
) -> tuple[ __.Absential[ dict[ str, __.typx.Any ] ], float ]:
    ''' Probes for MkDocs search index files and validates structure. '''
    for path in _SEARCH_INDEX_PATHS:
        search_url = base_url._replace( path = base_url.path + path )
        result = await _try_single_search_index( auxdata, search_url )
        if not __.is_absent( result ): return result
    return __.absent, 0.0


def _count_valid_docs( docs: list[ __.typx.Any ] ) -> int:
    ''' Counts valid document entries in search index. '''
    valid_docs = 0
    for doc in docs:
        if not isinstance( doc, dict ): continue
        if 'location' not in doc or 'title' not in doc: continue
        valid_docs += 1
    return valid_docs


def _is_valid_search_index( data: __.typx.Any ) -> bool:
    ''' Validates search index structure. '''
    if not isinstance( data, dict ):
        return False
    typed_data = __.typx.cast( dict[ str, __.typx.Any ], data )
    docs = typed_data.get( 'docs', [ ] )
    if not isinstance( docs, list ):
        return False
    typed_docs = __.typx.cast( list[ __.typx.Any ], docs )
    return len( typed_docs ) >= _MINIMUM_DOCUMENT_COUNT


async def _try_single_search_index(
    auxdata: __.ApplicationGlobals,
    search_url: __.typx.Any,
) -> __.Absential[ tuple[ dict[ str, __.typx.Any ], float ] ]:
    ''' Attempts to load and validate a single search index URL. '''
    search_index_raw = await __.retrieve_url_as_text(
        auxdata.content_cache, search_url )
    if __.is_absent( search_index_raw ):
        return __.absent
    try: inventory_data = _json.loads( search_index_raw )
    except ( _json.JSONDecodeError, UnicodeDecodeError, Exception ):
        return __.absent
    if not _is_valid_search_index( inventory_data ):
        return __.absent
    docs = inventory_data[ 'docs' ]
    valid_docs = _count_valid_docs( docs )
    if valid_docs < _MINIMUM_DOCUMENT_COUNT:
        return __.absent
    confidence = calculate_confidence( docs, valid_docs )
    return inventory_data, confidence