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


''' Logging utilities. '''


import logging as _logging

from . import imports as __


def report_exceptions(
    exception: BaseException | __.excg.ExceptionGroup[ Exception ],
    scribe: _logging.Logger,
) -> None:
    ''' Reports exception groups or individual exceptions to logger. '''
    if isinstance( exception, __.excg.ExceptionGroup ):
        for exc in exception.exceptions: # pyright: ignore
            report_exceptions( exc, scribe ) # pyright: ignore
    else:
        scribe.error( "{exception_class}: {exception}".format(
            exception_class = type( exception ), exception = exception ) )
