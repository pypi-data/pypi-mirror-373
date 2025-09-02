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


''' Site processors. '''


from . import __
from . import exceptions as _exceptions
from . import interfaces as _interfaces
from . import results as _results
from . import state as _state


class Processor( __.immut.DataclassProtocol ):
    ''' Abstract base class for documentation source detectors. '''

    name: str

    @property
    @__.abc.abstractmethod
    def capabilities( self ) -> _interfaces.ProcessorCapabilities:
        ''' Returns processor capabilities for advertisement. '''
        raise NotImplementedError

    @__.abc.abstractmethod
    async def detect(
        self, auxdata: _state.Globals, source: str
    ) -> 'Detection':
        ''' Detects if can process documentation from source. '''
        raise NotImplementedError


InventoryProcessorsRegistry: __.typx.TypeAlias = (
    __.accret.ValidatorDictionary[ str, Processor ] )
StructureProcessorsRegistry: __.typx.TypeAlias = (
    __.accret.ValidatorDictionary[ str, Processor ] )


class Detection( __.immut.DataclassProtocol ):
    ''' Abstract base class for documentation detector selections. '''

    processor: Processor
    confidence: float
    timestamp: float = __.dcls.field( default_factory = __.time.time )

    @property
    def capabilities( self ) -> _interfaces.ProcessorCapabilities:
        ''' Returns capabilities for processor. '''
        return self.processor.capabilities

    def __post_init__( self ) -> None:
        ''' Validates confidence is in valid range [0.0, 1.0]. '''
        if not ( 0.0 <= self.confidence <= 1.0 ):
            raise _exceptions.DetectionConfidenceInvalidity( self.confidence )

    @classmethod
    @__.abc.abstractmethod
    async def from_source(
        selfclass,
        auxdata: _state.Globals,
        processor: Processor,
        source: str,
    ) -> __.typx.Self:
        ''' Constructs detection from source location. '''
        raise NotImplementedError


class InventoryDetection( Detection ):
    ''' Base class for inventory detection results. '''

    @__.abc.abstractmethod
    async def filter_inventory(
        self,
        auxdata: _state.Globals,
        source: str, /, *,
        filters: __.cabc.Mapping[ str, __.typx.Any ],
        details: _interfaces.InventoryQueryDetails = (
            _interfaces.InventoryQueryDetails.Documentation ),
    ) -> tuple[ _results.InventoryObject, ... ]:
        ''' Extracts and filters inventory objects from source. '''
        raise NotImplementedError


class StructureDetection( Detection ):
    ''' Base class for structure detection results. '''

    @__.abc.abstractmethod
    async def extract_contents(
        self,
        auxdata: _state.Globals,
        source: str,
        objects: __.cabc.Sequence[ _results.InventoryObject ], /,
    ) -> tuple[ _results.ContentDocument, ... ]:
        ''' Extracts documentation content for specified objects. '''
        raise NotImplementedError


DetectionsByProcessor: __.typx.TypeAlias = __.cabc.Mapping[ str, Detection ]


class DetectionsForLocation( __.immut.DataclassObject ):
    ''' Detections for location. '''

    source: str
    detections: DetectionsByProcessor
    detection_optimal: __.typx.Optional[ Detection ]
    time_detection_ms: int


def _inventory_validator( name: str, value: Processor ) -> bool:
    return isinstance( value, Processor )

def _structure_validator( name: str, value: Processor ) -> bool:
    return isinstance( value, Processor )


inventory_processors: InventoryProcessorsRegistry = (
    __.accret.ValidatorDictionary( _inventory_validator ) )
structure_processors: StructureProcessorsRegistry = (
    __.accret.ValidatorDictionary( _structure_validator ) )
