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


''' MkDocs documentation structure processor main implementation. '''


from . import __
from . import detection as _detection


class MkDocsProcessor( __.Processor ):
    ''' Documentation processor for MkDocs sites with mkdocstrings. '''

    name: str = 'mkdocs'

    @property
    def capabilities( self ) -> __.ProcessorCapabilities:
        ''' Returns MkDocs structure processor capabilities. '''
        return __.ProcessorCapabilities(
            processor_name = self.name,
            version = '1.0.0',
            supported_filters = [ ],
            results_limit_max = 1000,
            response_time_typical = 'fast',
            notes = 'Processes MkDocs site structure and themes'
        )

    async def detect(
        self, auxdata: __.ApplicationGlobals, source: str
    ) -> _detection.MkDocsDetection:
        ''' Detects MkDocs documentation structure from source. '''
        base_url = __.normalize_base_url( source )
        normalized_source = base_url.geturl( )
        confidence = 0.0
        has_mkdocs_yml = (
            await _detection.check_mkdocs_yml( auxdata, base_url ) )
        if has_mkdocs_yml:
            confidence += 0.6
        theme_metadata = (
            await _detection.detect_theme( auxdata, base_url ) )
        theme = theme_metadata.get( 'theme' )
        if theme is not None:
            confidence += 0.3
        mkdocs_html_confidence = (
            await _detection.check_mkdocs_html_markers( auxdata, base_url ) )
        confidence += mkdocs_html_confidence
        confidence = min( confidence, 1.0 )
        
        return _detection.MkDocsDetection(
            processor = self,
            confidence = confidence,
            source = source,
            has_mkdocs_yml = has_mkdocs_yml,
            normalized_source = normalized_source,
            theme = theme )

