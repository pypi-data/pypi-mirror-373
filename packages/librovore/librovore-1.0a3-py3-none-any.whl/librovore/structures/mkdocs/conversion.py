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


''' HTML to markdown conversion for MkDocs content. '''


from bs4 import BeautifulSoup as _BeautifulSoup

from . import __


def html_to_markdown( html_text: str ) -> str:
    ''' Converts MkDocs HTML content to clean markdown format. '''
    if not html_text.strip( ): return ''
    try: soup = _BeautifulSoup( html_text, 'lxml' )
    except Exception: return html_text
    context = _MarkdownContext( )
    result = _convert_element_to_markdown( soup, context )
    return _clean_whitespace( result )


class _MarkdownContext:
    ''' Context for tracking state during HTML-to-Markdown conversion. '''

    def __init__( self ) -> None:
        self.in_admonition = False
        self.admonition_type = ''


def _convert_admonition(
    element: __.typx.Any, context: _MarkdownContext
) -> str:
    ''' Converts Material for MkDocs admonition to clean text. '''
    classes = element.get( 'class', [ ] )
    if isinstance( classes, str ):
        classes = classes.split( )
    admonition_type = 'Note'
    for cls in classes:
        if cls in ( 'note', 'info', 'warning', 'danger', 'tip' ):
            admonition_type = cls.capitalize( )
            break
    old_in_admonition = context.in_admonition
    old_admonition_type = context.admonition_type
    context.in_admonition = True
    context.admonition_type = admonition_type
    title_elem = element.find( class_ = 'admonition-title' )
    title = (
        title_elem.get_text( strip = True )
        if title_elem else admonition_type )
    content_parts: list[ str ] = [ ]
    for child in element.children:
        if ( hasattr( child, 'get' )
             and 'admonition-title' in child.get( 'class', [ ] ) ):
            continue
        converted = _convert_element_to_markdown( child, context )
        if converted.strip( ):
            content_parts.append( converted.strip( ) )
    context.in_admonition = old_in_admonition
    context.admonition_type = old_admonition_type
    content = ' '.join( content_parts )
    return f"**{title}**: {content}\n\n" if content else ''


def _convert_children(
    element: __.typx.Any, context: _MarkdownContext
) -> str:
    ''' Converts all child elements to markdown. '''
    result_parts: list[ str ] = [ ]
    for child in element.children:
        converted = _convert_element_to_markdown( child, context )
        result_parts.append( converted )
    return ''.join( result_parts )


def _convert_code_block(
    element: __.typx.Any, context: _MarkdownContext
) -> str:
    ''' Converts code block with language detection. '''
    language = _detect_code_language( element )
    code_element = element.find( 'code' ) or element.find( 'pre' )
    code_text = (
        code_element.get_text( ) if code_element else element.get_text( ) )
    code_text = code_text.strip( )
    if not code_text: return ''
    if language: return f"```{language}\n{code_text}\n```\n\n"
    return f"```\n{code_text}\n```\n\n"


def _convert_definition_list(
    element: __.typx.Any, context: _MarkdownContext
) -> str:
    ''' Converts definition list to markdown format. '''
    children = _convert_children( element, context )
    return f"{children}\n" if children.strip( ) else ''


def _convert_div( element: __.typx.Any, context: _MarkdownContext ) -> str:
    ''' Converts div elements with special handling for MkDocs patterns. '''
    classes = element.get( 'class', [ ] )
    if isinstance( classes, str ):
        classes = classes.split( )
    if 'admonition' in classes:
        return _convert_admonition( element, context )
    if 'highlight' in classes or 'codehilite' in classes:
        return _convert_code_block( element, context )
    if 'superfences' in classes:
        return _convert_code_block( element, context )
    children = _convert_children( element, context )
    return f"{children}\n\n" if children.strip( ) else ''


def _convert_element_to_markdown(
    element: __.typx.Any, context: _MarkdownContext
) -> str:
    ''' Converts HTML element to markdown using single-pass traversal. '''
    if hasattr( element, 'name' ) and element.name:
        return _convert_tag_to_markdown( element, context )
    return str( element )


def _convert_header( element: __.typx.Any ) -> str:
    ''' Converts header element to markdown. '''
    text = element.get_text( strip = True )
    if not text:
        return ''
    level = int( element.name[ 1 ] )
    prefix = '#' * level
    return f"{prefix} {text}\n\n"


def _convert_inline_code( element: __.typx.Any ) -> str:
    ''' Converts inline code element. '''
    text = element.get_text( )
    return f"`{text}`"


def _convert_link( element: __.typx.Any, context: _MarkdownContext ) -> str:
    ''' Converts anchor element to markdown link. '''
    href = element.get( 'href', '' )
    text = element.get_text( )
    if href and not href.startswith( '#' ):
        return f"[{text}]({href})"
    return text


def _convert_preformatted(
    element: __.typx.Any, context: _MarkdownContext
) -> str:
    ''' Converts preformatted text block. '''
    language = _detect_code_language( element )
    text = element.get_text( )
    if not text.strip( ):
        return ''
    if language:
        return f"```{language}\n{text}\n```\n\n"
    return f"```\n{text}\n```\n\n"


