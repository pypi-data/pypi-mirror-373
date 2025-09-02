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


''' MkDocs inventory processor for search_index.json format. '''

from . import __
from . import detection as _detection


class MkDocsInventoryProcessor( __.Processor ):
    ''' Processes MkDocs search index files (search_index.json format). '''

    name: str = 'mkdocs'

    @property
    def capabilities( self ) -> __.ProcessorCapabilities:
        ''' Returns MkDocs inventory processor capabilities. '''
        return __.ProcessorCapabilities(
            processor_name = 'mkdocs',
            version = '1.0.0',
            supported_filters = [
                __.FilterCapability(
                    name = 'location',
                    description = 'Filter by page location/URL pattern',
                    type = 'string'
                ),
                __.FilterCapability(
                    name = 'title',
                    description = 'Filter by page title pattern',
                    type = 'string'
                ),
            ],
            results_limit_max = 10000,
            response_time_typical = 'fast',
            notes = 'Processes MkDocs search index files (search_index.json)'
        )

    async def detect(
        self, auxdata: __.ApplicationGlobals, source: str
    ) -> __.InventoryDetection:
        ''' Detects if source has a MkDocs search index file. '''
        base_url = __.normalize_base_url( source )
        inventory_data, confidence = await _detection.probe_search_index(
            auxdata, base_url )
        return _detection.MkDocsInventoryDetection(
            processor = self,
            confidence = confidence,
            inventory_data = inventory_data )