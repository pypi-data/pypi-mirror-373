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


''' Sphinx inventory processor for objects.inv format. '''

from . import __
from . import detection as _detection


class SphinxInventoryProcessor( __.Processor ):
    ''' Processes Sphinx inventory files (objects.inv format). '''

    name: str = 'sphinx'

    @property
    def capabilities( self ) -> __.ProcessorCapabilities:
        ''' Returns Sphinx inventory processor capabilities. '''
        return __.ProcessorCapabilities(
            processor_name = 'sphinx',
            version = '1.0.0',
            supported_filters = [
                __.FilterCapability(
                    name = 'domain',
                    description = 'Filter by object domain (e.g., py, js)',
                    type = 'string'
                ),
                __.FilterCapability(
                    name = 'role',
                    description = 'Filter by object role (e.g., class, func)',
                    type = 'string'
                ),
                __.FilterCapability(
                    name = 'priority',
                    description = 'Filter by object priority',
                    type = 'string'
                ),
            ],
            results_limit_max = 10000,
            response_time_typical = 'fast',
            notes = 'Processes Sphinx inventory files (objects.inv format)'
        )

    async def detect(
        self, auxdata: __.ApplicationGlobals, source: str
    ) -> __.InventoryDetection:
        ''' Detects if source has a Sphinx inventory file. '''
        base_url = __.normalize_base_url( source )
        has_objects_inv = await check_objects_inv( auxdata, base_url )
        if has_objects_inv:
            return _detection.SphinxInventoryDetection(
                processor = self, confidence = 1.0 )
        return _detection.SphinxInventoryDetection(
            processor = self, confidence = 0.0 )


async def check_objects_inv(
    auxdata: __.ApplicationGlobals, base_url: __.typx.Any
) -> bool:
    ''' Checks if objects.inv exists at the source for inventory detection. '''
    inventory_url = _detection.derive_inventory_url( base_url )
    try:
        return await __.probe_url(
            auxdata.probe_cache, inventory_url )
    except Exception: return False
