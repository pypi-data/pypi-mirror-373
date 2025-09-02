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


''' Core business logic shared between CLI and MCP server. '''


from . import __
from . import detection as _detection
from . import exceptions as _exceptions
from . import interfaces as _interfaces
from . import processors as _processors
from . import results as _results
from . import search as _search
from . import state as _state


_SUCCESS_RATE_MINIMUM = 0.1


LocationArgument: __.typx.TypeAlias = __.typx.Annotated[
    str, __.ddoc.Fname( 'location argument' ) ]


_search_behaviors_default = _interfaces.SearchBehaviors( )
_filters_default = __.immut.Dictionary[ str, __.typx.Any ]( )


async def detect(
    auxdata: _state.Globals,
    location: LocationArgument, /,
    genus: _interfaces.ProcessorGenera,
    processor_name: __.Absential[ str ] = __.absent,
) -> _results.DetectionsResult:
    ''' Detects relevant processors of particular genus for location. '''
    location = _normalize_location( location )
    start_time = __.time.perf_counter( )
    detections, detection_optimal = (
        await _detection.access_detections(
            auxdata, location, genus = genus ) )
    end_time = __.time.perf_counter( )
    detection_time_ms = int( ( end_time - start_time ) * 1000 )
    if __.is_absent( detection_optimal ):
        genus_name = (
            genus.name.lower( ) if hasattr( genus, 'name' ) else str( genus ) )
        raise _exceptions.ProcessorInavailability(
            location,
            genus = genus_name )
    # Convert detections mapping to tuple of results.Detection objects
    detections_tuple = tuple(
        _results.Detection(
            processor_name = detection.processor.name,
            confidence = detection.confidence,
            processor_type = genus.value,
            detection_metadata = __.immut.Dictionary( ),
        )
        for detection in detections.values( )
    )
    # Convert detection_optimal to results.Detection
    detection_optimal_result = _results.Detection(
        processor_name = detection_optimal.processor.name,
        confidence = detection_optimal.confidence,
        processor_type = genus.value,
        detection_metadata = __.immut.Dictionary( ),
    )
    return _results.DetectionsResult(
        source = location,
        detections = detections_tuple,
        detection_optimal = detection_optimal_result,
        time_detection_ms = detection_time_ms )


async def query_content(  # noqa: PLR0913
    auxdata: _state.Globals,
    location: LocationArgument,
    term: str, /, *,
    processor_name: __.Absential[ str ] = __.absent,
    search_behaviors: _interfaces.SearchBehaviors = _search_behaviors_default,
    filters: __.cabc.Mapping[ str, __.typx.Any ] = _filters_default,
    results_max: int = 10,
    lines_max: __.typx.Optional[ int ] = None,
) -> _results.ContentQueryResult:
    ''' Searches documentation content with relevance ranking. '''
    location = _normalize_location( location )
    start_time = __.time.perf_counter( )
    idetection = await _detection.detect_inventory(
        auxdata, location, processor_name = processor_name )
    # Resolve URL after detection to get working URL if redirect exists
    resolved_location = _detection.resolve_source_url( location )
    objects = await idetection.filter_inventory(
        auxdata, resolved_location,
        filters = filters,
        details = _interfaces.InventoryQueryDetails.Name )
    results = _search.filter_by_name(
        objects, term,
        match_mode = search_behaviors.match_mode,
        fuzzy_threshold = search_behaviors.fuzzy_threshold )
    candidates = [
        result.inventory_object for result in results[ : results_max * 3 ] ]
    locations = tuple( [ _results.InventoryLocationInfo(
        inventory_type = idetection.processor.name,
        location_url = resolved_location,
        processor_name = idetection.processor.name,
        confidence = idetection.confidence,
        object_count = len( objects ) ) ] )
    if not candidates:
        end_time = __.time.perf_counter( )
        search_time_ms = int( ( end_time - start_time ) * 1000 )
        return _results.ContentQueryResult(
            location = resolved_location,
            query = term,
            documents = tuple( ),
            search_metadata = _results.SearchMetadata(
                results_count = 0,
                results_max = results_max,
                search_time_ms = search_time_ms ),
            inventory_locations = locations )
    sdetection = await _detection.detect_structure(
        auxdata, resolved_location, processor_name = processor_name )
    documents = await sdetection.extract_contents(
        auxdata, resolved_location, candidates[ : results_max ] )
    end_time = __.time.perf_counter( )
    search_time_ms = int( ( end_time - start_time ) * 1000 )
    return _results.ContentQueryResult(
        location = resolved_location,
        query = term,
        documents = tuple( documents ),
        search_metadata = _results.SearchMetadata(
            results_count = len( documents ),
            results_max = results_max,
            matches_total = len( candidates ),
            search_time_ms = search_time_ms ),
        inventory_locations = locations )


