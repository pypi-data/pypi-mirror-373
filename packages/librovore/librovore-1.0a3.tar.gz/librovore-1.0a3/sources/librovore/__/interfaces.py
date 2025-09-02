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


''' Internal enumerations and interfaces. '''


from . import imports as __


class DisplayStreams( __.enum.Enum ):
    ''' Stream upon which to place output. '''

    Stderr = 'stderr'
    Stdout = 'stdout'


class DisplayTarget( __.immut.DataclassObject ):
    silence: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            aliases = ( '--quiet', '--silent', ), prefix_name = False ),
    ] = False
    file: __.typx.Annotated[
        __.typx.Optional[ __.Path ],
        __.tyro.conf.arg(
            name = 'console-capture-file', prefix_name = False ),
    ] = None
    stream: __.typx.Annotated[
        DisplayStreams,
        __.tyro.conf.arg( name = 'console-stream', prefix_name = False ),
    ] = DisplayStreams.Stderr

    async def provide_stream( self ) -> __.io.TextIOWrapper:
        ''' Provides output stream for display. '''
        if self.file: return open( self.file, 'w' )
        match self.stream:
            case DisplayStreams.Stdout:
                return __.sys.stdout # pyright: ignore[reportReturnType]
            case DisplayStreams.Stderr:
                return __.sys.stderr # pyright: ignore[reportReturnType]
