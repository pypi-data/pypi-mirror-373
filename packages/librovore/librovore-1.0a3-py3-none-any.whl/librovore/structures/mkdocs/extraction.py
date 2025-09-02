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


''' MkDocs documentation content extraction and processing. '''


from bs4 import BeautifulSoup as _BeautifulSoup

from . import __


MATERIAL_THEME_PATTERNS: __.cabc.Mapping[
    str, __.cabc.Mapping[ str, __.typx.Any ]
] = __.immut.Dictionary( {
    'material': __.immut.Dictionary( {
        'main_content_selectors': [
            'article[role="main"]',
            '.md-content__inner',
            '.md-typeset',
            'main .md-content',
        ],
        'api_section_selectors': [
            '.doc.doc-object-member',
            '.doc.doc-children',
            'section[id]',
            '.highlight',
        ],
        'description_selectors': [
            '.doc-contents',
            '.doc-object-member .doc-contents',
            'p',
            '.admonition',
        ],
        'cleanup_selectors': [
            '.md-nav',
            '.md-header',
            '.md-footer',
            '.md-sidebar',
            '.headerlink',
            '.md-clipboard',
            'a.md-top',
        ],
        'code_block_selectors': [
            '.highlight',
            'pre code',
            '.codehilite',
        ],
    } ),
    'readthedocs': __.immut.Dictionary( {
        'main_content_selectors': [
            '.wy-nav-content-wrap main',
            '.document',
            '[role="main"]',
        ],
        'api_section_selectors': [
            '.section',
            'dl.class',
            'dl.function',
            'dl.method',
        ],
        'description_selectors': [
            'dd',
            '.field-body',
            'p',
        ],
        'cleanup_selectors': [
            '.headerlink',
            '.wy-nav-top',
            '.wy-nav-side',
        ],
        'code_block_selectors': [
            '.highlight',
            'pre',
        ],
    } ),
} )

_GENERIC_PATTERN = __.immut.Dictionary( {
    'main_content_selectors': [
        'article[role="main"]',
        'main',
        '.content',
        '.document',
        'body',
    ],
    'api_section_selectors': [
        'section[id]',
        'div[id]',
        '.doc-object-member',
        'dl',
    ],
    'description_selectors': [
        'p',
        'dd',
        '.description',
        '.doc-contents',
    ],
    'cleanup_selectors': [
        '.headerlink',
        'nav',
        'header',
        'footer',
        '.sidebar',
    ],
    'code_block_selectors': [
        '.highlight',
        'pre',
        'code',
    ],
} )


async def extract_contents(
    auxdata: __.ApplicationGlobals,
    source: str,
    objects: __.cabc.Sequence[ __.InventoryObject ], /, *,
    theme: __.Absential[ str ] = __.absent,
) -> list[ __.ContentDocument ]:
    ''' Extracts documentation content for specified objects from MkDocs. '''
    base_url = __.normalize_base_url( source )
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


def parse_mkdocs_html(
    content: str, element_id: str, url: str, *,
    theme: __.Absential[ str ] = __.absent
) -> __.cabc.Mapping[ str, str ]:
    ''' Parses MkDocs HTML content to extract documentation sections. '''
    try: soup = _BeautifulSoup( content, 'lxml' )
    except Exception as exc:
        raise __.DocumentationParseFailure( element_id, exc ) from exc
    main_container = _find_main_content_container( soup, theme )
    if __.is_absent( main_container ):
        raise __.DocumentationContentAbsence( element_id )
    target_element = _find_target_element( main_container, element_id )
    if not target_element:
        raise __.DocumentationObjectAbsence( element_id, url )
    description = _extract_content_from_element(
        target_element, element_id, theme )
    return {
        'description': description,
        'object_name': element_id,
    }




def _cleanup_content(
    content: str,
    cleanup_selectors: __.cabc.Sequence[ str ]
) -> str:
    ''' Removes unwanted elements from content. '''
    # TODO: Implement more sophisticated cleanup
    return content


def _convert_to_markdown( html_content: str ) -> str:
    ''' Converts HTML content to markdown format using markdownify. '''
    import markdownify
    return markdownify.markdownify( html_content, heading_style = 'ATX' )


def _derive_documentation_url(
    base_url: __.typx.Any, uri: str, object_name: str
) -> __.typx.Any:
    ''' Derives documentation URL from base URL and object URI. '''
    if uri.endswith( '#$' ):
        # mkdocstrings pattern - replace #$ with object name anchor
        clean_uri = uri[ :-2 ]
        new_path = f"{base_url.path}/{clean_uri}"
        return base_url._replace( path = new_path, fragment = object_name )
    if '#' in uri:
        path_part, fragment = uri.split( '#', 1 )
        new_path = f"{base_url.path}/{path_part}"
        return base_url._replace( path = new_path, fragment = fragment )
    new_path = f"{base_url.path}/{uri}"
    return base_url._replace( path = new_path, fragment = object_name )


