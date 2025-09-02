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


''' Sphinx detection and metadata extraction. '''


from urllib.parse import ParseResult as _Url

from . import __
from . import extraction as _extraction
from . import urls as _urls


_scribe = __.acquire_scribe( __name__ )


class SphinxDetection( __.StructureDetection ):
    ''' Detection result for Sphinx documentation sources. '''

    source: str
    has_searchindex: bool = False
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
        theme = self.theme if self.theme is not None else __.absent
        documents = await _extraction.extract_contents(
            auxdata, source, objects, theme = theme )
        return tuple( documents )



async def check_searchindex(
    auxdata: __.ApplicationGlobals, source: _Url
) -> bool:
    ''' Checks if searchindex.js exists (indicates full Sphinx site). '''
    url = _urls.derive_searchindex_url( source )
    return await __.probe_url( auxdata.probe_cache, url )


async def detect_theme(
    auxdata: __.ApplicationGlobals, source: _Url
) -> dict[ str, __.typx.Any ]:
    ''' Detects Sphinx theme and other metadata. '''
    theme_metadata: dict[ str, __.typx.Any ] = { }
    html_url = _urls.derive_html_url( source )
    try:
        # TODO: Use probe_url instead of `try`.
        html_content = await __.retrieve_url_as_text(
            auxdata.content_cache,
            html_url, duration_max = 10.0 )
    except __.DocumentationInaccessibility: pass
    else:
        html_content_lower = html_content.lower( )
        if ( 'furo' in html_content_lower
             or 'css/furo.css' in html_content_lower
        ): theme_metadata[ 'theme' ] = 'furo'
        elif ( 'sphinx_rtd_theme' in html_content_lower
               or 'css/theme.css' in html_content_lower
        ): theme_metadata[ 'theme' ] = 'sphinx_rtd_theme'
        elif ( 'alabaster' in html_content_lower
               or 'css/alabaster.css' in html_content_lower
        ): theme_metadata[ 'theme' ] = 'alabaster'
        elif ( 'pydoctheme.css' in html_content_lower
               or 'classic.css' in html_content_lower
        ): theme_metadata[ 'theme' ] = 'pydoctheme'
        elif 'flask.css' in html_content_lower:
            theme_metadata[ 'theme' ] = 'flask'
        elif 'css/nature.css' in html_content_lower:
            theme_metadata[ 'theme' ] = 'nature'
        elif 'css/default.css' in html_content_lower:
            theme_metadata[ 'theme' ] = 'classic'
        elif 'sphinx_book_theme' in html_content_lower:
            theme_metadata[ 'theme' ] = 'sphinx_book_theme'
        elif 'pydata_sphinx_theme' in html_content_lower:
            theme_metadata[ 'theme' ] = 'pydata_sphinx_theme'
        # If no theme detected, don't set theme key (returns None)
    return theme_metadata
