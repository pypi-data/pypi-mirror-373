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


''' Documentation extraction and content retrieval. '''


from bs4 import BeautifulSoup as _BeautifulSoup

from . import __
from . import urls as _urls


_scribe = __.acquire_scribe( __name__ )


# Theme-specific content extraction patterns
THEME_EXTRACTION_PATTERNS: __.cabc.Mapping[
    str, __.cabc.Mapping[ str, __.typx.Any ]
] = __.immut.Dictionary( {
    'pydoctheme': __.immut.Dictionary( {
        'anchor_elements': [ 'dt', 'a' ],
        'content_strategies': __.immut.Dictionary( {
            'dt': __.immut.Dictionary( {
                'description_source': 'next_sibling',
                'description_element': 'dd',
            } ),
            'a': __.immut.Dictionary( {
                'description_source': 'parent_next_sibling',
                'description_element': 'dd',
            } ),
        } ),
        'cleanup_selectors': [ 'a.headerlink' ],
    } ),
    'furo': __.immut.Dictionary( {
        'anchor_elements': [ 'span', 'a', 'dt' ],
        'content_strategies': __.immut.Dictionary( {
            'span': __.immut.Dictionary( {
                'description_source': 'parent_next_element',
                'description_element': 'p',
                'fallback_container': 'section',
            } ),
            'a': __.immut.Dictionary( {
                'description_source': 'parent_next_element',
                'description_element': 'p',
            } ),
            'dt': __.immut.Dictionary( {
                'description_source': 'next_sibling',
                'description_element': 'dd',
            } ),
        } ),
        'cleanup_selectors': [ 'a.headerlink', '.highlight' ],
    } ),
    'sphinx_rtd_theme': __.immut.Dictionary( {
        'anchor_elements': [ 'dt', 'span', 'a' ],
        'content_strategies': __.immut.Dictionary( {
            'dt': __.immut.Dictionary( {
                'description_source': 'next_sibling',
                'description_element': 'dd',
            } ),
            'span': __.immut.Dictionary( {
                'description_source': 'parent_content',
                'description_element': 'p',
            } ),
        } ),
        'cleanup_selectors': [ 'a.headerlink' ],
    } ),
} )

# Generic fallback pattern for unknown themes
_GENERIC_PATTERN = __.immut.Dictionary( {
    'anchor_elements': [ 'dt', 'span', 'a', 'section', 'div' ],
    'content_strategies': __.immut.Dictionary( {
        'dt': __.immut.Dictionary( {
            'description_source': 'next_sibling',
            'description_element': 'dd',
        } ),
        'section': __.immut.Dictionary( {
            'description_source': 'first_paragraph',
            'description_element': 'p',
        } ),
        'span': __.immut.Dictionary( {
            'description_source': 'parent_next_element',
            'description_element': 'p',
        } ),
        'a': __.immut.Dictionary( {
            'description_source': 'parent_next_element',
            'description_element': 'p',
        } ),
    } ),
    'cleanup_selectors': [ 'a.headerlink' ],
} )


async def extract_contents(
    auxdata: __.ApplicationGlobals,
    source: str,
    objects: __.cabc.Sequence[ __.InventoryObject ], /, *,
    theme: __.Absential[ str ] = __.absent,
) -> list[ __.ContentDocument ]:
    ''' Extracts documentation content for specified objects. '''
    base_url = _urls.normalize_base_url( source )
    if not objects: return [ ]
    tasks = [
        _extract_object_documentation(
            auxdata, base_url, obj, theme )
        for obj in objects ]
    candidate_results = await __.asyncf.gather_async(
        *tasks, return_exceptions = True )
    results: list[ __.ContentDocument ] = [
        result.value for result in candidate_results
        if __.generics.is_value( result ) and result.value is not None ]
    return results


