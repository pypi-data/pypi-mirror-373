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


''' Inventory detection implementations. '''


from urllib.parse import ParseResult as _Url

import sphobjinv as _sphobjinv

from . import __


class SphinxInventoryDetection( __.InventoryDetection ):
    ''' Detection result for Sphinx inventory sources. '''

    @classmethod
    async def from_source(
        selfclass,
        auxdata: __.ApplicationGlobals,
        processor: __.Processor,
        source: str,
    ) -> __.typx.Self:
        ''' Constructs Sphinx inventory detection from source. '''
        # TODO: Figure out why this is not used.
        # This is not used in current implementation
        return selfclass( processor = processor, confidence = 0.0 )

    async def filter_inventory(
        self,
        auxdata: __.ApplicationGlobals,
        source: str, /, *,
        filters: __.cabc.Mapping[ str, __.typx.Any ],
        details: __.InventoryQueryDetails = (
            __.InventoryQueryDetails.Documentation ),
    ) -> tuple[ __.InventoryObject, ... ]:
        ''' Filters inventory objects from Sphinx source. '''
        objects = await filter_inventory(
            source, filters = filters, details = details )
        return tuple( objects )


def derive_inventory_url( base_url: _Url ) -> _Url:
    ''' Derives objects.inv URL from base URL ParseResult. '''
    new_path = f"{base_url.path}/objects.inv"
    # TODO: Do not rely on named tuple internals.
    return base_url._replace( path = new_path )


def extract_inventory( base_url: _Url ) -> _sphobjinv.Inventory:
    ''' Extracts and parses Sphinx inventory from URL or file path. '''
    url = derive_inventory_url( base_url )
    url_s = url.geturl( )
    nomargs: __.NominativeArguments = { }
    match url.scheme:
        case 'http' | 'https': nomargs[ 'url' ] = url_s
        case 'file': nomargs[ 'fname_zlib' ] = url.path
        case _:
            raise __.InventoryUrlNoSupport(
                url, component = 'scheme', value = url.scheme )
    try: return _sphobjinv.Inventory( **nomargs )
    except ( ConnectionError, OSError, TimeoutError ) as exc:
        raise __.InventoryInaccessibility(
            url_s, cause = exc ) from exc
    except Exception as exc:
        raise __.InventoryInvalidity( url_s, cause = exc ) from exc


async def filter_inventory(
    source: str, /, *,
    filters: __.cabc.Mapping[ str, __.typx.Any ],
    details: __.InventoryQueryDetails = (
        __.InventoryQueryDetails.Documentation ),
) -> tuple[ __.InventoryObject, ... ]:
    ''' Extracts and filters inventory objects by structural criteria only. '''
    domain = filters.get( 'domain', '' ) or __.absent
    role = filters.get( 'role', '' ) or __.absent
    priority = filters.get( 'priority', '' ) or __.absent
    base_url = __.normalize_base_url( source )
    inventory = extract_inventory( base_url )
    all_objects: list[ __.InventoryObject ] = [ ]
    for objct in inventory.objects:
        if not __.is_absent( domain ) and objct.domain != domain: continue
        if not __.is_absent( role ) and objct.role != role: continue
        if not __.is_absent( priority ) and objct.priority != priority:
            continue
        obj = format_inventory_object( 
            objct, inventory, source )
        all_objects.append( obj )
    return tuple( all_objects )


class SphinxInventoryObject( __.InventoryObject ):
    ''' Sphinx-specific inventory object with domain-aware formatting. '''
    
    def render_specifics_markdown(
        self, /, *,
        reveal_internals: bool = True,
    ) -> tuple[ str, ... ]:
        ''' Renders Sphinx specifics with domain and role information. '''
        lines: list[ str ] = [ ]
        role = self.specifics.get( 'role' )
        if role:
            lines.append( f"- **Type:** {role}" )
        domain = self.specifics.get( 'domain' )
        if domain:
            lines.append( f"- **Domain:** {domain}" )
        if reveal_internals:
            priority = self.specifics.get( 'priority' )
            if priority is not None:
                lines.append( f"- **Priority:** {priority}" )
            project = self.specifics.get( 'inventory_project' )
            if project:
                lines.append( f"- **Project:** {project}" )
            version = self.specifics.get( 'inventory_version' )
            if version:
                lines.append( f"- **Version:** {version}" )
        return tuple( lines )
    
    def render_specifics_json(
        self
    ) -> __.immut.Dictionary[ str, __.typx.Any ]:
        ''' Renders Sphinx specifics with structured format information. '''
        return __.immut.Dictionary(
            role = self.specifics.get( 'role' ),
            domain = self.specifics.get( 'domain' ),
            priority = self.specifics.get( 'priority' ),
            inventory_project = self.specifics.get( 'inventory_project' ),
            inventory_version = self.specifics.get( 'inventory_version' ),
        )


def format_inventory_object(
    objct: __.typx.Any,
    inventory: __.typx.Any,
    location_url: str,
) -> SphinxInventoryObject:
    ''' Formats Sphinx inventory object with complete attribution. '''
    return SphinxInventoryObject(
        name = objct.name,
        uri = objct.uri,
        inventory_type = 'sphinx_objects_inv',
        location_url = location_url,
        display_name = (
            objct.dispname 
            if objct.dispname != '-' 
            else None ),
        specifics = __.immut.Dictionary(
            domain = objct.domain,
            role = objct.role,
            priority = objct.priority,
            inventory_project = inventory.project,
            inventory_version = inventory.version ) )
