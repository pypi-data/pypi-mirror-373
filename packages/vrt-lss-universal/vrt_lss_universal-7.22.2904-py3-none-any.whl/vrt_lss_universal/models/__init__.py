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


if __import__("typing").TYPE_CHECKING:
    # import models into model package
    from vrt_lss_universal.models.actualize_settings import ActualizeSettings
    from vrt_lss_universal.models.actualize_task import ActualizeTask
    from vrt_lss_universal.models.assigned_performer import AssignedPerformer
    from vrt_lss_universal.models.assigned_transport import AssignedTransport
    from vrt_lss_universal.models.attribute import Attribute
    from vrt_lss_universal.models.box import Box
    from vrt_lss_universal.models.box_compatibilities import BoxCompatibilities
    from vrt_lss_universal.models.box_limits import BoxLimits
    from vrt_lss_universal.models.break_rules import BreakRules
    from vrt_lss_universal.models.calculation_async_result import CalculationAsyncResult
    from vrt_lss_universal.models.calculation_info import CalculationInfo
    from vrt_lss_universal.models.calculation_settings import CalculationSettings
    from vrt_lss_universal.models.calculation_state import CalculationState
    from vrt_lss_universal.models.calculation_status import CalculationStatus
    from vrt_lss_universal.models.capacity import Capacity
    from vrt_lss_universal.models.capacity_cost import CapacityCost
    from vrt_lss_universal.models.capacity_limit import CapacityLimit
    from vrt_lss_universal.models.capacity_multiplier import CapacityMultiplier
    from vrt_lss_universal.models.capacity_statistics_load import CapacityStatisticsLoad
    from vrt_lss_universal.models.capacity_statistics_ratio import CapacityStatisticsRatio
    from vrt_lss_universal.models.capacity_statistics_sum import CapacityStatisticsSum
    from vrt_lss_universal.models.cargo import Cargo
    from vrt_lss_universal.models.cargo_action import CargoAction
    from vrt_lss_universal.models.cargo_action_type import CargoActionType
    from vrt_lss_universal.models.cargo_compatibilities import CargoCompatibilities
    from vrt_lss_universal.models.cargo_rotation_type import CargoRotationType
    from vrt_lss_universal.models.check_result import CheckResult
    from vrt_lss_universal.models.compatibility_penalty import CompatibilityPenalty
    from vrt_lss_universal.models.custom400_with_errors_and_warnings import Custom400WithErrorsAndWarnings
    from vrt_lss_universal.models.demand import Demand
    from vrt_lss_universal.models.demand_extra_duration import DemandExtraDuration
    from vrt_lss_universal.models.demand_type import DemandType
    from vrt_lss_universal.models.entity_error import EntityError
    from vrt_lss_universal.models.entity_error_type import EntityErrorType
    from vrt_lss_universal.models.entity_path import EntityPath
    from vrt_lss_universal.models.entity_type import EntityType
    from vrt_lss_universal.models.entity_warning import EntityWarning
    from vrt_lss_universal.models.entity_warning_type import EntityWarningType
    from vrt_lss_universal.models.extension_settings import ExtensionSettings
    from vrt_lss_universal.models.fact import Fact
    from vrt_lss_universal.models.fact_type import FactType
    from vrt_lss_universal.models.feature_lifetime import FeatureLifetime
    from vrt_lss_universal.models.general402 import General402
    from vrt_lss_universal.models.general403 import General403
    from vrt_lss_universal.models.general404 import General404
    from vrt_lss_universal.models.general404_detail import General404Detail
    from vrt_lss_universal.models.general429 import General429
    from vrt_lss_universal.models.general500 import General500
    from vrt_lss_universal.models.general_statistics import GeneralStatistics
    from vrt_lss_universal.models.geo_settings import GeoSettings
    from vrt_lss_universal.models.geopoint import Geopoint
    from vrt_lss_universal.models.hardlink import Hardlink
    from vrt_lss_universal.models.hardlink_element import HardlinkElement
    from vrt_lss_universal.models.hardlink_element_type import HardlinkElementType
    from vrt_lss_universal.models.load_statistics import LoadStatistics
    from vrt_lss_universal.models.location import Location
    from vrt_lss_universal.models.location_cargos_limit import LocationCargosLimit
    from vrt_lss_universal.models.location_compatibilities import LocationCompatibilities
    from vrt_lss_universal.models.location_limit import LocationLimit
    from vrt_lss_universal.models.location_limit_statistics import LocationLimitStatistics
    from vrt_lss_universal.models.location_statistics import LocationStatistics
    from vrt_lss_universal.models.location_timetable_element import LocationTimetableElement
    from vrt_lss_universal.models.location_transports_limit import LocationTransportsLimit
    from vrt_lss_universal.models.measurements import Measurements
    from vrt_lss_universal.models.model_break import ModelBreak
    from vrt_lss_universal.models.order import Order
    from vrt_lss_universal.models.order_compatibilities import OrderCompatibilities
    from vrt_lss_universal.models.performer import Performer
    from vrt_lss_universal.models.performer_compatibilities import PerformerCompatibilities
    from vrt_lss_universal.models.performer_limits import PerformerLimits
    from vrt_lss_universal.models.performer_shift import PerformerShift
    from vrt_lss_universal.models.performer_tariff import PerformerTariff
    from vrt_lss_universal.models.performer_tariff_constraint import PerformerTariffConstraint
    from vrt_lss_universal.models.plan_result import PlanResult
    from vrt_lss_universal.models.plan_settings import PlanSettings
    from vrt_lss_universal.models.plan_statistics import PlanStatistics
    from vrt_lss_universal.models.plan_task import PlanTask
    from vrt_lss_universal.models.possible_event import PossibleEvent
    from vrt_lss_universal.models.quality import Quality
    from vrt_lss_universal.models.refine_result import RefineResult
    from vrt_lss_universal.models.removed_items import RemovedItems
    from vrt_lss_universal.models.replan_settings import ReplanSettings
    from vrt_lss_universal.models.replan_strategy import ReplanStrategy
    from vrt_lss_universal.models.replan_task import ReplanTask
    from vrt_lss_universal.models.rest import Rest
    from vrt_lss_universal.models.rest_rules import RestRules
    from vrt_lss_universal.models.roundtrip_statistics import RoundtripStatistics
    from vrt_lss_universal.models.routing_matrix import RoutingMatrix
    from vrt_lss_universal.models.routing_matrix_waypoint import RoutingMatrixWaypoint
    from vrt_lss_universal.models.routing_transport_matrix import RoutingTransportMatrix
    from vrt_lss_universal.models.schema_error import SchemaError
    from vrt_lss_universal.models.service import Service
    from vrt_lss_universal.models.statistics_task import StatisticsTask
    from vrt_lss_universal.models.stop_demand import StopDemand
    from vrt_lss_universal.models.stop_statistics import StopStatistics
    from vrt_lss_universal.models.task_statistics import TaskStatistics
    from vrt_lss_universal.models.time_window import TimeWindow
    from vrt_lss_universal.models.time_window_violation_detail import TimeWindowViolationDetail
    from vrt_lss_universal.models.time_window_violations import TimeWindowViolations
    from vrt_lss_universal.models.tracedata import Tracedata
    from vrt_lss_universal.models.transport import Transport
    from vrt_lss_universal.models.transport_capacity_multiplier import TransportCapacityMultiplier
    from vrt_lss_universal.models.transport_compatibilities import TransportCompatibilities
    from vrt_lss_universal.models.transport_limits import TransportLimits
    from vrt_lss_universal.models.transport_load import TransportLoad
    from vrt_lss_universal.models.transport_shift import TransportShift
    from vrt_lss_universal.models.transport_speed_multiplier import TransportSpeedMultiplier
    from vrt_lss_universal.models.transport_tariff import TransportTariff
    from vrt_lss_universal.models.transport_tariff_constraint import TransportTariffConstraint
    from vrt_lss_universal.models.transport_type import TransportType
    from vrt_lss_universal.models.trip import Trip
    from vrt_lss_universal.models.trip_assumptions import TripAssumptions
    from vrt_lss_universal.models.trip_expectations import TripExpectations
    from vrt_lss_universal.models.trip_penalties import TripPenalties
    from vrt_lss_universal.models.trip_start_time_strategy import TripStartTimeStrategy
    from vrt_lss_universal.models.trip_state import TripState
    from vrt_lss_universal.models.trip_state_flag import TripStateFlag
    from vrt_lss_universal.models.trip_statistics import TripStatistics
    from vrt_lss_universal.models.trips_settings import TripsSettings
    from vrt_lss_universal.models.universal_data import UniversalData
    from vrt_lss_universal.models.unplanned_items import UnplannedItems
    from vrt_lss_universal.models.validate_result import ValidateResult
    from vrt_lss_universal.models.version_result import VersionResult
    from vrt_lss_universal.models.work_and_rest_rules import WorkAndRestRules
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import models into model package
from vrt_lss_universal.models.actualize_settings import ActualizeSettings
from vrt_lss_universal.models.actualize_task import ActualizeTask
from vrt_lss_universal.models.assigned_performer import AssignedPerformer
from vrt_lss_universal.models.assigned_transport import AssignedTransport
from vrt_lss_universal.models.attribute import Attribute
from vrt_lss_universal.models.box import Box
from vrt_lss_universal.models.box_compatibilities import BoxCompatibilities
from vrt_lss_universal.models.box_limits import BoxLimits
from vrt_lss_universal.models.break_rules import BreakRules
from vrt_lss_universal.models.calculation_async_result import CalculationAsyncResult
from vrt_lss_universal.models.calculation_info import CalculationInfo
from vrt_lss_universal.models.calculation_settings import CalculationSettings
from vrt_lss_universal.models.calculation_state import CalculationState
from vrt_lss_universal.models.calculation_status import CalculationStatus
from vrt_lss_universal.models.capacity import Capacity
from vrt_lss_universal.models.capacity_cost import CapacityCost
from vrt_lss_universal.models.capacity_limit import CapacityLimit
from vrt_lss_universal.models.capacity_multiplier import CapacityMultiplier
from vrt_lss_universal.models.capacity_statistics_load import CapacityStatisticsLoad
from vrt_lss_universal.models.capacity_statistics_ratio import CapacityStatisticsRatio
from vrt_lss_universal.models.capacity_statistics_sum import CapacityStatisticsSum
from vrt_lss_universal.models.cargo import Cargo
from vrt_lss_universal.models.cargo_action import CargoAction
from vrt_lss_universal.models.cargo_action_type import CargoActionType
from vrt_lss_universal.models.cargo_compatibilities import CargoCompatibilities
from vrt_lss_universal.models.cargo_rotation_type import CargoRotationType
from vrt_lss_universal.models.check_result import CheckResult
from vrt_lss_universal.models.compatibility_penalty import CompatibilityPenalty
from vrt_lss_universal.models.custom400_with_errors_and_warnings import Custom400WithErrorsAndWarnings
from vrt_lss_universal.models.demand import Demand
from vrt_lss_universal.models.demand_extra_duration import DemandExtraDuration
from vrt_lss_universal.models.demand_type import DemandType
from vrt_lss_universal.models.entity_error import EntityError
from vrt_lss_universal.models.entity_error_type import EntityErrorType
from vrt_lss_universal.models.entity_path import EntityPath
from vrt_lss_universal.models.entity_type import EntityType
from vrt_lss_universal.models.entity_warning import EntityWarning
from vrt_lss_universal.models.entity_warning_type import EntityWarningType
from vrt_lss_universal.models.extension_settings import ExtensionSettings
from vrt_lss_universal.models.fact import Fact
from vrt_lss_universal.models.fact_type import FactType
from vrt_lss_universal.models.feature_lifetime import FeatureLifetime
from vrt_lss_universal.models.general402 import General402
from vrt_lss_universal.models.general403 import General403
from vrt_lss_universal.models.general404 import General404
from vrt_lss_universal.models.general404_detail import General404Detail
from vrt_lss_universal.models.general429 import General429
from vrt_lss_universal.models.general500 import General500
from vrt_lss_universal.models.general_statistics import GeneralStatistics
from vrt_lss_universal.models.geo_settings import GeoSettings
from vrt_lss_universal.models.geopoint import Geopoint
from vrt_lss_universal.models.hardlink import Hardlink
from vrt_lss_universal.models.hardlink_element import HardlinkElement
from vrt_lss_universal.models.hardlink_element_type import HardlinkElementType
from vrt_lss_universal.models.load_statistics import LoadStatistics
from vrt_lss_universal.models.location import Location
from vrt_lss_universal.models.location_cargos_limit import LocationCargosLimit
from vrt_lss_universal.models.location_compatibilities import LocationCompatibilities
from vrt_lss_universal.models.location_limit import LocationLimit
from vrt_lss_universal.models.location_limit_statistics import LocationLimitStatistics
from vrt_lss_universal.models.location_statistics import LocationStatistics
from vrt_lss_universal.models.location_timetable_element import LocationTimetableElement
from vrt_lss_universal.models.location_transports_limit import LocationTransportsLimit
from vrt_lss_universal.models.measurements import Measurements
from vrt_lss_universal.models.model_break import ModelBreak
from vrt_lss_universal.models.order import Order
from vrt_lss_universal.models.order_compatibilities import OrderCompatibilities
from vrt_lss_universal.models.performer import Performer
from vrt_lss_universal.models.performer_compatibilities import PerformerCompatibilities
from vrt_lss_universal.models.performer_limits import PerformerLimits
from vrt_lss_universal.models.performer_shift import PerformerShift
from vrt_lss_universal.models.performer_tariff import PerformerTariff
from vrt_lss_universal.models.performer_tariff_constraint import PerformerTariffConstraint
from vrt_lss_universal.models.plan_result import PlanResult
from vrt_lss_universal.models.plan_settings import PlanSettings
from vrt_lss_universal.models.plan_statistics import PlanStatistics
from vrt_lss_universal.models.plan_task import PlanTask
from vrt_lss_universal.models.possible_event import PossibleEvent
from vrt_lss_universal.models.quality import Quality
from vrt_lss_universal.models.refine_result import RefineResult
from vrt_lss_universal.models.removed_items import RemovedItems
from vrt_lss_universal.models.replan_settings import ReplanSettings
from vrt_lss_universal.models.replan_strategy import ReplanStrategy
from vrt_lss_universal.models.replan_task import ReplanTask
from vrt_lss_universal.models.rest import Rest
from vrt_lss_universal.models.rest_rules import RestRules
from vrt_lss_universal.models.roundtrip_statistics import RoundtripStatistics
from vrt_lss_universal.models.routing_matrix import RoutingMatrix
from vrt_lss_universal.models.routing_matrix_waypoint import RoutingMatrixWaypoint
from vrt_lss_universal.models.routing_transport_matrix import RoutingTransportMatrix
from vrt_lss_universal.models.schema_error import SchemaError
from vrt_lss_universal.models.service import Service
from vrt_lss_universal.models.statistics_task import StatisticsTask
from vrt_lss_universal.models.stop_demand import StopDemand
from vrt_lss_universal.models.stop_statistics import StopStatistics
from vrt_lss_universal.models.task_statistics import TaskStatistics
from vrt_lss_universal.models.time_window import TimeWindow
from vrt_lss_universal.models.time_window_violation_detail import TimeWindowViolationDetail
from vrt_lss_universal.models.time_window_violations import TimeWindowViolations
from vrt_lss_universal.models.tracedata import Tracedata
from vrt_lss_universal.models.transport import Transport
from vrt_lss_universal.models.transport_capacity_multiplier import TransportCapacityMultiplier
from vrt_lss_universal.models.transport_compatibilities import TransportCompatibilities
from vrt_lss_universal.models.transport_limits import TransportLimits
from vrt_lss_universal.models.transport_load import TransportLoad
from vrt_lss_universal.models.transport_shift import TransportShift
from vrt_lss_universal.models.transport_speed_multiplier import TransportSpeedMultiplier
from vrt_lss_universal.models.transport_tariff import TransportTariff
from vrt_lss_universal.models.transport_tariff_constraint import TransportTariffConstraint
from vrt_lss_universal.models.transport_type import TransportType
from vrt_lss_universal.models.trip import Trip
from vrt_lss_universal.models.trip_assumptions import TripAssumptions
from vrt_lss_universal.models.trip_expectations import TripExpectations
from vrt_lss_universal.models.trip_penalties import TripPenalties
from vrt_lss_universal.models.trip_start_time_strategy import TripStartTimeStrategy
from vrt_lss_universal.models.trip_state import TripState
from vrt_lss_universal.models.trip_state_flag import TripStateFlag
from vrt_lss_universal.models.trip_statistics import TripStatistics
from vrt_lss_universal.models.trips_settings import TripsSettings
from vrt_lss_universal.models.universal_data import UniversalData
from vrt_lss_universal.models.unplanned_items import UnplannedItems
from vrt_lss_universal.models.validate_result import ValidateResult
from vrt_lss_universal.models.version_result import VersionResult
from vrt_lss_universal.models.work_and_rest_rules import WorkAndRestRules

""",
            name=__name__,
            doc=__doc__,
        )
    )
