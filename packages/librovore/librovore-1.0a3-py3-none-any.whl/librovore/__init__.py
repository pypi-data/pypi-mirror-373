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


''' Model Context Protocol (MCP) server for Sphinx documentation. '''


from . import __
from . import server
from . import xtnsmgr
# --- BEGIN: Injected by Copier ---
from . import exceptions
# --- END: Injected by Copier ---


__version__: str
__version__ = '1.0a3'


def main( ):
    ''' Entrypoint. '''
    from .cli import execute
    execute( )


__.immut.finalize_module(
    __name__, dynadoc_table = __.doctab, recursive = True )
