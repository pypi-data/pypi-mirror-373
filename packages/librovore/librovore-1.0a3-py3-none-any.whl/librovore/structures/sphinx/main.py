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
#  WITHOUT WARRANTIES OR CONDITIONS of ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Main Sphinx processor implementation. '''


from . import __
from . import detection as _detection
from . import urls as _urls


_scribe = __.acquire_scribe( __name__ )
_search_behaviors_default = __.SearchBehaviors( )
_filters_default = __.immut.Dictionary[ str, __.typx.Any ]( )


class SphinxProcessor( __.Processor ):
    ''' Processor for Sphinx documentation sources. '''

    name: str = 'sphinx'

    @property
    def capabilities( self ) -> __.ProcessorCapabilities:
        ''' Returns Sphinx processor capabilities. '''
        return __.ProcessorCapabilities(
            processor_name = 'sphinx',
            version = '1.0.0',
            supported_filters = [
                __.FilterCapability(
                    name = 'domain',
                    description = 'Sphinx domain (py, std, js, etc.)',
                    type = 'string',
                    values = None,
                ),
                __.FilterCapability(
                    name = 'role',
                    description = 'Object role (class, function, method)',
                    type = 'string',
                    values = None,
                ),
                __.FilterCapability(
                    name = 'priority',
                    description = 'Documentation priority level',
                    type = 'string',
                    values = [ '0', '1', '-1' ],
                ),
            ],
            results_limit_max = 100,
            response_time_typical = 'fast',
            notes = 'Works with Sphinx-generated documentation sites',
        )

    async def detect(
        self, auxdata: __.ApplicationGlobals, source: str
    ) -> __.StructureDetection:
        ''' Detects if can process documentation from source. '''
        try: base_url = _urls.normalize_base_url( source )
        except Exception:
            return _detection.SphinxDetection(
                processor = self, confidence = 0.0, source = source )
        confidence = 0.0
        has_searchindex = (
            await _detection.check_searchindex( auxdata, base_url ) )
        if has_searchindex:
            confidence += 0.8
        theme = None
        try:
            theme_metadata = (
                await _detection.detect_theme( auxdata, base_url ) )
            theme = theme_metadata.get( 'theme' )
            if theme is not None:
                confidence += 0.2
        except Exception as exc:
            _scribe.debug( f"Theme detection failed for {source}: {exc}" )
        confidence = min( confidence, 1.0 )
        
        return _detection.SphinxDetection(
            processor = self,
            confidence = confidence,
            source = source,
            has_searchindex = has_searchindex,
            normalized_source = base_url.geturl( ),
            theme = theme )

