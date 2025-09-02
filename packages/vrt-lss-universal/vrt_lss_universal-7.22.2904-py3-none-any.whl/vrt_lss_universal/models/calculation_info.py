# coding: utf-8

"""
    VRt.Universal [UV]

    # Description  Software interface for universal trip planning.  ## Features  * Ability to pick up cargo from any location * Possibility of unloading in any location * Pair orders of several types: `PICKUP` (loading), `DROP` (unloading) * Single requests of several types: `DROP_FROM_BOX` (unloading cargo that is already in the body), `PICKUP_TO_BOX` (cargo pickup into the body without subsequent unloading), `WORK` (working at the location without moving the cargo) * A complex order can consist of any number of orders of any type * Transport and performers are divided into different entities, when planning, the optimal assignment of the performer to the transport occurs * The transport has several boxes - each of which can accommodate cargo and has its own characteristics * Accounting for the compatibility of cargo with transport in terms of cargo dimensions (length, width, height, additional capacity parameters) * Taking into account the compatibility of the cargo-box of transport (the ability to take into account the features of the box: refrigerator, thermal bag, fasteners, etc.) * Substitute applications, i.e. the ability to execute one of the substitute applications, the choice of which is based on its geographic location and time window  ## Restrictions support  **Performer** restrictions:  * Start/finish location * Accounting for the performer's way to the transport location * Performer's availability schedule is a list of time windows when the performer can move and work on locations * The maximum duration of the performer's work during the specified time period  **Transport** restrictions:  * Start/finish location * Transport availability schedule is a list of time windows when the transport is available * The maximum route distance * Several boxes in the transport, each with its own parameters * Capacity upper limit (weight, volume, number of orders, number of demands)  **Order** restrictions:  * Strict time windows * Ability to specify different valid time windows for a location and time windows to fulfil the desired demand * Accounting for the requests fulfillment order within the route * A list of desired time windows with different associated costs  ## Compatibilities  Entities are compatible if the capabilities list of one entity corresponds to the list of restrictions of another entity (example: fleet parameters corresponds to cargo parameters to be delivered).  Supported compatibilities:  | Name                    | Restrictions                     | Features                     | |-------------------------|----------------------------------|------------------------------| | Order - Performer       | order.performer_restrictions     | performer.performer_features | | Order - Not a performer | order.performer_blacklist        | performer.performer_features | | Cargo - Box             | order.cargo.box_restrictions     | transport.box.box_features   | | Location - Transport    | location.transport_restrictions  | transport.transport_features | | Transport - Performer   | transport.performer_restrictions | performer.performer_features | | Performer - Transport   | performer.transport_restrictions | transport.transport_features | | Order - Order           | order.order_restrictions         | order.order_features         |  Business rule examples:  | Name                    | Business rule example                                                                       | |-------------------------|---------------------------------------------------------------------------------------------| | Order - Performer       | The driver must have a special license to fulfil the order                                  | | Order - Not a performer | The driver is in the blacklist                                                              | | Cargo - Box             | For transportation of frozen products, a box with a special temperature profile is required | | Location - Transport    | Restrictions on the transport height                                                        | | Transport - Performer   | The truck driver must have the class C driving license                                      | | Performer - Transport   | The driver is allowed to work on a specific transport                                       | | Order - Order           | It is not allowed to transport fish and fruits in the same box                              |  ## Cargo placement  List of possibilities of a object rotations (90 degree step):  * `ALL` - can rotate by any axis * `YAW` - can yaw * `PITCH` - can pitch * `ROLL` - can roll    ![rotation](../images/universal_cargo_yaw_pitch_roll.svg)  ## Trip model  A trip is described by a list of states of the performer, while at the same time the performer can be in several states (for example, being inside the working time window of a location and fulfilling an order at the same location).  The meanings of the flags responsible for the geographical location:  * `AROUND_LOCATION` - the performer is located near the location - in the process of parking or leaving it. * `INSIDE_LOCATION` - the performer is located at the location.  The values ​​of the flags responsible for being in time windows:  * `INSIDE_WORKING_WINDOW` - the performer is inside the working time window. * `INSIDE_LOCATION_WINDOW` - the performer is located inside the location's operating time. * `INSIDE_EVENT_HARD_WINDOW` - the performer is inside a hard time window. * `INSIDE_EVENT_SOFT_WINDOW` - the performer is inside a soft time window.  The values ​​of the flags responsible for the actions:  * `ON_DEMAND` - the performer is working on the request. * `WAITING` - the performer is in standby mode. * `RELOCATING` - the performer moves to the next stop. * `BREAK` - the performer is on a break. * `REST` - the performer is on a long vacation.  Flag values ​​responsible for the logical state:  * `DURING_ROUNDTRIP` - the executor is performing a roundtrip.  ### An example of a route with multiple states at each point in time  | time  | set of active flags                                                                                                                                                          | location / order / application / event | comment                                                                                        | |:------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------|:-----------------------------------------------------------------------------------------------| | 10:00 | INSIDE_LOCATION <br/> AROUND_LOCATION                                                                                                                                        | 2 / - / - / -                          | starting location                                                                              | | 10:10 | RELOCATING                                                                                                                                                                   | - / - / - / -                          | we go to the first order                                                                       | | 10:20 | AROUND_LOCATION                                                                                                                                                              | 2 / - / - / -                          | arrived at the first order                                                                     | | 10:40 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> WAITING                                                                                                                          | 2 / - / - / -                          | parked                                                                                         | | 11:00 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> WAITING <br/> INSIDE_EVENT_HARD_WINDOW                                                              | 2 / - / - / -                          | waited for the start of the location window and at the same time the availability of the order | | 11:25 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> ON_DEMAND <br/> INSIDE_WORKING_WINDOW <br/> INSIDE_EVENT_HARD_WINDOW                                | 2 / 1 / 2 / 3                          | waited for the change of artist                                                                | | 11:30 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> ON_DEMAND <br/> INSIDE_WORKING_WINDOW <br/> INSIDE_EVENT_HARD_WINDOW <br/> INSIDE_EVENT_SOFT_WINDOW | 2 / 1 / 2 / 3                          | while working - a soft window happened                                                         | | 11:40 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> INSIDE_WORKING_WINDOW                                                                               | 2 / - / - / -                          | finished working                                                                               | | 11:45 | AROUND_LOCATION <br/> INSIDE_WORKING_WINDOW                                                                                                                                  | 2 / - / - / -                          | drove out of the parking lot                                                                   | | 11:45 | RELOCATING <br/> INSIDE_WORKING_WINDOW                                                                                                                                       | - / - / - / -                          | we go to the next order                                                                        |  ## Roundtrips  A trip consists of one or more round trips.  The flag of the presence of a round trip `DURING_ROUNDTRIP` is set when the work on the request starts and is removed in one of three cases:  * the executor arrived at the next location to stop using transport * the executor arrived at the location separating round trips * the executor stopped using transport (in a location not separating round trips, after performing some other action)  Between the end of one round trip and the beginning of another round trip, a change of location `RELOCATING` cannot occur, but the following can occur: waiting `WAITING`, a break for the executor `BREAK`, a rest for the executor `REST`.  Locations dividing a trip into round trips are defined as follows:  * if the location has a capacity limitation `timetable.limits` (in this case, there may be more than one location dividing the trip) * if the location is simultaneously the starting and ending location of all performers and transports, as well as all requests with the `PICKUP` type (in this case, there will be only one location dividing the trip)  Examples of such locations, depending on the task formulation, can be:  * distribution centers when delivering goods to stores or warehouses in long-haul transportation tasks * stores or warehouses when delivering goods to customers in last-mile tasks * landfills in garbage collection tasks  ## Planning configuration  For each planning, it is possible to specify a planning configuration that defines the objective function, the desired quality of the routes, and the calculation speed.  The name of the scheduling configuration is passed in the `trips_settings.configuration` field.  Main configurations:  | Title                           | Task                                                                                                                                                   | |---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------| | **optimize_distance**           | Arrange as many orders as possible, then optimize the total mileage (the number of vehicles is selected based on the mileage), used by default         | | **optimize_transports**         | Place as many orders as possible, while using as little transport as possible, ceteris paribus, optimize the work time of performers                   | | **optimize_locality_grouping**  | Place as many orders as possible, while striving to optimize the visual grouping of routes, but not their number                                       | | **optimize_cars_then_distance** | Arrange as many orders as possible, then optimize the number of vehicles, then the mileage                                                             | | **optimize_time**               | Place as many orders as possible, then optimize the total work time of performers                                                                      | | **optimize_cars_then_time**     | Arrange as many orders as possible, then optimize the number of transport, then the total time of the performers                                       | | **optimize_money**              | Optimize the value of \"profit - costs\", consists of rewards for applications and costs for performers and transports (optimized value is non-negative) |  Additional configurations:  | Title                                                     | Task                                                                                                                                                                                            | |-----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| | **visual_grouping**                                       | Arrange as many orders as possible while using as little transport as possible and routes should be visually grouped                                                                            | | **optimize_visual_grouping**                              | Arrange as many orders as possible, then evenly distribute orders taking into account transport accessibility zones (similar to visual_grouping, but visual grouping is calculated differently) | | **optimize_cars_then_locality_grouping**                  | Arrange as many orders as possible, then optimize the number of vehicles, then visually group the routes                                                                                        | | **optimize_cars_then_single_location_grouping_sequenced** | Place as many orders as possible, then optimize the number of machines, then reliability                                                                                                        |  In addition to the existing planning options, it is possible to create an objective function directly for the client's business processes ([request configuration](mailto:servicedesk@veeroute.com)).  For development, it is recommended to use **optimize_cars_then_distance**, since this configuration does not require detailed selection of rates and order values.  ## Data validation  Input data validation consists of several steps, which are described below.  Validation of planning results (including the search for possible reasons why orders were not planned) is located in the `analytics` method.  ### 1. Schema check  If the request does not follow the schema, then scheduling is not fully started and such an error is returned along with a 400 code in `schema_errors`.  We recommend validating the request against the schema (or yaml file) before sending it to the server.  ### 2. Check for logical errors that prevent planning from continuing  Schema-correct data passes the second stage of checking for the possibility of starting planning.  An example of errors at this stage are keys leading to empty entities, or if all orders are incompatible with all performers, i.e. something that makes the planning task pointless.  These errors are returned along with a 400 code in `logical_errors`.  ### 3. Check for logical errors that prevent planning from continuing  At the third stage, each entity is checked separately.  All entities that have not passed validation are cut out from the original task and are not sent for planning.  Depending on the setting of `treat_warnings_as_errors`, the results of this type of validation are returned to `warnings` either with a 400 code or with the scheduling result.  ### 4. Checks in the planning process  Part of the checks can only be carried out in the planning process.  For example - that according to the specified tariffs and according to the current traffic forecast, it is physically impossible to reach a certain point.  The results of these checks are returned in `warnings` or together with the scheduling result.  ## Entity relationship diagram  ![erd](../uml/universal.svg) 

    The version of the OpenAPI document: 7.22.2904
    Contact: servicedesk@veeroute.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from vrt_lss_universal.models.calculation_status import CalculationStatus
from typing import Optional, Set
from typing_extensions import Self

class CalculationInfo(BaseModel):
    """
    Calculation information.
    """ # noqa: E501
    status: CalculationStatus
    message: Optional[StrictStr] = Field(default=None, description="Message with additional information about the calculation status.")
    result_version: Annotated[int, Field(le=1000000, strict=True, ge=0)] = Field(description="Planning result version.")
    preparing_time: Annotated[str, Field(min_length=3, strict=True, max_length=16)] = Field(description="Time duration according to [ISO 8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations).")
    business_validation_time: Annotated[str, Field(min_length=3, strict=True, max_length=16)] = Field(description="Time duration according to [ISO 8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations).")
    math_validation_time: Annotated[str, Field(min_length=3, strict=True, max_length=16)] = Field(description="Time duration according to [ISO 8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations).")
    waiting_time: Annotated[str, Field(min_length=3, strict=True, max_length=16)] = Field(description="Time duration according to [ISO 8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations).")
    calculation_time: Annotated[str, Field(min_length=3, strict=True, max_length=16)] = Field(description="Time duration according to [ISO 8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations).")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["status", "message", "result_version", "preparing_time", "business_validation_time", "math_validation_time", "waiting_time", "calculation_time"]

    @field_validator('preparing_time')
    def preparing_time_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^P(?!$)((\d+Y)|(\d+\.\d+Y$))?((\d+M)|(\d+\.\d+M$))?((\d+W)|(\d+\.\d+W$))?((\d+D)|(\d+\.\d+D$))?(T(?=\d)((\d+H)|(\d+\.\d+H$))?((\d+M)|(\d+\.\d+M$))?(\d+(\.\d+)?S)?)??$", value):
            raise ValueError(r"must validate the regular expression /^P(?!$)((\d+Y)|(\d+\.\d+Y$))?((\d+M)|(\d+\.\d+M$))?((\d+W)|(\d+\.\d+W$))?((\d+D)|(\d+\.\d+D$))?(T(?=\d)((\d+H)|(\d+\.\d+H$))?((\d+M)|(\d+\.\d+M$))?(\d+(\.\d+)?S)?)??$/")
        return value

    @field_validator('business_validation_time')
    def business_validation_time_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^P(?!$)((\d+Y)|(\d+\.\d+Y$))?((\d+M)|(\d+\.\d+M$))?((\d+W)|(\d+\.\d+W$))?((\d+D)|(\d+\.\d+D$))?(T(?=\d)((\d+H)|(\d+\.\d+H$))?((\d+M)|(\d+\.\d+M$))?(\d+(\.\d+)?S)?)??$", value):
            raise ValueError(r"must validate the regular expression /^P(?!$)((\d+Y)|(\d+\.\d+Y$))?((\d+M)|(\d+\.\d+M$))?((\d+W)|(\d+\.\d+W$))?((\d+D)|(\d+\.\d+D$))?(T(?=\d)((\d+H)|(\d+\.\d+H$))?((\d+M)|(\d+\.\d+M$))?(\d+(\.\d+)?S)?)??$/")
        return value

    @field_validator('math_validation_time')
    def math_validation_time_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^P(?!$)((\d+Y)|(\d+\.\d+Y$))?((\d+M)|(\d+\.\d+M$))?((\d+W)|(\d+\.\d+W$))?((\d+D)|(\d+\.\d+D$))?(T(?=\d)((\d+H)|(\d+\.\d+H$))?((\d+M)|(\d+\.\d+M$))?(\d+(\.\d+)?S)?)??$", value):
            raise ValueError(r"must validate the regular expression /^P(?!$)((\d+Y)|(\d+\.\d+Y$))?((\d+M)|(\d+\.\d+M$))?((\d+W)|(\d+\.\d+W$))?((\d+D)|(\d+\.\d+D$))?(T(?=\d)((\d+H)|(\d+\.\d+H$))?((\d+M)|(\d+\.\d+M$))?(\d+(\.\d+)?S)?)??$/")
        return value

    @field_validator('waiting_time')
    def waiting_time_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^P(?!$)((\d+Y)|(\d+\.\d+Y$))?((\d+M)|(\d+\.\d+M$))?((\d+W)|(\d+\.\d+W$))?((\d+D)|(\d+\.\d+D$))?(T(?=\d)((\d+H)|(\d+\.\d+H$))?((\d+M)|(\d+\.\d+M$))?(\d+(\.\d+)?S)?)??$", value):
            raise ValueError(r"must validate the regular expression /^P(?!$)((\d+Y)|(\d+\.\d+Y$))?((\d+M)|(\d+\.\d+M$))?((\d+W)|(\d+\.\d+W$))?((\d+D)|(\d+\.\d+D$))?(T(?=\d)((\d+H)|(\d+\.\d+H$))?((\d+M)|(\d+\.\d+M$))?(\d+(\.\d+)?S)?)??$/")
        return value

    @field_validator('calculation_time')
    def calculation_time_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^P(?!$)((\d+Y)|(\d+\.\d+Y$))?((\d+M)|(\d+\.\d+M$))?((\d+W)|(\d+\.\d+W$))?((\d+D)|(\d+\.\d+D$))?(T(?=\d)((\d+H)|(\d+\.\d+H$))?((\d+M)|(\d+\.\d+M$))?(\d+(\.\d+)?S)?)??$", value):
            raise ValueError(r"must validate the regular expression /^P(?!$)((\d+Y)|(\d+\.\d+Y$))?((\d+M)|(\d+\.\d+M$))?((\d+W)|(\d+\.\d+W$))?((\d+D)|(\d+\.\d+D$))?(T(?=\d)((\d+H)|(\d+\.\d+H$))?((\d+M)|(\d+\.\d+M$))?(\d+(\.\d+)?S)?)??$/")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of CalculationInfo from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * Fields in `self.additional_properties` are added to the output dict.
        """
        excluded_fields: Set[str] = set([
            "additional_properties",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        # set to None if message (nullable) is None
        # and model_fields_set contains the field
        if self.message is None and "message" in self.model_fields_set:
            _dict['message'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CalculationInfo from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "status": obj.get("status"),
            "message": obj.get("message"),
            "result_version": obj.get("result_version"),
            "preparing_time": obj.get("preparing_time") if obj.get("preparing_time") is not None else 'PT0S',
            "business_validation_time": obj.get("business_validation_time") if obj.get("business_validation_time") is not None else 'PT0S',
            "math_validation_time": obj.get("math_validation_time") if obj.get("math_validation_time") is not None else 'PT0S',
            "waiting_time": obj.get("waiting_time") if obj.get("waiting_time") is not None else 'PT0S',
            "calculation_time": obj.get("calculation_time") if obj.get("calculation_time") is not None else 'PT0S'
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