def _convert_span( element: __.typx.Any, context: _MarkdownContext ) -> str:
    ''' Converts span element with special handling for mkdocstrings. '''
    classes = element.get( 'class', [ ] )
    if isinstance( classes, str ):
        classes = classes.split( )
    if 'doc-heading' in classes:
        children = _convert_children( element, context )
        return f"**{children}**" if children.strip( ) else ''
    return _convert_children( element, context )


def _convert_table( element: __.typx.Any, context: _MarkdownContext ) -> str:
    ''' Converts HTML table to simple text representation. '''
    rows: list[ str ] = [ ]
    for row in element.find_all( 'tr' ):
        cells: list[ str ] = [ ]
        for cell in row.find_all( [ 'td', 'th' ] ):
            cell_text = cell.get_text( strip = True )
            cells.append( cell_text )
        if cells:
            rows.append( ' | '.join( cells ) )
    return '\n'.join( rows ) + '\n\n' if rows else ''


def _convert_tag_to_markdown(  # noqa: C901, PLR0911, PLR0912
    element: __.typx.Any, context: _MarkdownContext
) -> str:
    ''' Converts HTML tag to markdown with MkDocs-specific handling. '''
    if _should_skip_element( element ): return ''
    match element.name:
        case 'code': return _convert_inline_code( element )
        case 'pre': return _convert_preformatted( element, context )
        case 'strong' | 'b':
            children = _convert_children( element, context )
            return f"**{children}**" if children.strip( ) else ''
        case 'em' | 'i':
            children = _convert_children( element, context )
            return f"*{children}*" if children.strip( ) else ''
        case 'a': return _convert_link( element, context )
        case 'span': return _convert_span( element, context )
        case 'div': return _convert_div( element, context )
        case 'p' | 'section' | 'article':
            children = _convert_children( element, context )
            return f"{children}\n\n" if children.strip( ) else ''
        case 'li':
            children = _convert_children( element, context )
            return f"- {children}\n" if children.strip( ) else ''
        case 'ul' | 'ol':
            children = _convert_children( element, context )
            return f"{children}\n" if children.strip( ) else ''
        case 'dl':
            return _convert_definition_list( element, context )
        case 'dt':
            children = _convert_children( element, context )
            return f"**{children}**" if children.strip( ) else ''
        case 'dd':
            children = _convert_children( element, context )
            return f": {children}\n" if children.strip( ) else ''
        case 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6':
            return _convert_header( element )
        case 'br': return '\n'
        case 'table' | 'tr' | 'td' | 'th' | 'thead' | 'tbody':
            return _convert_table( element, context )
        case _:
            return _convert_children( element, context )


def _clean_whitespace( text: str ) -> str:
    ''' Cleans up whitespace while preserving markdown structure. '''
    text = __.re.sub( r' +', ' ', text )
    text = __.re.sub( r'\n +', '\n', text )
    text = __.re.sub( r' +\n', '\n', text )
    text = __.re.sub( r'\n{3,}', '\n\n', text )
    text = __.re.sub( r'^[ \t]+|[ \t]+$', '', text, flags = __.re.MULTILINE )
    return text.strip( )


def _detect_code_language( element: __.typx.Any ) -> str:  # noqa: C901, PLR0911
    ''' Detects programming language from code block element. '''
    classes = element.get( 'class', [ ] )
    if isinstance( classes, str ):
        classes = classes.split( )
    for cls in classes:
        if cls.startswith( 'language-' ):
            return cls[ 9: ]
        if cls.startswith( 'highlight-' ):
            return cls[ 10: ]
        if cls.startswith( 'lang-' ):
            return cls[ 5: ]
        if cls in ( 'python', 'javascript', 'typescript', 'bash', 'shell',
                   'json', 'yaml', 'xml', 'html', 'css', 'sql', 'rust',
                   'go', 'java', 'cpp', 'c' ):
            return cls
    code_element = element.find( 'code' )
    if code_element:
        code_classes = code_element.get( 'class', [ ] )
        if isinstance( code_classes, str ):
            code_classes = code_classes.split( )
        for cls in code_classes:
            if cls.startswith( 'language-' ):
                return cls[ 9: ]
            if cls.startswith( 'highlight-' ):
                return cls[ 10: ]
            if cls.startswith( 'lang-' ):
                return cls[ 5: ]
    return ''


def _should_skip_element( element: __.typx.Any ) -> bool:
    ''' Determines if element should be skipped entirely. '''
    classes = element.get( 'class', [ ] )
    if isinstance( classes, str ):
        classes = classes.split( )
    skip_classes = {
        'md-nav', 'md-header', 'md-footer', 'md-sidebar',
        'headerlink', 'md-clipboard', 'md-top',
        'toc', 'navigation', 'skip-link'
    }
    return (
        any( cls in skip_classes for cls in classes )
        or element.get( 'role' ) in ( 'navigation', 'banner', 'contentinfo' )
    )