def parse_documentation_html(
    content: str, element_id: str, url: str, *,
    theme: __.Absential[ str ] = __.absent
) -> __.cabc.Mapping[ str, str ]:
    ''' Parses HTML content to extract documentation sections. '''
    try: soup = _BeautifulSoup( content, 'lxml' )
    except Exception as exc:
        raise __.DocumentationParseFailure(
            element_id, exc ) from exc
    # Theme should be provided from detection metadata
    # If absent, use None to fall back to generic detection
    container = _find_main_content_container( soup, theme )
    if __.is_absent( container ):
        raise __.DocumentationContentAbsence( element_id )
    element = container.find( id = element_id )
    if not element:
        raise __.DocumentationObjectAbsence( element_id, url )
    description = _extract_content_with_dsl(
        element, element_id, theme )
    return {
        'description': description,
        'object_name': element_id,
    }


def _cleanup_content(
    content: str,
    cleanup_selectors: __.cabc.Sequence[ str ]
) -> str:
    ''' Removes unwanted elements from content using CSS selectors. '''
    # TODO: Implement CSS selector-based cleanup
    return content


def _extract_content_with_dsl(
    element: __.typx.Any,
    element_id: str,
    theme: __.Absential[ str ] = __.absent
) -> str:
    ''' Extracts content using DSL pattern configuration. '''
    theme_name = theme if not __.is_absent( theme ) else None
    if theme_name is not None:
        pattern = THEME_EXTRACTION_PATTERNS.get( theme_name, _GENERIC_PATTERN )
    else: pattern = _GENERIC_PATTERN
    content_strategies = __.typx.cast(
        __.cabc.Mapping[ str, __.cabc.Mapping[ str, __.typx.Any ] ],
        pattern[ 'content_strategies' ] )
    strategy = content_strategies.get( element.name )
    if not strategy: return _generic_extraction( element )
    description = _extract_description_with_strategy( element, strategy )
    if 'cleanup_selectors' in pattern:
        cleanup_selectors = __.typx.cast(
            __.cabc.Sequence[ str ], pattern[ 'cleanup_selectors' ] )
        description = _cleanup_content( description, cleanup_selectors )
    return description


def _extract_description_with_strategy(
    element: __.typx.Any,
    strategy: __.cabc.Mapping[ str, __.typx.Any ]
) -> str:
    ''' Extracts description using DSL strategy. '''
    source_type = __.typx.cast( str, strategy[ 'description_source' ] )
    element_type = __.typx.cast(
        str, strategy.get( 'description_element', 'p' ) )
    return _get_description_by_source_type(
        element, source_type, element_type )


async def _extract_object_documentation(
    auxdata: __.ApplicationGlobals,
    base_url: __.typx.Any,
    obj: __.InventoryObject,
    theme: __.Absential[ str ] = __.absent,
) -> __.ContentDocument | None:
    ''' Extracts documentation for a single object. '''
    from . import conversion as _conversion
    doc_url = _urls.derive_documentation_url(
        base_url, obj.uri, obj.name )
    try:
        html_content = (
            await __.retrieve_url_as_text(
                auxdata.content_cache, doc_url ) )
    except Exception as exc:
        _scribe.debug( "Failed to retrieve %s: %s", doc_url, exc )
        return None
    anchor = doc_url.fragment or str( obj.name )
    try:
        parsed_content = parse_documentation_html(
            html_content, anchor, str( doc_url ), theme = theme )
    except Exception: return None
    description = _conversion.html_to_markdown(
        parsed_content[ 'description' ] )
    return __.ContentDocument(
        inventory_object = obj,
        description = description,
        documentation_url = doc_url.geturl( ),
        extraction_metadata = __.immut.Dictionary( {
            'theme': theme if not __.is_absent( theme ) else 'unknown',
            'extraction_method': 'sphinx_html_parsing',
            'relevance_score': 1.0,
            'match_reasons': [ 'direct extraction' ],
        } )
    )