async def query_inventory(  # noqa: PLR0913
    auxdata: _state.Globals,
    location: LocationArgument,
    term: str, /, *,
    processor_name: __.Absential[ str ] = __.absent,
    search_behaviors: _interfaces.SearchBehaviors = _search_behaviors_default,
    filters: __.cabc.Mapping[ str, __.typx.Any ] = _filters_default,
    details: _interfaces.InventoryQueryDetails = (
        _interfaces.InventoryQueryDetails.Name ),
    results_max: int = 5,
) -> _results.InventoryQueryResult:
    ''' Searches object inventory by name.

        Returns configurable detail levels. Always includes object names
        plus requested detail flags (signatures, summaries, documentation).
    '''
    location = _normalize_location( location )
    start_time = __.time.perf_counter( )
    detection = await _detection.detect_inventory(
        auxdata, location, processor_name = processor_name )
    # Resolve URL after detection to get working URL if redirect exists
    resolved_location = _detection.resolve_source_url( location )
    objects = await detection.filter_inventory(
        auxdata, resolved_location, filters = filters, details = details )
    results = _search.filter_by_name(
        objects, term,
        match_mode = search_behaviors.match_mode,
        fuzzy_threshold = search_behaviors.fuzzy_threshold )
    selections = [
        result.inventory_object for result in results[ : results_max ] ]
    end_time = __.time.perf_counter( )
    search_time_ms = int( ( end_time - start_time ) * 1000 )
    return _results.InventoryQueryResult(
        location = resolved_location,
        query = term,
        objects = tuple( selections ),
        search_metadata = _results.SearchMetadata(
            results_count = len( selections ),
            results_max = results_max,
            matches_total = len( objects ),
            search_time_ms = search_time_ms ),
        inventory_locations = tuple( [
            _results.InventoryLocationInfo(
                inventory_type = detection.processor.name,
                location_url = resolved_location,
                processor_name = detection.processor.name,
                confidence = detection.confidence,
                object_count = len( objects ) ) ] ) )



async def survey_processors(
    auxdata: _state.Globals, /,
    genus: _interfaces.ProcessorGenera,
    name: __.typx.Optional[ str ] = None,
) -> _results.ProcessorsSurveyResult:
    ''' Lists processor capabilities for specified genus, filtered by name. '''
    start_time = __.time.perf_counter( )
    match genus:
        case _interfaces.ProcessorGenera.Inventory:
            processors = dict( _processors.inventory_processors )
        case _interfaces.ProcessorGenera.Structure:
            processors = dict( _processors.structure_processors )
    if name is not None and name not in processors:
        raise _exceptions.ProcessorInavailability(
            name,
            genus = genus.value )
    processor_infos: list[ _results.ProcessorInfo ] = [ ]
    for name_, processor in processors.items( ):
        if name is None or name_ == name:
            processor_info = _results.ProcessorInfo(
                processor_name = name_,
                processor_type = genus.value,
                capabilities = processor.capabilities,
            )
            processor_infos.append( processor_info )
    end_time = __.time.perf_counter( )
    survey_time_ms = int( ( end_time - start_time ) * 1000 )
    return _results.ProcessorsSurveyResult(
        genus = genus,
        filter_name = name,
        processors = tuple( processor_infos ),
        survey_time_ms = survey_time_ms,
    )



def _normalize_location( location: str ) -> str:
    ''' Normalizes location URL by stripping index.html. '''
    if location.endswith( '/' ): return location[ : -1 ]
    if location.endswith( '/index.html' ): return location[ : -11 ]
    return location



def _serialize_for_json( obj: __.typx.Any ) -> __.typx.Any:
    ''' Recursively serializes dataclass objects to JSON-compatible format. '''
    # TODO: Remove type suppressions.
    if __.dcls.is_dataclass( obj ):
        result = { }  # type: ignore[var-annotated]
        for field in __.dcls.fields( obj ):
            if field.name.startswith( '_' ):
                continue
            value = getattr( obj, field.name )
            result[ field.name ] = _serialize_for_json( value )
        return result  # type: ignore[return-value]
    if isinstance( obj, ( list, tuple ) ):
        return [ _serialize_for_json( item ) for item in obj ]  # type: ignore[misc]
    if isinstance( obj, ( frozenset, set ) ):
        return list( obj )  # type: ignore[arg-type]
    if hasattr( obj, 'items' ):  # Handle mappings (dict, frigid.Dictionary)
        return { k: _serialize_for_json( v ) for k, v in obj.items( ) }
    if obj is None or isinstance( obj, ( str, int, float, bool ) ):
        return obj
    return str( obj )
