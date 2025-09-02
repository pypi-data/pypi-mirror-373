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


''' Docstrings table for reuse across entities. '''


from . import imports as __


def access_doctab( name: str ) -> str:
    ''' Returns cleaned string corresponding to fragment. '''
    return __.inspect.cleandoc( fragments[ name ] )


fragments: __.cabc.Mapping[ str, str ] = __.types.MappingProxyType( {

    # Arguments

    'group by argument':
    ''' Field to group results by (e.g., 'domain', 'role', 'priority'). ''',

    'include snippets argument':
    ''' Include content snippets in results. ''',

    'term argument':
    ''' Search term for documentation content. ''',

    'query details argument':
    ''' Detail level for inventory results.

        One of: Name, Signature, Summary, Documentation
    ''',

    'results max argument':
    ''' Maximum number of results to return. ''',

    'server port argument':
    ''' TCP port for server. ''',

    'location argument':
    ''' URL or file path to documentation location. ''',

    'term filter argument':
    ''' Filter objects by name containing this text. ''',

    'transport argument':
    ''' Transport: stdio or sse. ''',

    # Returns

    'content query return':
    ''' Documentation content search results with relevance ranking.
        Contains documents with signatures, descriptions, content snippets,
        relevance scores, and match reasons.
    ''',

    'inventory query return':
    ''' Inventory search results with configurable detail levels.
        Contains project metadata, matching objects, and search metadata
        with applied filters.
    ''',

    'inventory summary return':
    ''' Human-readable summary of inventory contents. ''',

} )
