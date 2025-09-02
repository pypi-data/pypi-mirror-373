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


''' MkDocs detection and metadata extraction. '''


from urllib.parse import ParseResult as _Url

from . import __
from . import extraction as _extraction


_scribe = __.acquire_scribe( __name__ )


class MkDocsDetection( __.StructureDetection ):
    ''' Detection result for MkDocs documentation sources. '''

    source: str
    has_mkdocs_yml: bool = False
    normalized_source: str = ''
    theme: __.typx.Optional[ str ] = None

    @classmethod
    async def from_source(
        selfclass,
        auxdata: __.ApplicationGlobals,
        processor: __.Processor,
        source: str,
    ) -> __.typx.Self:
        ''' Constructs detection from source location. '''
        detection = await processor.detect( auxdata, source )
        return __.typx.cast( __.typx.Self, detection )

    async def extract_contents(
        self,
        auxdata: __.ApplicationGlobals,
        source: str,
        objects: __.cabc.Sequence[ __.InventoryObject ], /,
    ) -> tuple[ __.ContentDocument, ... ]:
        ''' Extracts documentation content for specified objects. '''
        theme_value = self.theme if self.theme is not None else __.absent
        documents = await _extraction.extract_contents(
            auxdata, source, objects, theme = theme_value )
        return tuple( documents )



async def check_mkdocs_yml(
    auxdata: __.ApplicationGlobals, source: _Url
) -> bool:
    ''' Checks if mkdocs.yml exists (indicates MkDocs site). '''
    url = source._replace( path = f"{source.path}/mkdocs.yml" )
    return await __.probe_url( auxdata.probe_cache, url )


async def check_mkdocs_html_markers(
    auxdata: __.ApplicationGlobals, source: _Url
) -> float:
    ''' Checks HTML content for MkDocs-specific markers. '''
    html_candidates = [
        source._replace( path = f"{source.path}/" ),
        source._replace( path = f"{source.path}/index.html" ),
    ]
    html_content = None
    for html_url in html_candidates:
        try:
            html_content = await __.retrieve_url_as_text(
                auxdata.content_cache,
                html_url, duration_max = 10.0 )
        except __.DocumentationInaccessibility: continue # noqa: PERF203
        else: break
    if not html_content: return 0.0
    confidence = 0.0
    html_content_lower = html_content.lower( )
    if 'mkdocs' in html_content_lower:
        confidence += 0.3
    if 'mkdocs-material' in html_content_lower:
        confidence += 0.2
    if '_mkdocstrings' in html_content_lower:
        confidence += 0.2
    if ( 'name="generator"' in html_content_lower
         and 'mkdocs' in html_content_lower
    ):
        confidence += 0.3
    return min( confidence, 0.5 )


async def detect_theme(
    auxdata: __.ApplicationGlobals, source: _Url
) -> dict[ str, __.typx.Any ]:
    ''' Detects MkDocs theme and other metadata. '''
    theme_metadata: dict[ str, __.typx.Any ] = { }
    html_candidates = [
        source._replace( path = f"{source.path}/" ),
        source._replace( path = f"{source.path}/index.html" ),
    ]
    html_content = None
    for html_url in html_candidates:
        # TODO: Use probe_url instead of `try`.
        try:
            html_content = await __.retrieve_url_as_text(
                auxdata.content_cache,
                html_url, duration_max = 10.0 )
        except __.DocumentationInaccessibility: continue # noqa: PERF203
        else: break
    if html_content:
        html_content_lower = html_content.lower( )
        if ( 'material' in html_content_lower
             or 'mkdocs-material' in html_content_lower
        ): theme_metadata[ 'theme' ] = 'material'
        elif 'readthedocs' in html_content_lower:
            theme_metadata[ 'theme' ] = 'readthedocs'
    return theme_metadata
