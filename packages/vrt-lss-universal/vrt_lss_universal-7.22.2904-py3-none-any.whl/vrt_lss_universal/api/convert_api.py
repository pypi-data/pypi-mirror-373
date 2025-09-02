# coding: utf-8

"""
    VRt.Universal [UV]

    # Description  Software interface for universal trip planning.  ## Features  * Ability to pick up cargo from any location * Possibility of unloading in any location * Pair orders of several types: `PICKUP` (loading), `DROP` (unloading) * Single requests of several types: `DROP_FROM_BOX` (unloading cargo that is already in the body), `PICKUP_TO_BOX` (cargo pickup into the body without subsequent unloading), `WORK` (working at the location without moving the cargo) * A complex order can consist of any number of orders of any type * Transport and performers are divided into different entities, when planning, the optimal assignment of the performer to the transport occurs * The transport has several boxes - each of which can accommodate cargo and has its own characteristics * Accounting for the compatibility of cargo with transport in terms of cargo dimensions (length, width, height, additional capacity parameters) * Taking into account the compatibility of the cargo-box of transport (the ability to take into account the features of the box: refrigerator, thermal bag, fasteners, etc.) * Substitute applications, i.e. the ability to execute one of the substitute applications, the choice of which is based on its geographic location and time window  ## Restrictions support  **Performer** restrictions:  * Start/finish location * Accounting for the performer's way to the transport location * Performer's availability schedule is a list of time windows when the performer can move and work on locations * The maximum duration of the performer's work during the specified time period  **Transport** restrictions:  * Start/finish location * Transport availability schedule is a list of time windows when the transport is available * The maximum route distance * Several boxes in the transport, each with its own parameters * Capacity upper limit (weight, volume, number of orders, number of demands)  **Order** restrictions:  * Strict time windows * Ability to specify different valid time windows for a location and time windows to fulfil the desired demand * Accounting for the requests fulfillment order within the route * A list of desired time windows with different associated costs  ## Compatibilities  Entities are compatible if the capabilities list of one entity corresponds to the list of restrictions of another entity (example: fleet parameters corresponds to cargo parameters to be delivered).  Supported compatibilities:  | Name                    | Restrictions                     | Features                     | |-------------------------|----------------------------------|------------------------------| | Order - Performer       | order.performer_restrictions     | performer.performer_features | | Order - Not a performer | order.performer_blacklist        | performer.performer_features | | Cargo - Box             | order.cargo.box_restrictions     | transport.box.box_features   | | Location - Transport    | location.transport_restrictions  | transport.transport_features | | Transport - Performer   | transport.performer_restrictions | performer.performer_features | | Performer - Transport   | performer.transport_restrictions | transport.transport_features | | Order - Order           | order.order_restrictions         | order.order_features         |  Business rule examples:  | Name                    | Business rule example                                                                       | |-------------------------|---------------------------------------------------------------------------------------------| | Order - Performer       | The driver must have a special license to fulfil the order                                  | | Order - Not a performer | The driver is in the blacklist                                                              | | Cargo - Box             | For transportation of frozen products, a box with a special temperature profile is required | | Location - Transport    | Restrictions on the transport height                                                        | | Transport - Performer   | The truck driver must have the class C driving license                                      | | Performer - Transport   | The driver is allowed to work on a specific transport                                       | | Order - Order           | It is not allowed to transport fish and fruits in the same box                              |  ## Cargo placement  List of possibilities of a object rotations (90 degree step):  * `ALL` - can rotate by any axis * `YAW` - can yaw * `PITCH` - can pitch * `ROLL` - can roll    ![rotation](../images/universal_cargo_yaw_pitch_roll.svg)  ## Trip model  A trip is described by a list of states of the performer, while at the same time the performer can be in several states (for example, being inside the working time window of a location and fulfilling an order at the same location).  The meanings of the flags responsible for the geographical location:  * `AROUND_LOCATION` - the performer is located near the location - in the process of parking or leaving it. * `INSIDE_LOCATION` - the performer is located at the location.  The values ​​of the flags responsible for being in time windows:  * `INSIDE_WORKING_WINDOW` - the performer is inside the working time window. * `INSIDE_LOCATION_WINDOW` - the performer is located inside the location's operating time. * `INSIDE_EVENT_HARD_WINDOW` - the performer is inside a hard time window. * `INSIDE_EVENT_SOFT_WINDOW` - the performer is inside a soft time window.  The values ​​of the flags responsible for the actions:  * `ON_DEMAND` - the performer is working on the request. * `WAITING` - the performer is in standby mode. * `RELOCATING` - the performer moves to the next stop. * `BREAK` - the performer is on a break. * `REST` - the performer is on a long vacation.  Flag values ​​responsible for the logical state:  * `DURING_ROUNDTRIP` - the executor is performing a roundtrip.  ### An example of a route with multiple states at each point in time  | time  | set of active flags                                                                                                                                                          | location / order / application / event | comment                                                                                        | |:------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------|:-----------------------------------------------------------------------------------------------| | 10:00 | INSIDE_LOCATION <br/> AROUND_LOCATION                                                                                                                                        | 2 / - / - / -                          | starting location                                                                              | | 10:10 | RELOCATING                                                                                                                                                                   | - / - / - / -                          | we go to the first order                                                                       | | 10:20 | AROUND_LOCATION                                                                                                                                                              | 2 / - / - / -                          | arrived at the first order                                                                     | | 10:40 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> WAITING                                                                                                                          | 2 / - / - / -                          | parked                                                                                         | | 11:00 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> WAITING <br/> INSIDE_EVENT_HARD_WINDOW                                                              | 2 / - / - / -                          | waited for the start of the location window and at the same time the availability of the order | | 11:25 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> ON_DEMAND <br/> INSIDE_WORKING_WINDOW <br/> INSIDE_EVENT_HARD_WINDOW                                | 2 / 1 / 2 / 3                          | waited for the change of artist                                                                | | 11:30 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> ON_DEMAND <br/> INSIDE_WORKING_WINDOW <br/> INSIDE_EVENT_HARD_WINDOW <br/> INSIDE_EVENT_SOFT_WINDOW | 2 / 1 / 2 / 3                          | while working - a soft window happened                                                         | | 11:40 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> INSIDE_WORKING_WINDOW                                                                               | 2 / - / - / -                          | finished working                                                                               | | 11:45 | AROUND_LOCATION <br/> INSIDE_WORKING_WINDOW                                                                                                                                  | 2 / - / - / -                          | drove out of the parking lot                                                                   | | 11:45 | RELOCATING <br/> INSIDE_WORKING_WINDOW                                                                                                                                       | - / - / - / -                          | we go to the next order                                                                        |  ## Roundtrips  A trip consists of one or more round trips.  The flag of the presence of a round trip `DURING_ROUNDTRIP` is set when the work on the request starts and is removed in one of three cases:  * the executor arrived at the next location to stop using transport * the executor arrived at the location separating round trips * the executor stopped using transport (in a location not separating round trips, after performing some other action)  Between the end of one round trip and the beginning of another round trip, a change of location `RELOCATING` cannot occur, but the following can occur: waiting `WAITING`, a break for the executor `BREAK`, a rest for the executor `REST`.  Locations dividing a trip into round trips are defined as follows:  * if the location has a capacity limitation `timetable.limits` (in this case, there may be more than one location dividing the trip) * if the location is simultaneously the starting and ending location of all performers and transports, as well as all requests with the `PICKUP` type (in this case, there will be only one location dividing the trip)  Examples of such locations, depending on the task formulation, can be:  * distribution centers when delivering goods to stores or warehouses in long-haul transportation tasks * stores or warehouses when delivering goods to customers in last-mile tasks * landfills in garbage collection tasks  ## Planning configuration  For each planning, it is possible to specify a planning configuration that defines the objective function, the desired quality of the routes, and the calculation speed.  The name of the scheduling configuration is passed in the `trips_settings.configuration` field.  Main configurations:  | Title                           | Task                                                                                                                                                   | |---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------| | **optimize_distance**           | Arrange as many orders as possible, then optimize the total mileage (the number of vehicles is selected based on the mileage), used by default         | | **optimize_transports**         | Place as many orders as possible, while using as little transport as possible, ceteris paribus, optimize the work time of performers                   | | **optimize_locality_grouping**  | Place as many orders as possible, while striving to optimize the visual grouping of routes, but not their number                                       | | **optimize_cars_then_distance** | Arrange as many orders as possible, then optimize the number of vehicles, then the mileage                                                             | | **optimize_time**               | Place as many orders as possible, then optimize the total work time of performers                                                                      | | **optimize_cars_then_time**     | Arrange as many orders as possible, then optimize the number of transport, then the total time of the performers                                       | | **optimize_money**              | Optimize the value of \"profit - costs\", consists of rewards for applications and costs for performers and transports (optimized value is non-negative) |  Additional configurations:  | Title                                                     | Task                                                                                                                                                                                            | |-----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| | **visual_grouping**                                       | Arrange as many orders as possible while using as little transport as possible and routes should be visually grouped                                                                            | | **optimize_visual_grouping**                              | Arrange as many orders as possible, then evenly distribute orders taking into account transport accessibility zones (similar to visual_grouping, but visual grouping is calculated differently) | | **optimize_cars_then_locality_grouping**                  | Arrange as many orders as possible, then optimize the number of vehicles, then visually group the routes                                                                                        | | **optimize_cars_then_single_location_grouping_sequenced** | Place as many orders as possible, then optimize the number of machines, then reliability                                                                                                        |  In addition to the existing planning options, it is possible to create an objective function directly for the client's business processes ([request configuration](mailto:servicedesk@veeroute.com)).  For development, it is recommended to use **optimize_cars_then_distance**, since this configuration does not require detailed selection of rates and order values.  ## Data validation  Input data validation consists of several steps, which are described below.  Validation of planning results (including the search for possible reasons why orders were not planned) is located in the `analytics` method.  ### 1. Schema check  If the request does not follow the schema, then scheduling is not fully started and such an error is returned along with a 400 code in `schema_errors`.  We recommend validating the request against the schema (or yaml file) before sending it to the server.  ### 2. Check for logical errors that prevent planning from continuing  Schema-correct data passes the second stage of checking for the possibility of starting planning.  An example of errors at this stage are keys leading to empty entities, or if all orders are incompatible with all performers, i.e. something that makes the planning task pointless.  These errors are returned along with a 400 code in `logical_errors`.  ### 3. Check for logical errors that prevent planning from continuing  At the third stage, each entity is checked separately.  All entities that have not passed validation are cut out from the original task and are not sent for planning.  Depending on the setting of `treat_warnings_as_errors`, the results of this type of validation are returned to `warnings` either with a 400 code or with the scheduling result.  ### 4. Checks in the planning process  Part of the checks can only be carried out in the planning process.  For example - that according to the specified tariffs and according to the current traffic forecast, it is physically impossible to reach a certain point.  The results of these checks are returned in `warnings` or together with the scheduling result.  ## Entity relationship diagram  ![erd](../uml/universal.svg) 

    The version of the OpenAPI document: 7.22.2904
    Contact: servicedesk@veeroute.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

import warnings
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from pydantic import Field, StrictBytes, StrictStr
from typing import Optional, Union
from typing_extensions import Annotated
from vrt_lss_universal.models.universal_data import UniversalData

from vrt_lss_universal.api_client import ApiClient, RequestSerialized
from vrt_lss_universal.api_response import ApiResponse
from vrt_lss_universal.rest import RESTResponseType


class ConvertApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def run_convert_json_to_thrift(
        self,
        universal_data: Annotated[UniversalData, Field(description="Conversion request to the THRIFT.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> str:
        """JSON >> THRIFT

        Used for conversion of input data to the THRIFT format.

        :param universal_data: Conversion request to the THRIFT. (required)
        :type universal_data: UniversalData
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._run_convert_json_to_thrift_serialize(
            universal_data=universal_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "str",
            '400': "Custom400WithErrorsAndWarnings",
            '401': None,
            '402': "General402",
            '403': "General403",
            '406': None,
            '415': None,
            '429': "General429",
            '500': "General500",
            '501': None,
            '502': None,
            '503': None,
            '504': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def run_convert_json_to_thrift_with_http_info(
        self,
        universal_data: Annotated[UniversalData, Field(description="Conversion request to the THRIFT.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[str]:
        """JSON >> THRIFT

        Used for conversion of input data to the THRIFT format.

        :param universal_data: Conversion request to the THRIFT. (required)
        :type universal_data: UniversalData
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._run_convert_json_to_thrift_serialize(
            universal_data=universal_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "str",
            '400': "Custom400WithErrorsAndWarnings",
            '401': None,
            '402': "General402",
            '403': "General403",
            '406': None,
            '415': None,
            '429': "General429",
            '500': "General500",
            '501': None,
            '502': None,
            '503': None,
            '504': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def run_convert_json_to_thrift_without_preload_content(
        self,
        universal_data: Annotated[UniversalData, Field(description="Conversion request to the THRIFT.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """JSON >> THRIFT

        Used for conversion of input data to the THRIFT format.

        :param universal_data: Conversion request to the THRIFT. (required)
        :type universal_data: UniversalData
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._run_convert_json_to_thrift_serialize(
            universal_data=universal_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "str",
            '400': "Custom400WithErrorsAndWarnings",
            '401': None,
            '402': "General402",
            '403': "General403",
            '406': None,
            '415': None,
            '429': "General429",
            '500': "General500",
            '501': None,
            '502': None,
            '503': None,
            '504': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _run_convert_json_to_thrift_serialize(
        self,
        universal_data,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if universal_data is not None:
            _body_params = universal_data


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'text/plain', 
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'ApiKeyAuth'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/universal/convert/json-to-thrift',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def run_convert_json_to_xlsx(
        self,
        universal_data: Annotated[UniversalData, Field(description="Conversion request to the XLSX.")],
        timezone: Annotated[Optional[Annotated[int, Field(le=12, strict=True, ge=-12)]], Field(description="Target time zone.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> bytearray:
        """JSON >> XLSX

        Used for conversion of data to the [VRt.Universal XLSX](#tag/XLSX-Format) format.

        :param universal_data: Conversion request to the XLSX. (required)
        :type universal_data: UniversalData
        :param timezone: Target time zone.
        :type timezone: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._run_convert_json_to_xlsx_serialize(
            universal_data=universal_data,
            timezone=timezone,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "Custom400WithErrorsAndWarnings",
            '401': None,
            '402': "General402",
            '403': "General403",
            '406': None,
            '415': None,
            '429': "General429",
            '500': "General500",
            '501': None,
            '502': None,
            '503': None,
            '504': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def run_convert_json_to_xlsx_with_http_info(
        self,
        universal_data: Annotated[UniversalData, Field(description="Conversion request to the XLSX.")],
        timezone: Annotated[Optional[Annotated[int, Field(le=12, strict=True, ge=-12)]], Field(description="Target time zone.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[bytearray]:
        """JSON >> XLSX

        Used for conversion of data to the [VRt.Universal XLSX](#tag/XLSX-Format) format.

        :param universal_data: Conversion request to the XLSX. (required)
        :type universal_data: UniversalData
        :param timezone: Target time zone.
        :type timezone: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._run_convert_json_to_xlsx_serialize(
            universal_data=universal_data,
            timezone=timezone,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "Custom400WithErrorsAndWarnings",
            '401': None,
            '402': "General402",
            '403': "General403",
            '406': None,
            '415': None,
            '429': "General429",
            '500': "General500",
            '501': None,
            '502': None,
            '503': None,
            '504': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def run_convert_json_to_xlsx_without_preload_content(
        self,
        universal_data: Annotated[UniversalData, Field(description="Conversion request to the XLSX.")],
        timezone: Annotated[Optional[Annotated[int, Field(le=12, strict=True, ge=-12)]], Field(description="Target time zone.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """JSON >> XLSX

        Used for conversion of data to the [VRt.Universal XLSX](#tag/XLSX-Format) format.

        :param universal_data: Conversion request to the XLSX. (required)
        :type universal_data: UniversalData
        :param timezone: Target time zone.
        :type timezone: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._run_convert_json_to_xlsx_serialize(
            universal_data=universal_data,
            timezone=timezone,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
            '400': "Custom400WithErrorsAndWarnings",
            '401': None,
            '402': "General402",
            '403': "General403",
            '406': None,
            '415': None,
            '429': "General429",
            '500': "General500",
            '501': None,
            '502': None,
            '503': None,
            '504': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _run_convert_json_to_xlsx_serialize(
        self,
        universal_data,
        timezone,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if timezone is not None:
            
            _query_params.append(('timezone', timezone))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if universal_data is not None:
            _body_params = universal_data


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/octet-stream', 
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'ApiKeyAuth'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/universal/convert/json-to-xlsx',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def run_convert_xlsx_to_json(
        self,
        body: Annotated[Union[StrictBytes, StrictStr], Field(description="Conversion request to the JSON format.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> UniversalData:
        """XLSX >> JSON

        Used for data conversion from the [VRt.Universal XLSX](#tag/XLSX-Format) format to the VRt.Universal JSON format. 

        :param body: Conversion request to the JSON format. (required)
        :type body: bytearray
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._run_convert_xlsx_to_json_serialize(
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "UniversalData",
            '400': "Custom400WithErrorsAndWarnings",
            '401': None,
            '402': "General402",
            '403': "General403",
            '406': None,
            '415': None,
            '429': "General429",
            '500': "General500",
            '501': None,
            '502': None,
            '503': None,
            '504': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def run_convert_xlsx_to_json_with_http_info(
        self,
        body: Annotated[Union[StrictBytes, StrictStr], Field(description="Conversion request to the JSON format.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[UniversalData]:
        """XLSX >> JSON

        Used for data conversion from the [VRt.Universal XLSX](#tag/XLSX-Format) format to the VRt.Universal JSON format. 

        :param body: Conversion request to the JSON format. (required)
        :type body: bytearray
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._run_convert_xlsx_to_json_serialize(
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "UniversalData",
            '400': "Custom400WithErrorsAndWarnings",
            '401': None,
            '402': "General402",
            '403': "General403",
            '406': None,
            '415': None,
            '429': "General429",
            '500': "General500",
            '501': None,
            '502': None,
            '503': None,
            '504': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def run_convert_xlsx_to_json_without_preload_content(
        self,
        body: Annotated[Union[StrictBytes, StrictStr], Field(description="Conversion request to the JSON format.")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """XLSX >> JSON

        Used for data conversion from the [VRt.Universal XLSX](#tag/XLSX-Format) format to the VRt.Universal JSON format. 

        :param body: Conversion request to the JSON format. (required)
        :type body: bytearray
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._run_convert_xlsx_to_json_serialize(
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "UniversalData",
            '400': "Custom400WithErrorsAndWarnings",
            '401': None,
            '402': "General402",
            '403': "General403",
            '406': None,
            '415': None,
            '429': "General429",
            '500': "General500",
            '501': None,
            '502': None,
            '503': None,
            '504': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _run_convert_xlsx_to_json_serialize(
        self,
        body,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body is not None:
            _body_params = body


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/octet-stream'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'ApiKeyAuth'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/universal/convert/xlsx-to-json',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


