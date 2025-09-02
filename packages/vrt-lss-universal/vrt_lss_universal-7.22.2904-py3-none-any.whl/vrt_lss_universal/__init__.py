# coding: utf-8

# flake8: noqa

"""
    VRt.Universal [UV]

    # Description  Software interface for universal trip planning.  ## Features  * Ability to pick up cargo from any location * Possibility of unloading in any location * Pair orders of several types: `PICKUP` (loading), `DROP` (unloading) * Single requests of several types: `DROP_FROM_BOX` (unloading cargo that is already in the body), `PICKUP_TO_BOX` (cargo pickup into the body without subsequent unloading), `WORK` (working at the location without moving the cargo) * A complex order can consist of any number of orders of any type * Transport and performers are divided into different entities, when planning, the optimal assignment of the performer to the transport occurs * The transport has several boxes - each of which can accommodate cargo and has its own characteristics * Accounting for the compatibility of cargo with transport in terms of cargo dimensions (length, width, height, additional capacity parameters) * Taking into account the compatibility of the cargo-box of transport (the ability to take into account the features of the box: refrigerator, thermal bag, fasteners, etc.) * Substitute applications, i.e. the ability to execute one of the substitute applications, the choice of which is based on its geographic location and time window  ## Restrictions support  **Performer** restrictions:  * Start/finish location * Accounting for the performer's way to the transport location * Performer's availability schedule is a list of time windows when the performer can move and work on locations * The maximum duration of the performer's work during the specified time period  **Transport** restrictions:  * Start/finish location * Transport availability schedule is a list of time windows when the transport is available * The maximum route distance * Several boxes in the transport, each with its own parameters * Capacity upper limit (weight, volume, number of orders, number of demands)  **Order** restrictions:  * Strict time windows * Ability to specify different valid time windows for a location and time windows to fulfil the desired demand * Accounting for the requests fulfillment order within the route * A list of desired time windows with different associated costs  ## Compatibilities  Entities are compatible if the capabilities list of one entity corresponds to the list of restrictions of another entity (example: fleet parameters corresponds to cargo parameters to be delivered).  Supported compatibilities:  | Name                    | Restrictions                     | Features                     | |-------------------------|----------------------------------|------------------------------| | Order - Performer       | order.performer_restrictions     | performer.performer_features | | Order - Not a performer | order.performer_blacklist        | performer.performer_features | | Cargo - Box             | order.cargo.box_restrictions     | transport.box.box_features   | | Location - Transport    | location.transport_restrictions  | transport.transport_features | | Transport - Performer   | transport.performer_restrictions | performer.performer_features | | Performer - Transport   | performer.transport_restrictions | transport.transport_features | | Order - Order           | order.order_restrictions         | order.order_features         |  Business rule examples:  | Name                    | Business rule example                                                                       | |-------------------------|---------------------------------------------------------------------------------------------| | Order - Performer       | The driver must have a special license to fulfil the order                                  | | Order - Not a performer | The driver is in the blacklist                                                              | | Cargo - Box             | For transportation of frozen products, a box with a special temperature profile is required | | Location - Transport    | Restrictions on the transport height                                                        | | Transport - Performer   | The truck driver must have the class C driving license                                      | | Performer - Transport   | The driver is allowed to work on a specific transport                                       | | Order - Order           | It is not allowed to transport fish and fruits in the same box                              |  ## Cargo placement  List of possibilities of a object rotations (90 degree step):  * `ALL` - can rotate by any axis * `YAW` - can yaw * `PITCH` - can pitch * `ROLL` - can roll    ![rotation](../images/universal_cargo_yaw_pitch_roll.svg)  ## Trip model  A trip is described by a list of states of the performer, while at the same time the performer can be in several states (for example, being inside the working time window of a location and fulfilling an order at the same location).  The meanings of the flags responsible for the geographical location:  * `AROUND_LOCATION` - the performer is located near the location - in the process of parking or leaving it. * `INSIDE_LOCATION` - the performer is located at the location.  The values ​​of the flags responsible for being in time windows:  * `INSIDE_WORKING_WINDOW` - the performer is inside the working time window. * `INSIDE_LOCATION_WINDOW` - the performer is located inside the location's operating time. * `INSIDE_EVENT_HARD_WINDOW` - the performer is inside a hard time window. * `INSIDE_EVENT_SOFT_WINDOW` - the performer is inside a soft time window.  The values ​​of the flags responsible for the actions:  * `ON_DEMAND` - the performer is working on the request. * `WAITING` - the performer is in standby mode. * `RELOCATING` - the performer moves to the next stop. * `BREAK` - the performer is on a break. * `REST` - the performer is on a long vacation.  Flag values ​​responsible for the logical state:  * `DURING_ROUNDTRIP` - the executor is performing a roundtrip.  ### An example of a route with multiple states at each point in time  | time  | set of active flags                                                                                                                                                          | location / order / application / event | comment                                                                                        | |:------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------|:-----------------------------------------------------------------------------------------------| | 10:00 | INSIDE_LOCATION <br/> AROUND_LOCATION                                                                                                                                        | 2 / - / - / -                          | starting location                                                                              | | 10:10 | RELOCATING                                                                                                                                                                   | - / - / - / -                          | we go to the first order                                                                       | | 10:20 | AROUND_LOCATION                                                                                                                                                              | 2 / - / - / -                          | arrived at the first order                                                                     | | 10:40 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> WAITING                                                                                                                          | 2 / - / - / -                          | parked                                                                                         | | 11:00 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> WAITING <br/> INSIDE_EVENT_HARD_WINDOW                                                              | 2 / - / - / -                          | waited for the start of the location window and at the same time the availability of the order | | 11:25 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> ON_DEMAND <br/> INSIDE_WORKING_WINDOW <br/> INSIDE_EVENT_HARD_WINDOW                                | 2 / 1 / 2 / 3                          | waited for the change of artist                                                                | | 11:30 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> ON_DEMAND <br/> INSIDE_WORKING_WINDOW <br/> INSIDE_EVENT_HARD_WINDOW <br/> INSIDE_EVENT_SOFT_WINDOW | 2 / 1 / 2 / 3                          | while working - a soft window happened                                                         | | 11:40 | AROUND_LOCATION <br/> INSIDE_LOCATION <br/> INSIDE_LOCATION_WINDOW <br/> INSIDE_WORKING_WINDOW                                                                               | 2 / - / - / -                          | finished working                                                                               | | 11:45 | AROUND_LOCATION <br/> INSIDE_WORKING_WINDOW                                                                                                                                  | 2 / - / - / -                          | drove out of the parking lot                                                                   | | 11:45 | RELOCATING <br/> INSIDE_WORKING_WINDOW                                                                                                                                       | - / - / - / -                          | we go to the next order                                                                        |  ## Roundtrips  A trip consists of one or more round trips.  The flag of the presence of a round trip `DURING_ROUNDTRIP` is set when the work on the request starts and is removed in one of three cases:  * the executor arrived at the next location to stop using transport * the executor arrived at the location separating round trips * the executor stopped using transport (in a location not separating round trips, after performing some other action)  Between the end of one round trip and the beginning of another round trip, a change of location `RELOCATING` cannot occur, but the following can occur: waiting `WAITING`, a break for the executor `BREAK`, a rest for the executor `REST`.  Locations dividing a trip into round trips are defined as follows:  * if the location has a capacity limitation `timetable.limits` (in this case, there may be more than one location dividing the trip) * if the location is simultaneously the starting and ending location of all performers and transports, as well as all requests with the `PICKUP` type (in this case, there will be only one location dividing the trip)  Examples of such locations, depending on the task formulation, can be:  * distribution centers when delivering goods to stores or warehouses in long-haul transportation tasks * stores or warehouses when delivering goods to customers in last-mile tasks * landfills in garbage collection tasks  ## Planning configuration  For each planning, it is possible to specify a planning configuration that defines the objective function, the desired quality of the routes, and the calculation speed.  The name of the scheduling configuration is passed in the `trips_settings.configuration` field.  Main configurations:  | Title                           | Task                                                                                                                                                   | |---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------| | **optimize_distance**           | Arrange as many orders as possible, then optimize the total mileage (the number of vehicles is selected based on the mileage), used by default         | | **optimize_transports**         | Place as many orders as possible, while using as little transport as possible, ceteris paribus, optimize the work time of performers                   | | **optimize_locality_grouping**  | Place as many orders as possible, while striving to optimize the visual grouping of routes, but not their number                                       | | **optimize_cars_then_distance** | Arrange as many orders as possible, then optimize the number of vehicles, then the mileage                                                             | | **optimize_time**               | Place as many orders as possible, then optimize the total work time of performers                                                                      | | **optimize_cars_then_time**     | Arrange as many orders as possible, then optimize the number of transport, then the total time of the performers                                       | | **optimize_money**              | Optimize the value of \"profit - costs\", consists of rewards for applications and costs for performers and transports (optimized value is non-negative) |  Additional configurations:  | Title                                                     | Task                                                                                                                                                                                            | |-----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| | **visual_grouping**                                       | Arrange as many orders as possible while using as little transport as possible and routes should be visually grouped                                                                            | | **optimize_visual_grouping**                              | Arrange as many orders as possible, then evenly distribute orders taking into account transport accessibility zones (similar to visual_grouping, but visual grouping is calculated differently) | | **optimize_cars_then_locality_grouping**                  | Arrange as many orders as possible, then optimize the number of vehicles, then visually group the routes                                                                                        | | **optimize_cars_then_single_location_grouping_sequenced** | Place as many orders as possible, then optimize the number of machines, then reliability                                                                                                        |  In addition to the existing planning options, it is possible to create an objective function directly for the client's business processes ([request configuration](mailto:servicedesk@veeroute.com)).  For development, it is recommended to use **optimize_cars_then_distance**, since this configuration does not require detailed selection of rates and order values.  ## Data validation  Input data validation consists of several steps, which are described below.  Validation of planning results (including the search for possible reasons why orders were not planned) is located in the `analytics` method.  ### 1. Schema check  If the request does not follow the schema, then scheduling is not fully started and such an error is returned along with a 400 code in `schema_errors`.  We recommend validating the request against the schema (or yaml file) before sending it to the server.  ### 2. Check for logical errors that prevent planning from continuing  Schema-correct data passes the second stage of checking for the possibility of starting planning.  An example of errors at this stage are keys leading to empty entities, or if all orders are incompatible with all performers, i.e. something that makes the planning task pointless.  These errors are returned along with a 400 code in `logical_errors`.  ### 3. Check for logical errors that prevent planning from continuing  At the third stage, each entity is checked separately.  All entities that have not passed validation are cut out from the original task and are not sent for planning.  Depending on the setting of `treat_warnings_as_errors`, the results of this type of validation are returned to `warnings` either with a 400 code or with the scheduling result.  ### 4. Checks in the planning process  Part of the checks can only be carried out in the planning process.  For example - that according to the specified tariffs and according to the current traffic forecast, it is physically impossible to reach a certain point.  The results of these checks are returned in `warnings` or together with the scheduling result.  ## Entity relationship diagram  ![erd](../uml/universal.svg) 

    The version of the OpenAPI document: 7.22.2904
    Contact: servicedesk@veeroute.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "7.22.2904"

# Define package exports
__all__ = [
    "ActualizeApi",
    "ConvertApi",
    "PlanApi",
    "ReplanApi",
    "SystemApi",
    "ApiResponse",
    "ApiClient",
    "Configuration",
    "OpenApiException",
    "ApiTypeError",
    "ApiValueError",
    "ApiKeyError",
    "ApiAttributeError",
    "ApiException",
    "ActualizeSettings",
    "ActualizeTask",
    "AssignedPerformer",
    "AssignedTransport",
    "Attribute",
    "Box",
    "BoxCompatibilities",
    "BoxLimits",
    "BreakRules",
    "CalculationAsyncResult",
    "CalculationInfo",
    "CalculationSettings",
    "CalculationState",
    "CalculationStatus",
    "Capacity",
    "CapacityCost",
    "CapacityLimit",
    "CapacityMultiplier",
    "CapacityStatisticsLoad",
    "CapacityStatisticsRatio",
    "CapacityStatisticsSum",
    "Cargo",
    "CargoAction",
    "CargoActionType",
    "CargoCompatibilities",
    "CargoRotationType",
    "CheckResult",
    "CompatibilityPenalty",
    "Custom400WithErrorsAndWarnings",
    "Demand",
    "DemandExtraDuration",
    "DemandType",
    "EntityError",
    "EntityErrorType",
    "EntityPath",
    "EntityType",
    "EntityWarning",
    "EntityWarningType",
    "ExtensionSettings",
    "Fact",
    "FactType",
    "FeatureLifetime",
    "General402",
    "General403",
    "General404",
    "General404Detail",
    "General429",
    "General500",
    "GeneralStatistics",
    "GeoSettings",
    "Geopoint",
    "Hardlink",
    "HardlinkElement",
    "HardlinkElementType",
    "LoadStatistics",
    "Location",
    "LocationCargosLimit",
    "LocationCompatibilities",
    "LocationLimit",
    "LocationLimitStatistics",
    "LocationStatistics",
    "LocationTimetableElement",
    "LocationTransportsLimit",
    "Measurements",
    "ModelBreak",
    "Order",
    "OrderCompatibilities",
    "Performer",
    "PerformerCompatibilities",
    "PerformerLimits",
    "PerformerShift",
    "PerformerTariff",
    "PerformerTariffConstraint",
    "PlanResult",
    "PlanSettings",
    "PlanStatistics",
    "PlanTask",
    "PossibleEvent",
    "Quality",
    "RefineResult",
    "RemovedItems",
    "ReplanSettings",
    "ReplanStrategy",
    "ReplanTask",
    "Rest",
    "RestRules",
    "RoundtripStatistics",
    "RoutingMatrix",
    "RoutingMatrixWaypoint",
    "RoutingTransportMatrix",
    "SchemaError",
    "Service",
    "StatisticsTask",
    "StopDemand",
    "StopStatistics",
    "TaskStatistics",
    "TimeWindow",
    "TimeWindowViolationDetail",
    "TimeWindowViolations",
    "Tracedata",
    "Transport",
    "TransportCapacityMultiplier",
    "TransportCompatibilities",
    "TransportLimits",
    "TransportLoad",
    "TransportShift",
    "TransportSpeedMultiplier",
    "TransportTariff",
    "TransportTariffConstraint",
    "TransportType",
    "Trip",
    "TripAssumptions",
    "TripExpectations",
    "TripPenalties",
    "TripStartTimeStrategy",
    "TripState",
    "TripStateFlag",
    "TripStatistics",
    "TripsSettings",
    "UniversalData",
    "UnplannedItems",
    "ValidateResult",
    "VersionResult",
    "WorkAndRestRules",
]

if __import__("typing").TYPE_CHECKING:
    # import apis into sdk package
    from vrt_lss_universal.api.actualize_api import ActualizeApi as ActualizeApi
    from vrt_lss_universal.api.convert_api import ConvertApi as ConvertApi
    from vrt_lss_universal.api.plan_api import PlanApi as PlanApi
    from vrt_lss_universal.api.replan_api import ReplanApi as ReplanApi
    from vrt_lss_universal.api.system_api import SystemApi as SystemApi
    
    # import ApiClient
    from vrt_lss_universal.api_response import ApiResponse as ApiResponse
    from vrt_lss_universal.api_client import ApiClient as ApiClient
    from vrt_lss_universal.configuration import Configuration as Configuration
    from vrt_lss_universal.exceptions import OpenApiException as OpenApiException
    from vrt_lss_universal.exceptions import ApiTypeError as ApiTypeError
    from vrt_lss_universal.exceptions import ApiValueError as ApiValueError
    from vrt_lss_universal.exceptions import ApiKeyError as ApiKeyError
    from vrt_lss_universal.exceptions import ApiAttributeError as ApiAttributeError
    from vrt_lss_universal.exceptions import ApiException as ApiException
    
    # import models into sdk package
    from vrt_lss_universal.models.actualize_settings import ActualizeSettings as ActualizeSettings
    from vrt_lss_universal.models.actualize_task import ActualizeTask as ActualizeTask
    from vrt_lss_universal.models.assigned_performer import AssignedPerformer as AssignedPerformer
    from vrt_lss_universal.models.assigned_transport import AssignedTransport as AssignedTransport
    from vrt_lss_universal.models.attribute import Attribute as Attribute
    from vrt_lss_universal.models.box import Box as Box
    from vrt_lss_universal.models.box_compatibilities import BoxCompatibilities as BoxCompatibilities
    from vrt_lss_universal.models.box_limits import BoxLimits as BoxLimits
    from vrt_lss_universal.models.break_rules import BreakRules as BreakRules
    from vrt_lss_universal.models.calculation_async_result import CalculationAsyncResult as CalculationAsyncResult
    from vrt_lss_universal.models.calculation_info import CalculationInfo as CalculationInfo
    from vrt_lss_universal.models.calculation_settings import CalculationSettings as CalculationSettings
    from vrt_lss_universal.models.calculation_state import CalculationState as CalculationState
    from vrt_lss_universal.models.calculation_status import CalculationStatus as CalculationStatus
    from vrt_lss_universal.models.capacity import Capacity as Capacity
    from vrt_lss_universal.models.capacity_cost import CapacityCost as CapacityCost
    from vrt_lss_universal.models.capacity_limit import CapacityLimit as CapacityLimit
    from vrt_lss_universal.models.capacity_multiplier import CapacityMultiplier as CapacityMultiplier
    from vrt_lss_universal.models.capacity_statistics_load import CapacityStatisticsLoad as CapacityStatisticsLoad
    from vrt_lss_universal.models.capacity_statistics_ratio import CapacityStatisticsRatio as CapacityStatisticsRatio
    from vrt_lss_universal.models.capacity_statistics_sum import CapacityStatisticsSum as CapacityStatisticsSum
    from vrt_lss_universal.models.cargo import Cargo as Cargo
    from vrt_lss_universal.models.cargo_action import CargoAction as CargoAction
    from vrt_lss_universal.models.cargo_action_type import CargoActionType as CargoActionType
    from vrt_lss_universal.models.cargo_compatibilities import CargoCompatibilities as CargoCompatibilities
    from vrt_lss_universal.models.cargo_rotation_type import CargoRotationType as CargoRotationType
    from vrt_lss_universal.models.check_result import CheckResult as CheckResult
    from vrt_lss_universal.models.compatibility_penalty import CompatibilityPenalty as CompatibilityPenalty
    from vrt_lss_universal.models.custom400_with_errors_and_warnings import Custom400WithErrorsAndWarnings as Custom400WithErrorsAndWarnings
    from vrt_lss_universal.models.demand import Demand as Demand
    from vrt_lss_universal.models.demand_extra_duration import DemandExtraDuration as DemandExtraDuration
    from vrt_lss_universal.models.demand_type import DemandType as DemandType
    from vrt_lss_universal.models.entity_error import EntityError as EntityError
    from vrt_lss_universal.models.entity_error_type import EntityErrorType as EntityErrorType
    from vrt_lss_universal.models.entity_path import EntityPath as EntityPath
    from vrt_lss_universal.models.entity_type import EntityType as EntityType
    from vrt_lss_universal.models.entity_warning import EntityWarning as EntityWarning
    from vrt_lss_universal.models.entity_warning_type import EntityWarningType as EntityWarningType
    from vrt_lss_universal.models.extension_settings import ExtensionSettings as ExtensionSettings
    from vrt_lss_universal.models.fact import Fact as Fact
    from vrt_lss_universal.models.fact_type import FactType as FactType
    from vrt_lss_universal.models.feature_lifetime import FeatureLifetime as FeatureLifetime
    from vrt_lss_universal.models.general402 import General402 as General402
    from vrt_lss_universal.models.general403 import General403 as General403
    from vrt_lss_universal.models.general404 import General404 as General404
    from vrt_lss_universal.models.general404_detail import General404Detail as General404Detail
    from vrt_lss_universal.models.general429 import General429 as General429
    from vrt_lss_universal.models.general500 import General500 as General500
    from vrt_lss_universal.models.general_statistics import GeneralStatistics as GeneralStatistics
    from vrt_lss_universal.models.geo_settings import GeoSettings as GeoSettings
    from vrt_lss_universal.models.geopoint import Geopoint as Geopoint
    from vrt_lss_universal.models.hardlink import Hardlink as Hardlink
    from vrt_lss_universal.models.hardlink_element import HardlinkElement as HardlinkElement
    from vrt_lss_universal.models.hardlink_element_type import HardlinkElementType as HardlinkElementType
    from vrt_lss_universal.models.load_statistics import LoadStatistics as LoadStatistics
    from vrt_lss_universal.models.location import Location as Location
    from vrt_lss_universal.models.location_cargos_limit import LocationCargosLimit as LocationCargosLimit
    from vrt_lss_universal.models.location_compatibilities import LocationCompatibilities as LocationCompatibilities
    from vrt_lss_universal.models.location_limit import LocationLimit as LocationLimit
    from vrt_lss_universal.models.location_limit_statistics import LocationLimitStatistics as LocationLimitStatistics
    from vrt_lss_universal.models.location_statistics import LocationStatistics as LocationStatistics
    from vrt_lss_universal.models.location_timetable_element import LocationTimetableElement as LocationTimetableElement
    from vrt_lss_universal.models.location_transports_limit import LocationTransportsLimit as LocationTransportsLimit
    from vrt_lss_universal.models.measurements import Measurements as Measurements
    from vrt_lss_universal.models.model_break import ModelBreak as ModelBreak
    from vrt_lss_universal.models.order import Order as Order
    from vrt_lss_universal.models.order_compatibilities import OrderCompatibilities as OrderCompatibilities
    from vrt_lss_universal.models.performer import Performer as Performer
    from vrt_lss_universal.models.performer_compatibilities import PerformerCompatibilities as PerformerCompatibilities
    from vrt_lss_universal.models.performer_limits import PerformerLimits as PerformerLimits
    from vrt_lss_universal.models.performer_shift import PerformerShift as PerformerShift
    from vrt_lss_universal.models.performer_tariff import PerformerTariff as PerformerTariff
    from vrt_lss_universal.models.performer_tariff_constraint import PerformerTariffConstraint as PerformerTariffConstraint
    from vrt_lss_universal.models.plan_result import PlanResult as PlanResult
    from vrt_lss_universal.models.plan_settings import PlanSettings as PlanSettings
    from vrt_lss_universal.models.plan_statistics import PlanStatistics as PlanStatistics
    from vrt_lss_universal.models.plan_task import PlanTask as PlanTask
    from vrt_lss_universal.models.possible_event import PossibleEvent as PossibleEvent
    from vrt_lss_universal.models.quality import Quality as Quality
    from vrt_lss_universal.models.refine_result import RefineResult as RefineResult
    from vrt_lss_universal.models.removed_items import RemovedItems as RemovedItems
    from vrt_lss_universal.models.replan_settings import ReplanSettings as ReplanSettings
    from vrt_lss_universal.models.replan_strategy import ReplanStrategy as ReplanStrategy
    from vrt_lss_universal.models.replan_task import ReplanTask as ReplanTask
    from vrt_lss_universal.models.rest import Rest as Rest
    from vrt_lss_universal.models.rest_rules import RestRules as RestRules
    from vrt_lss_universal.models.roundtrip_statistics import RoundtripStatistics as RoundtripStatistics
    from vrt_lss_universal.models.routing_matrix import RoutingMatrix as RoutingMatrix
    from vrt_lss_universal.models.routing_matrix_waypoint import RoutingMatrixWaypoint as RoutingMatrixWaypoint
    from vrt_lss_universal.models.routing_transport_matrix import RoutingTransportMatrix as RoutingTransportMatrix
    from vrt_lss_universal.models.schema_error import SchemaError as SchemaError
    from vrt_lss_universal.models.service import Service as Service
    from vrt_lss_universal.models.statistics_task import StatisticsTask as StatisticsTask
    from vrt_lss_universal.models.stop_demand import StopDemand as StopDemand
    from vrt_lss_universal.models.stop_statistics import StopStatistics as StopStatistics
    from vrt_lss_universal.models.task_statistics import TaskStatistics as TaskStatistics
    from vrt_lss_universal.models.time_window import TimeWindow as TimeWindow
    from vrt_lss_universal.models.time_window_violation_detail import TimeWindowViolationDetail as TimeWindowViolationDetail
    from vrt_lss_universal.models.time_window_violations import TimeWindowViolations as TimeWindowViolations
    from vrt_lss_universal.models.tracedata import Tracedata as Tracedata
    from vrt_lss_universal.models.transport import Transport as Transport
    from vrt_lss_universal.models.transport_capacity_multiplier import TransportCapacityMultiplier as TransportCapacityMultiplier
    from vrt_lss_universal.models.transport_compatibilities import TransportCompatibilities as TransportCompatibilities
    from vrt_lss_universal.models.transport_limits import TransportLimits as TransportLimits
    from vrt_lss_universal.models.transport_load import TransportLoad as TransportLoad
    from vrt_lss_universal.models.transport_shift import TransportShift as TransportShift
    from vrt_lss_universal.models.transport_speed_multiplier import TransportSpeedMultiplier as TransportSpeedMultiplier
    from vrt_lss_universal.models.transport_tariff import TransportTariff as TransportTariff
    from vrt_lss_universal.models.transport_tariff_constraint import TransportTariffConstraint as TransportTariffConstraint
    from vrt_lss_universal.models.transport_type import TransportType as TransportType
    from vrt_lss_universal.models.trip import Trip as Trip
    from vrt_lss_universal.models.trip_assumptions import TripAssumptions as TripAssumptions
    from vrt_lss_universal.models.trip_expectations import TripExpectations as TripExpectations
    from vrt_lss_universal.models.trip_penalties import TripPenalties as TripPenalties
    from vrt_lss_universal.models.trip_start_time_strategy import TripStartTimeStrategy as TripStartTimeStrategy
    from vrt_lss_universal.models.trip_state import TripState as TripState
    from vrt_lss_universal.models.trip_state_flag import TripStateFlag as TripStateFlag
    from vrt_lss_universal.models.trip_statistics import TripStatistics as TripStatistics
    from vrt_lss_universal.models.trips_settings import TripsSettings as TripsSettings
    from vrt_lss_universal.models.universal_data import UniversalData as UniversalData
    from vrt_lss_universal.models.unplanned_items import UnplannedItems as UnplannedItems
    from vrt_lss_universal.models.validate_result import ValidateResult as ValidateResult
    from vrt_lss_universal.models.version_result import VersionResult as VersionResult
    from vrt_lss_universal.models.work_and_rest_rules import WorkAndRestRules as WorkAndRestRules
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            ("__version__", __version__),
            ("__all__", __all__),
            """# import apis into sdk package
