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


''' HTML to markdown conversion utilities. '''


import markdownify as _markdownify

from bs4 import BeautifulSoup as _BeautifulSoup


def html_to_markdown( html_text: str ) -> str:
    ''' Converts HTML text to clean markdown format with proper paragraphs. '''
    if not html_text.strip( ): return ''
    try: cleaned_html = _preprocess_sphinx_html( html_text )
    except Exception: return html_text
    try:
        markdown = _markdownify.markdownify(
            cleaned_html,
            heading_style = 'ATX',
            strip = [ 'nav', 'header', 'footer' ],
            escape_underscores = False,
            escape_asterisks = False )
    except Exception: return html_text
    return markdown.strip( )


def _preprocess_sphinx_html( html_text: str ) -> str:
    ''' Removes Sphinx-specific elements before markdownify processing. '''
    soup = _BeautifulSoup( html_text, 'lxml' )
    # Remove headerlink elements (¶ symbols)
    for element in soup.find_all( class_ = 'headerlink' ):
        element.decompose( )
    return str( soup )