def _find_main_content_container(
    soup: __.typx.Any, theme: __.Absential[ str ] = __.absent
) -> __.Absential[ __.typx.Any ]:
    ''' Finds the main content container using theme-specific strategies. '''
    if theme == 'furo':
        containers = [
            soup.find( 'article', { 'role': 'main' } ),
            soup.find( 'div', { 'id': 'furo-main-content' } ),
        ]
    elif theme == 'sphinx_rtd_theme':
        containers = [
            soup.find( 'div', { 'class': 'document' } ),
            soup.find( 'div', { 'class': 'body' } ),
            soup.find( 'div', { 'role': 'main' } ),
        ]
    elif theme == 'pydoctheme':  # Python docs
        containers = [
            soup.find( 'div', { 'class': 'body' } ),
            soup.find( 'div', { 'class': 'content' } ),
            soup.body,  # Python docs often use body directly
        ]
    elif theme == 'flask':  # Flask docs
        containers = [
            soup.find( 'div', { 'class': 'body' } ),
            soup.find( 'div', { 'class': 'content' } ),
            soup.body,
        ]
    elif theme == 'alabaster':
        containers = [
            soup.find( 'div', { 'class': 'body' } ),
            soup.find( 'div', { 'class': 'content' } ),
        ]
    else:  # Generic fallback for unknown themes
        containers = [
            soup.find( 'article', { 'role': 'main' } ),  # Furo theme
            soup.find( 'div', { 'class': 'body' } ),  # Basic theme
            soup.find( 'div', { 'class': 'content' } ),  # Nature theme
            soup.find( 'div', { 'class': 'main' } ),  # Generic main
            soup.find( 'main' ),  # HTML5 main element
            soup.find( 'div', { 'role': 'main' } ),  # Role-based
            soup.body,  # Fallback to body if nothing else works
        ]
    for container in containers:
        if container: return container
    return __.absent




def _generic_extraction( element: __.typx.Any ) -> str:
    ''' Generic fallback extraction for unknown element types. '''
    description = ''
    if element.parent:
        next_p = element.parent.find( 'p' )
        if next_p:
            description = str( next_p )
    return description


def _get_description_by_source_type(
    element: __.typx.Any,
    source_type: str,
    element_type: str
) -> str:
    ''' Gets description content based on source type. '''
    match source_type:
        case 'next_sibling':
            return _get_sibling_text( element, element_type )
        case 'parent_next_sibling':
            return _get_parent_sibling_text( element, element_type )
        case 'parent_next_element':
            return _get_parent_element_text( element, element_type )
        case 'parent_content':
            return _get_parent_content_text( element, element_type )
        case 'first_paragraph':
            return _get_first_paragraph_text( element )
        case _: return ''


def _get_first_paragraph_text( element: __.typx.Any ) -> str:
    ''' Gets HTML content from first paragraph within element. '''
    paragraph = element.find( 'p' )
    return str( paragraph ) if paragraph else ''


def _get_parent_content_text( element: __.typx.Any, element_type: str ) -> str:
    ''' Gets HTML content from content element within parent. '''
    if element.parent:
        content_elem = element.parent.find( element_type )
        return content_elem.decode_contents( ) if content_elem else ''
    return ''


def _get_parent_element_text( element: __.typx.Any, element_type: str ) -> str:
    ''' Gets HTML content from element within parent. '''
    if element.parent:
        next_elem = element.parent.find( element_type )
        return next_elem.decode_contents( ) if next_elem else ''
    return ''


def _get_parent_sibling_text( element: __.typx.Any, element_type: str ) -> str:
    ''' Gets HTML content from parent's next sibling element. '''
    if element.parent:
        sibling = element.parent.find_next_sibling( element_type )
        return sibling.decode_contents( ) if sibling else ''
    return ''


def _get_sibling_text( element: __.typx.Any, element_type: str ) -> str:
    ''' Gets HTML content from next sibling element. '''
    sibling = element.find_next_sibling( element_type )
    return sibling.decode_contents( ) if sibling else ''