def _extract_content_from_element(
    element: __.typx.Any,
    element_id: str,
    theme: __.Absential[ str ] = __.absent
) -> str:
    ''' Extracts description content from element. '''
    theme_name = theme if not __.is_absent( theme ) else 'material'
    patterns = MATERIAL_THEME_PATTERNS.get( theme_name, _GENERIC_PATTERN )
    description = _extract_description( element, patterns )
    cleanup_selectors = __.typx.cast(
        __.cabc.Sequence[ str ], patterns[ 'cleanup_selectors' ] )
    return _cleanup_content( description, cleanup_selectors )


def _extract_description(
    element: __.typx.Any,
    patterns: __.cabc.Mapping[ str, __.typx.Any ]
) -> str:
    ''' Extracts description content from element. '''
    doc_contents = _find_doc_contents_container( element )
    if doc_contents:
        return doc_contents.decode_contents( )
    descriptions = _extract_using_fallback_selectors( element, patterns )
    return '\n\n'.join( descriptions ) if descriptions else ''


async def _extract_object_documentation(
    auxdata: __.ApplicationGlobals,
    base_url: __.typx.Any,
    obj: __.InventoryObject,
    theme: __.Absential[ str ] = __.absent,
) -> __.ContentDocument | None:
    ''' Extracts documentation for a single object from MkDocs site. '''
    doc_url = _derive_documentation_url(
        base_url, obj.uri, obj.name )
    try:
        html_content = (
            await __.retrieve_url_as_text(
                auxdata.content_cache, doc_url ) )
    except Exception as exc:
        __.acquire_scribe( __name__ ).debug(
            "Failed to retrieve %s: %s", doc_url, exc )
        return None
    anchor = doc_url.fragment or str( obj.name )
    try:
        parsed_content = parse_mkdocs_html(
            html_content, anchor, str( doc_url ), theme = theme )
    except Exception: return None
    description = _convert_to_markdown( parsed_content[ 'description' ] )
    return __.ContentDocument(
        inventory_object = obj,
        description = description,
        documentation_url = doc_url.geturl( ),
        extraction_metadata = __.immut.Dictionary( {
            'theme': theme if not __.is_absent( theme ) else 'unknown',
            'extraction_method': 'mkdocs_html_parsing',
            'relevance_score': 1.0,
            'match_reasons': [ 'direct extraction' ],
        } )
    )




def _extract_using_fallback_selectors(
    element: __.typx.Any,
    patterns: __.cabc.Mapping[ str, __.typx.Any ]
) -> list[ str ]:
    ''' Extracts description using fallback selectors. '''
    descriptions: list[ str ] = [ ]
    description_selectors = __.typx.cast(
        __.cabc.Sequence[ str ], patterns[ 'description_selectors' ] )
    for selector in description_selectors:
        desc_elements = element.select( selector )
        for desc_elem in desc_elements:
            if (
                desc_elem.get( 'class' ) and
                'admonition-title' in desc_elem.get( 'class', [ ] )
            ): continue
            html_content = str( desc_elem )
            if html_content and html_content not in descriptions:
                descriptions.append( html_content )
    return descriptions


def _find_doc_contents_container( element: __.typx.Any ) -> __.typx.Any | None:
    ''' Finds the doc-contents container for the element. '''
    if element.name in ( 'h1', 'h2', 'h3', 'h4', 'h5', 'h6' ):
        sibling = element.next_sibling
        while sibling:
            if (
                hasattr( sibling, 'get' ) and sibling.name == 'div' and
                'doc-contents' in sibling.get( 'class', [ ] )
            ): return sibling
            sibling = sibling.next_sibling
    return element.select_one( '.doc-contents' )


def _find_target_element(
    container: __.typx.Any, element_id: str
) -> __.typx.Any:
    ''' Finds target element within main container using ID strategies. '''
    target = container.find( id = element_id )
    if target: return target
    target = container.find( attrs = { 'data-toc-label': element_id } )
    if target: return target
    for heading in container.find_all(
            [ 'h1', 'h2', 'h3', 'h4', 'h5', 'h6' ] ):
        if element_id in heading.get_text( ):
            return heading
    for section in container.find_all( 'section' ):
        class_attr = section.get( 'class' )
        if class_attr and element_id in ' '.join( class_attr ):
            return section
    return container


def _find_main_content_container(
    soup: __.typx.Any, theme: __.Absential[ str ] = __.absent
) -> __.Absential[ __.typx.Any ]:
    ''' Finds main content container using theme-specific strategies. '''
    theme_name = theme if not __.is_absent( theme ) else 'material'
    patterns = MATERIAL_THEME_PATTERNS.get( theme_name, _GENERIC_PATTERN )
    main_selectors = __.typx.cast(
        __.cabc.Sequence[ str ], patterns[ 'main_content_selectors' ] )
    for selector in main_selectors:
        container = soup.select_one( selector )
        if container: return container
    return __.absent