from vrt_lss_universal.api.actualize_api import ActualizeApi as ActualizeApi
from vrt_lss_universal.api.convert_api import ConvertApi as ConvertApi
from vrt_lss_universal.api.plan_api import PlanApi as PlanApi
from vrt_lss_universal.api.replan_api import ReplanApi as ReplanApi
from vrt_lss_universal.api.system_api import SystemApi as SystemApi

# import ApiClient
from vrt_lss_universal.api_response import ApiResponse as ApiResponse
from vrt_lss_universal.api_client import ApiClient as ApiClient
from vrt_lss_universal.configuration import Configuration as Configuration
from vrt_lss_universal.exceptions import OpenApiException as OpenApiException
from vrt_lss_universal.exceptions import ApiTypeError as ApiTypeError
from vrt_lss_universal.exceptions import ApiValueError as ApiValueError
from vrt_lss_universal.exceptions import ApiKeyError as ApiKeyError
from vrt_lss_universal.exceptions import ApiAttributeError as ApiAttributeError
from vrt_lss_universal.exceptions import ApiException as ApiException

# import models into sdk package
from vrt_lss_universal.models.actualize_settings import ActualizeSettings as ActualizeSettings
from vrt_lss_universal.models.actualize_task import ActualizeTask as ActualizeTask
from vrt_lss_universal.models.assigned_performer import AssignedPerformer as AssignedPerformer
from vrt_lss_universal.models.assigned_transport import AssignedTransport as AssignedTransport
from vrt_lss_universal.models.attribute import Attribute as Attribute
from vrt_lss_universal.models.box import Box as Box
from vrt_lss_universal.models.box_compatibilities import BoxCompatibilities as BoxCompatibilities
from vrt_lss_universal.models.box_limits import BoxLimits as BoxLimits
from vrt_lss_universal.models.break_rules import BreakRules as BreakRules
from vrt_lss_universal.models.calculation_async_result import CalculationAsyncResult as CalculationAsyncResult
from vrt_lss_universal.models.calculation_info import CalculationInfo as CalculationInfo
from vrt_lss_universal.models.calculation_settings import CalculationSettings as CalculationSettings
from vrt_lss_universal.models.calculation_state import CalculationState as CalculationState
from vrt_lss_universal.models.calculation_status import CalculationStatus as CalculationStatus
from vrt_lss_universal.models.capacity import Capacity as Capacity
from vrt_lss_universal.models.capacity_cost import CapacityCost as CapacityCost
from vrt_lss_universal.models.capacity_limit import CapacityLimit as CapacityLimit
from vrt_lss_universal.models.capacity_multiplier import CapacityMultiplier as CapacityMultiplier
from vrt_lss_universal.models.capacity_statistics_load import CapacityStatisticsLoad as CapacityStatisticsLoad
from vrt_lss_universal.models.capacity_statistics_ratio import CapacityStatisticsRatio as CapacityStatisticsRatio
from vrt_lss_universal.models.capacity_statistics_sum import CapacityStatisticsSum as CapacityStatisticsSum
from vrt_lss_universal.models.cargo import Cargo as Cargo
from vrt_lss_universal.models.cargo_action import CargoAction as CargoAction
from vrt_lss_universal.models.cargo_action_type import CargoActionType as CargoActionType
from vrt_lss_universal.models.cargo_compatibilities import CargoCompatibilities as CargoCompatibilities
from vrt_lss_universal.models.cargo_rotation_type import CargoRotationType as CargoRotationType
from vrt_lss_universal.models.check_result import CheckResult as CheckResult
from vrt_lss_universal.models.compatibility_penalty import CompatibilityPenalty as CompatibilityPenalty
from vrt_lss_universal.models.custom400_with_errors_and_warnings import Custom400WithErrorsAndWarnings as Custom400WithErrorsAndWarnings
from vrt_lss_universal.models.demand import Demand as Demand
from vrt_lss_universal.models.demand_extra_duration import DemandExtraDuration as DemandExtraDuration
from vrt_lss_universal.models.demand_type import DemandType as DemandType
from vrt_lss_universal.models.entity_error import EntityError as EntityError
from vrt_lss_universal.models.entity_error_type import EntityErrorType as EntityErrorType
from vrt_lss_universal.models.entity_path import EntityPath as EntityPath
from vrt_lss_universal.models.entity_type import EntityType as EntityType
from vrt_lss_universal.models.entity_warning import EntityWarning as EntityWarning
from vrt_lss_universal.models.entity_warning_type import EntityWarningType as EntityWarningType
from vrt_lss_universal.models.extension_settings import ExtensionSettings as ExtensionSettings
from vrt_lss_universal.models.fact import Fact as Fact
from vrt_lss_universal.models.fact_type import FactType as FactType
from vrt_lss_universal.models.feature_lifetime import FeatureLifetime as FeatureLifetime
from vrt_lss_universal.models.general402 import General402 as General402
from vrt_lss_universal.models.general403 import General403 as General403
from vrt_lss_universal.models.general404 import General404 as General404
from vrt_lss_universal.models.general404_detail import General404Detail as General404Detail
from vrt_lss_universal.models.general429 import General429 as General429
from vrt_lss_universal.models.general500 import General500 as General500
from vrt_lss_universal.models.general_statistics import GeneralStatistics as GeneralStatistics
from vrt_lss_universal.models.geo_settings import GeoSettings as GeoSettings
from vrt_lss_universal.models.geopoint import Geopoint as Geopoint
from vrt_lss_universal.models.hardlink import Hardlink as Hardlink
from vrt_lss_universal.models.hardlink_element import HardlinkElement as HardlinkElement
from vrt_lss_universal.models.hardlink_element_type import HardlinkElementType as HardlinkElementType
from vrt_lss_universal.models.load_statistics import LoadStatistics as LoadStatistics
from vrt_lss_universal.models.location import Location as Location
from vrt_lss_universal.models.location_cargos_limit import LocationCargosLimit as LocationCargosLimit
from vrt_lss_universal.models.location_compatibilities import LocationCompatibilities as LocationCompatibilities
from vrt_lss_universal.models.location_limit import LocationLimit as LocationLimit
from vrt_lss_universal.models.location_limit_statistics import LocationLimitStatistics as LocationLimitStatistics
from vrt_lss_universal.models.location_statistics import LocationStatistics as LocationStatistics
from vrt_lss_universal.models.location_timetable_element import LocationTimetableElement as LocationTimetableElement
from vrt_lss_universal.models.location_transports_limit import LocationTransportsLimit as LocationTransportsLimit
from vrt_lss_universal.models.measurements import Measurements as Measurements
from vrt_lss_universal.models.model_break import ModelBreak as ModelBreak
from vrt_lss_universal.models.order import Order as Order
from vrt_lss_universal.models.order_compatibilities import OrderCompatibilities as OrderCompatibilities
from vrt_lss_universal.models.performer import Performer as Performer
from vrt_lss_universal.models.performer_compatibilities import PerformerCompatibilities as PerformerCompatibilities
from vrt_lss_universal.models.performer_limits import PerformerLimits as PerformerLimits
from vrt_lss_universal.models.performer_shift import PerformerShift as PerformerShift
from vrt_lss_universal.models.performer_tariff import PerformerTariff as PerformerTariff
from vrt_lss_universal.models.performer_tariff_constraint import PerformerTariffConstraint as PerformerTariffConstraint
from vrt_lss_universal.models.plan_result import PlanResult as PlanResult
from vrt_lss_universal.models.plan_settings import PlanSettings as PlanSettings
from vrt_lss_universal.models.plan_statistics import PlanStatistics as PlanStatistics
from vrt_lss_universal.models.plan_task import PlanTask as PlanTask
from vrt_lss_universal.models.possible_event import PossibleEvent as PossibleEvent
from vrt_lss_universal.models.quality import Quality as Quality
from vrt_lss_universal.models.refine_result import RefineResult as RefineResult
from vrt_lss_universal.models.removed_items import RemovedItems as RemovedItems
from vrt_lss_universal.models.replan_settings import ReplanSettings as ReplanSettings
from vrt_lss_universal.models.replan_strategy import ReplanStrategy as ReplanStrategy
from vrt_lss_universal.models.replan_task import ReplanTask as ReplanTask
from vrt_lss_universal.models.rest import Rest as Rest
from vrt_lss_universal.models.rest_rules import RestRules as RestRules
from vrt_lss_universal.models.roundtrip_statistics import RoundtripStatistics as RoundtripStatistics
from vrt_lss_universal.models.routing_matrix import RoutingMatrix as RoutingMatrix
from vrt_lss_universal.models.routing_matrix_waypoint import RoutingMatrixWaypoint as RoutingMatrixWaypoint
from vrt_lss_universal.models.routing_transport_matrix import RoutingTransportMatrix as RoutingTransportMatrix
from vrt_lss_universal.models.schema_error import SchemaError as SchemaError
from vrt_lss_universal.models.service import Service as Service
from vrt_lss_universal.models.statistics_task import StatisticsTask as StatisticsTask
from vrt_lss_universal.models.stop_demand import StopDemand as StopDemand
from vrt_lss_universal.models.stop_statistics import StopStatistics as StopStatistics
from vrt_lss_universal.models.task_statistics import TaskStatistics as TaskStatistics
from vrt_lss_universal.models.time_window import TimeWindow as TimeWindow
from vrt_lss_universal.models.time_window_violation_detail import TimeWindowViolationDetail as TimeWindowViolationDetail
from vrt_lss_universal.models.time_window_violations import TimeWindowViolations as TimeWindowViolations
from vrt_lss_universal.models.tracedata import Tracedata as Tracedata
from vrt_lss_universal.models.transport import Transport as Transport
from vrt_lss_universal.models.transport_capacity_multiplier import TransportCapacityMultiplier as TransportCapacityMultiplier
from vrt_lss_universal.models.transport_compatibilities import TransportCompatibilities as TransportCompatibilities
from vrt_lss_universal.models.transport_limits import TransportLimits as TransportLimits
from vrt_lss_universal.models.transport_load import TransportLoad as TransportLoad
from vrt_lss_universal.models.transport_shift import TransportShift as TransportShift
from vrt_lss_universal.models.transport_speed_multiplier import TransportSpeedMultiplier as TransportSpeedMultiplier
from vrt_lss_universal.models.transport_tariff import TransportTariff as TransportTariff
from vrt_lss_universal.models.transport_tariff_constraint import TransportTariffConstraint as TransportTariffConstraint
from vrt_lss_universal.models.transport_type import TransportType as TransportType
from vrt_lss_universal.models.trip import Trip as Trip
from vrt_lss_universal.models.trip_assumptions import TripAssumptions as TripAssumptions
from vrt_lss_universal.models.trip_expectations import TripExpectations as TripExpectations
from vrt_lss_universal.models.trip_penalties import TripPenalties as TripPenalties
from vrt_lss_universal.models.trip_start_time_strategy import TripStartTimeStrategy as TripStartTimeStrategy
from vrt_lss_universal.models.trip_state import TripState as TripState
from vrt_lss_universal.models.trip_state_flag import TripStateFlag as TripStateFlag
from vrt_lss_universal.models.trip_statistics import TripStatistics as TripStatistics
from vrt_lss_universal.models.trips_settings import TripsSettings as TripsSettings
from vrt_lss_universal.models.universal_data import UniversalData as UniversalData
from vrt_lss_universal.models.unplanned_items import UnplannedItems as UnplannedItems
from vrt_lss_universal.models.validate_result import ValidateResult as ValidateResult
from vrt_lss_universal.models.version_result import VersionResult as VersionResult
from vrt_lss_universal.models.work_and_rest_rules import WorkAndRestRules as WorkAndRestRules

""",
            name=__name__,
            doc=__doc__,
        )
    )
