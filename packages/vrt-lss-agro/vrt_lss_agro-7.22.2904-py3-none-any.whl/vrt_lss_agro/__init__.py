# coding: utf-8

# flake8: noqa

"""
    VRt.Agro [AG]

    Veeroute Agro API.  # Description  The service is designed to calculate the work plan of production facilities.  ## Objects overview  ![objects](../images/agro_objects.svg)  ### Field  - produces a certain crop of a certain moisture content - products from the field can only be moved to the Elevator or Factory  ### Elevator  - consists of Gates, Dryers, short-term and long-term storage areas - dries the grain (if the moisture content of the crop is more than acceptable) - stores dry grain in short-term storage places (warehouses), while unloading and loading grain is allowed within one day - stores dry grain in long-term storage places (sleeves, trenches, mounds) - when stored in one storage, only one type of culture can be located - sells surplus grain to the Market - production processes inside the facility: drying, loading / unloading to a storage location, storage  ### Factory  - consists of Gates, Dryers, Bunkers, Consumers - [if drying is present] dries the grain (if the moisture content of the crop is more than allowed) - stores dry grain in Bunkers (short-term storage tied to a specific crop) - maintains a minimum supply of grain for consumption in the Bunkers - Consumes grain from Bunkers - buys the missing grain from the Market - production processes inside the facility: drying, loading / unloading to a storage location, storage, consumption  ### Market  - buys grain from elevators - sells grain to factories  ## Project  The project reflects the planned sequence of operations on agricultural crops, the types of operations are described below.  ### HARVEST  Crop harvesting:  - between production facilities (Field and Elevator or Field) - the operation takes place within one day - on the Field there is a determination of grain moisture  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Field               | -                             | | Destination | Elevator or Factory | Gate                          |  ### DRY  Drying culture:  - inside the production facility (Elevator or Field) - duration of the operation - days - during the drying process, the mass and type of humidity changes (WET -> DRY) - the source indicates the mass of raw culture - in the appointment, the resulting mass of dry culture is indicated  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Elevator or Factory | Gate                          | | Destination | Elevator or Factory | Dryer                         |  ### LOAD  Loading culture from the Gate to the Storage Location (long-term, short-term, silo):  - between parts of one production facility (Elevator or Field) - the operation takes place within one day  |             | Object (target_key) | Subobject (target_detail_key)                    | |-------------|---------------------|--------------------------------------------------| | Source      | Elevator or Factory | Gate or Dryer                                    | | Destination | Elevator or Factory | Storage location (long-term, short-term, bunker) |  ### UNLOAD  Unloading the culture from the storage place to the gate:  - between parts of one production facility (Elevator) - the operation takes place within one day  |             | Object (target_key) | Subobject (target_detail_key)                    | |-------------|---------------------|--------------------------------------------------| | Source      | Elevator            | Storage location (long-term, short-term, bunker) | | Destination | Elevator            | Gate                                             |  ### STORE  Culture storage:  - the operation takes place within one day - storage location does not change  |             | Object (target_key) | Subobject (target_detail_key)                    | |-------------|---------------------|--------------------------------------------------| | Source      | Elevator or Factory | Storage location (long-term, short-term, bunker) | | Destination | Elevator or Factory | The same storage location                        |  ### RELOCATE  Transportation between production facilities:  - between production facilities (Elevator and Field) - the operation takes place within one day  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Elevator            | Gate                          | | Destination | Factory             | Gate                          |  ### CONSUMPTION  Field crop consumption:  - between parts of one production facility (Field) - the operation takes place within one day - consumption comes from the Bunker - in addition, we can consume directly from the Gate or Dryer without laying in the Bunker  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Factory             | Hopper or Gate or Dryer       | | Destination | Factory             | Consumer                      |  ### SELL  Sale of culture:  - between production facilities (Elevator and Market) - the operation takes place within one day  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Elevator            | Gate                          | | Destination | Market              | Contract                      |  ### BUY  Buying culture:  - between production facilities (Market and Factory) - the operation takes place within one day  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Market              | Contract                      | | Destination | Factory             | Gate                          |  ## Entity relationship diagram  ![erd](../uml/agro.svg) 

    The version of the OpenAPI document: 7.22.2904
    Contact: servicedesk@veeroute.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "7.22.2904"

# Define package exports
__all__ = [
    "PlanApi",
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
    "Attribute",
    "Bunker",
    "CalculationAsyncResult",
    "CalculationInfo",
    "CalculationSettings",
    "CalculationState",
    "CalculationStatus",
    "CapacityForecastElement",
    "Chamber",
    "CheckResult",
    "Consumer",
    "Contract",
    "ContractType",
    "CostForecastElement",
    "Crop",
    "CropType",
    "Custom400WithErrorsAndWarnings",
    "DateWindow",
    "Dryer",
    "Elevator",
    "EntityError",
    "EntityErrorType",
    "EntityPath",
    "EntityType",
    "EntityWarning",
    "EntityWarningType",
    "Factory",
    "Gate",
    "General402",
    "General404",
    "General404Detail",
    "General429",
    "General500",
    "HumidityForecastElement",
    "Leftover",
    "ManufacturingOperation",
    "Market",
    "ModelField",
    "MovementMatrixElement",
    "ObjectType",
    "OperationMeasurements",
    "OperationTarget",
    "OperationType",
    "PlanResult",
    "PlanSettings",
    "PlanStatistics",
    "PlanTask",
    "PriceForecastElement",
    "Pricelist",
    "ProductivityForecastElement",
    "ProjectConfiguration",
    "ProjectSettings",
    "SchemaError",
    "Service",
    "Silo",
    "StockForecastElement",
    "Storage",
    "Tracedata",
    "UnplannedItems",
    "ValidateResult",
    "VersionResult",
]

if __import__("typing").TYPE_CHECKING:
    # import apis into sdk package
    from vrt_lss_agro.api.plan_api import PlanApi as PlanApi
    from vrt_lss_agro.api.system_api import SystemApi as SystemApi
    
    # import ApiClient
    from vrt_lss_agro.api_response import ApiResponse as ApiResponse
    from vrt_lss_agro.api_client import ApiClient as ApiClient
    from vrt_lss_agro.configuration import Configuration as Configuration
    from vrt_lss_agro.exceptions import OpenApiException as OpenApiException
    from vrt_lss_agro.exceptions import ApiTypeError as ApiTypeError
    from vrt_lss_agro.exceptions import ApiValueError as ApiValueError
    from vrt_lss_agro.exceptions import ApiKeyError as ApiKeyError
    from vrt_lss_agro.exceptions import ApiAttributeError as ApiAttributeError
    from vrt_lss_agro.exceptions import ApiException as ApiException
    
    # import models into sdk package
    from vrt_lss_agro.models.attribute import Attribute as Attribute
    from vrt_lss_agro.models.bunker import Bunker as Bunker
    from vrt_lss_agro.models.calculation_async_result import CalculationAsyncResult as CalculationAsyncResult
    from vrt_lss_agro.models.calculation_info import CalculationInfo as CalculationInfo
    from vrt_lss_agro.models.calculation_settings import CalculationSettings as CalculationSettings
    from vrt_lss_agro.models.calculation_state import CalculationState as CalculationState
    from vrt_lss_agro.models.calculation_status import CalculationStatus as CalculationStatus
    from vrt_lss_agro.models.capacity_forecast_element import CapacityForecastElement as CapacityForecastElement
    from vrt_lss_agro.models.chamber import Chamber as Chamber
    from vrt_lss_agro.models.check_result import CheckResult as CheckResult
    from vrt_lss_agro.models.consumer import Consumer as Consumer
    from vrt_lss_agro.models.contract import Contract as Contract
    from vrt_lss_agro.models.contract_type import ContractType as ContractType
    from vrt_lss_agro.models.cost_forecast_element import CostForecastElement as CostForecastElement
    from vrt_lss_agro.models.crop import Crop as Crop
    from vrt_lss_agro.models.crop_type import CropType as CropType
    from vrt_lss_agro.models.custom400_with_errors_and_warnings import Custom400WithErrorsAndWarnings as Custom400WithErrorsAndWarnings
    from vrt_lss_agro.models.date_window import DateWindow as DateWindow
    from vrt_lss_agro.models.dryer import Dryer as Dryer
    from vrt_lss_agro.models.elevator import Elevator as Elevator
    from vrt_lss_agro.models.entity_error import EntityError as EntityError
    from vrt_lss_agro.models.entity_error_type import EntityErrorType as EntityErrorType
    from vrt_lss_agro.models.entity_path import EntityPath as EntityPath
    from vrt_lss_agro.models.entity_type import EntityType as EntityType
    from vrt_lss_agro.models.entity_warning import EntityWarning as EntityWarning
    from vrt_lss_agro.models.entity_warning_type import EntityWarningType as EntityWarningType
    from vrt_lss_agro.models.factory import Factory as Factory
    from vrt_lss_agro.models.gate import Gate as Gate
    from vrt_lss_agro.models.general402 import General402 as General402
    from vrt_lss_agro.models.general404 import General404 as General404
    from vrt_lss_agro.models.general404_detail import General404Detail as General404Detail
    from vrt_lss_agro.models.general429 import General429 as General429
    from vrt_lss_agro.models.general500 import General500 as General500
    from vrt_lss_agro.models.humidity_forecast_element import HumidityForecastElement as HumidityForecastElement
    from vrt_lss_agro.models.leftover import Leftover as Leftover
    from vrt_lss_agro.models.manufacturing_operation import ManufacturingOperation as ManufacturingOperation
    from vrt_lss_agro.models.market import Market as Market
    from vrt_lss_agro.models.model_field import ModelField as ModelField
    from vrt_lss_agro.models.movement_matrix_element import MovementMatrixElement as MovementMatrixElement
    from vrt_lss_agro.models.object_type import ObjectType as ObjectType
    from vrt_lss_agro.models.operation_measurements import OperationMeasurements as OperationMeasurements
    from vrt_lss_agro.models.operation_target import OperationTarget as OperationTarget
    from vrt_lss_agro.models.operation_type import OperationType as OperationType
    from vrt_lss_agro.models.plan_result import PlanResult as PlanResult
    from vrt_lss_agro.models.plan_settings import PlanSettings as PlanSettings
    from vrt_lss_agro.models.plan_statistics import PlanStatistics as PlanStatistics
    from vrt_lss_agro.models.plan_task import PlanTask as PlanTask
    from vrt_lss_agro.models.price_forecast_element import PriceForecastElement as PriceForecastElement
    from vrt_lss_agro.models.pricelist import Pricelist as Pricelist
    from vrt_lss_agro.models.productivity_forecast_element import ProductivityForecastElement as ProductivityForecastElement
    from vrt_lss_agro.models.project_configuration import ProjectConfiguration as ProjectConfiguration
    from vrt_lss_agro.models.project_settings import ProjectSettings as ProjectSettings
    from vrt_lss_agro.models.schema_error import SchemaError as SchemaError
    from vrt_lss_agro.models.service import Service as Service
    from vrt_lss_agro.models.silo import Silo as Silo
    from vrt_lss_agro.models.stock_forecast_element import StockForecastElement as StockForecastElement
    from vrt_lss_agro.models.storage import Storage as Storage
    from vrt_lss_agro.models.tracedata import Tracedata as Tracedata
    from vrt_lss_agro.models.unplanned_items import UnplannedItems as UnplannedItems
    from vrt_lss_agro.models.validate_result import ValidateResult as ValidateResult
    from vrt_lss_agro.models.version_result import VersionResult as VersionResult
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            ("__version__", __version__),
            ("__all__", __all__),
            """# import apis into sdk package
from vrt_lss_agro.api.plan_api import PlanApi as PlanApi
from vrt_lss_agro.api.system_api import SystemApi as SystemApi

# import ApiClient
from vrt_lss_agro.api_response import ApiResponse as ApiResponse
from vrt_lss_agro.api_client import ApiClient as ApiClient
from vrt_lss_agro.configuration import Configuration as Configuration
from vrt_lss_agro.exceptions import OpenApiException as OpenApiException
from vrt_lss_agro.exceptions import ApiTypeError as ApiTypeError
from vrt_lss_agro.exceptions import ApiValueError as ApiValueError
from vrt_lss_agro.exceptions import ApiKeyError as ApiKeyError
from vrt_lss_agro.exceptions import ApiAttributeError as ApiAttributeError
from vrt_lss_agro.exceptions import ApiException as ApiException

# import models into sdk package
from vrt_lss_agro.models.attribute import Attribute as Attribute
from vrt_lss_agro.models.bunker import Bunker as Bunker
from vrt_lss_agro.models.calculation_async_result import CalculationAsyncResult as CalculationAsyncResult
from vrt_lss_agro.models.calculation_info import CalculationInfo as CalculationInfo
from vrt_lss_agro.models.calculation_settings import CalculationSettings as CalculationSettings
from vrt_lss_agro.models.calculation_state import CalculationState as CalculationState
from vrt_lss_agro.models.calculation_status import CalculationStatus as CalculationStatus
from vrt_lss_agro.models.capacity_forecast_element import CapacityForecastElement as CapacityForecastElement
from vrt_lss_agro.models.chamber import Chamber as Chamber
from vrt_lss_agro.models.check_result import CheckResult as CheckResult
from vrt_lss_agro.models.consumer import Consumer as Consumer
from vrt_lss_agro.models.contract import Contract as Contract
from vrt_lss_agro.models.contract_type import ContractType as ContractType
from vrt_lss_agro.models.cost_forecast_element import CostForecastElement as CostForecastElement
from vrt_lss_agro.models.crop import Crop as Crop
from vrt_lss_agro.models.crop_type import CropType as CropType
from vrt_lss_agro.models.custom400_with_errors_and_warnings import Custom400WithErrorsAndWarnings as Custom400WithErrorsAndWarnings
from vrt_lss_agro.models.date_window import DateWindow as DateWindow
from vrt_lss_agro.models.dryer import Dryer as Dryer
from vrt_lss_agro.models.elevator import Elevator as Elevator
from vrt_lss_agro.models.entity_error import EntityError as EntityError
from vrt_lss_agro.models.entity_error_type import EntityErrorType as EntityErrorType
from vrt_lss_agro.models.entity_path import EntityPath as EntityPath
from vrt_lss_agro.models.entity_type import EntityType as EntityType
from vrt_lss_agro.models.entity_warning import EntityWarning as EntityWarning
from vrt_lss_agro.models.entity_warning_type import EntityWarningType as EntityWarningType
from vrt_lss_agro.models.factory import Factory as Factory
from vrt_lss_agro.models.gate import Gate as Gate
from vrt_lss_agro.models.general402 import General402 as General402
from vrt_lss_agro.models.general404 import General404 as General404
from vrt_lss_agro.models.general404_detail import General404Detail as General404Detail
from vrt_lss_agro.models.general429 import General429 as General429
from vrt_lss_agro.models.general500 import General500 as General500
from vrt_lss_agro.models.humidity_forecast_element import HumidityForecastElement as HumidityForecastElement
from vrt_lss_agro.models.leftover import Leftover as Leftover
from vrt_lss_agro.models.manufacturing_operation import ManufacturingOperation as ManufacturingOperation
from vrt_lss_agro.models.market import Market as Market
from vrt_lss_agro.models.model_field import ModelField as ModelField
from vrt_lss_agro.models.movement_matrix_element import MovementMatrixElement as MovementMatrixElement
from vrt_lss_agro.models.object_type import ObjectType as ObjectType
from vrt_lss_agro.models.operation_measurements import OperationMeasurements as OperationMeasurements
from vrt_lss_agro.models.operation_target import OperationTarget as OperationTarget
from vrt_lss_agro.models.operation_type import OperationType as OperationType
from vrt_lss_agro.models.plan_result import PlanResult as PlanResult
from vrt_lss_agro.models.plan_settings import PlanSettings as PlanSettings
from vrt_lss_agro.models.plan_statistics import PlanStatistics as PlanStatistics
from vrt_lss_agro.models.plan_task import PlanTask as PlanTask
from vrt_lss_agro.models.price_forecast_element import PriceForecastElement as PriceForecastElement
from vrt_lss_agro.models.pricelist import Pricelist as Pricelist
from vrt_lss_agro.models.productivity_forecast_element import ProductivityForecastElement as ProductivityForecastElement
from vrt_lss_agro.models.project_configuration import ProjectConfiguration as ProjectConfiguration
from vrt_lss_agro.models.project_settings import ProjectSettings as ProjectSettings
from vrt_lss_agro.models.schema_error import SchemaError as SchemaError
from vrt_lss_agro.models.service import Service as Service
from vrt_lss_agro.models.silo import Silo as Silo
from vrt_lss_agro.models.stock_forecast_element import StockForecastElement as StockForecastElement
from vrt_lss_agro.models.storage import Storage as Storage
from vrt_lss_agro.models.tracedata import Tracedata as Tracedata
from vrt_lss_agro.models.unplanned_items import UnplannedItems as UnplannedItems
from vrt_lss_agro.models.validate_result import ValidateResult as ValidateResult
from vrt_lss_agro.models.version_result import VersionResult as VersionResult

""",
            name=__name__,
            doc=__doc__,
        )
    )
