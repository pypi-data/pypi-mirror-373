# coding: utf-8

"""
    VRt.Agro [AG]

    Veeroute Agro API.  # Description  The service is designed to calculate the work plan of production facilities.  ## Objects overview  ![objects](../images/agro_objects.svg)  ### Field  - produces a certain crop of a certain moisture content - products from the field can only be moved to the Elevator or Factory  ### Elevator  - consists of Gates, Dryers, short-term and long-term storage areas - dries the grain (if the moisture content of the crop is more than acceptable) - stores dry grain in short-term storage places (warehouses), while unloading and loading grain is allowed within one day - stores dry grain in long-term storage places (sleeves, trenches, mounds) - when stored in one storage, only one type of culture can be located - sells surplus grain to the Market - production processes inside the facility: drying, loading / unloading to a storage location, storage  ### Factory  - consists of Gates, Dryers, Bunkers, Consumers - [if drying is present] dries the grain (if the moisture content of the crop is more than allowed) - stores dry grain in Bunkers (short-term storage tied to a specific crop) - maintains a minimum supply of grain for consumption in the Bunkers - Consumes grain from Bunkers - buys the missing grain from the Market - production processes inside the facility: drying, loading / unloading to a storage location, storage, consumption  ### Market  - buys grain from elevators - sells grain to factories  ## Project  The project reflects the planned sequence of operations on agricultural crops, the types of operations are described below.  ### HARVEST  Crop harvesting:  - between production facilities (Field and Elevator or Field) - the operation takes place within one day - on the Field there is a determination of grain moisture  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Field               | -                             | | Destination | Elevator or Factory | Gate                          |  ### DRY  Drying culture:  - inside the production facility (Elevator or Field) - duration of the operation - days - during the drying process, the mass and type of humidity changes (WET -> DRY) - the source indicates the mass of raw culture - in the appointment, the resulting mass of dry culture is indicated  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Elevator or Factory | Gate                          | | Destination | Elevator or Factory | Dryer                         |  ### LOAD  Loading culture from the Gate to the Storage Location (long-term, short-term, silo):  - between parts of one production facility (Elevator or Field) - the operation takes place within one day  |             | Object (target_key) | Subobject (target_detail_key)                    | |-------------|---------------------|--------------------------------------------------| | Source      | Elevator or Factory | Gate or Dryer                                    | | Destination | Elevator or Factory | Storage location (long-term, short-term, bunker) |  ### UNLOAD  Unloading the culture from the storage place to the gate:  - between parts of one production facility (Elevator) - the operation takes place within one day  |             | Object (target_key) | Subobject (target_detail_key)                    | |-------------|---------------------|--------------------------------------------------| | Source      | Elevator            | Storage location (long-term, short-term, bunker) | | Destination | Elevator            | Gate                                             |  ### STORE  Culture storage:  - the operation takes place within one day - storage location does not change  |             | Object (target_key) | Subobject (target_detail_key)                    | |-------------|---------------------|--------------------------------------------------| | Source      | Elevator or Factory | Storage location (long-term, short-term, bunker) | | Destination | Elevator or Factory | The same storage location                        |  ### RELOCATE  Transportation between production facilities:  - between production facilities (Elevator and Field) - the operation takes place within one day  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Elevator            | Gate                          | | Destination | Factory             | Gate                          |  ### CONSUMPTION  Field crop consumption:  - between parts of one production facility (Field) - the operation takes place within one day - consumption comes from the Bunker - in addition, we can consume directly from the Gate or Dryer without laying in the Bunker  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Factory             | Hopper or Gate or Dryer       | | Destination | Factory             | Consumer                      |  ### SELL  Sale of culture:  - between production facilities (Elevator and Market) - the operation takes place within one day  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Elevator            | Gate                          | | Destination | Market              | Contract                      |  ### BUY  Buying culture:  - between production facilities (Market and Factory) - the operation takes place within one day  |             | Object (target_key) | Subobject (target_detail_key) | |-------------|---------------------|-------------------------------| | Source      | Market              | Contract                      | | Destination | Factory             | Gate                          |  ## Entity relationship diagram  ![erd](../uml/agro.svg) 

    The version of the OpenAPI document: 7.22.2904
    Contact: servicedesk@veeroute.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, ClassVar, Dict, List, Union
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class PlanStatistics(BaseModel):
    """
    General statistics. 
    """ # noqa: E501
    days_count: Annotated[int, Field(le=3653, strict=True, ge=0)] = Field(description="The number of planned fields.")
    crops_count: Annotated[int, Field(le=501, strict=True, ge=0)] = Field(description="The total number of planned crops.")
    fields_count: Annotated[int, Field(le=20001, strict=True, ge=0)] = Field(description="The total number of planned fields.")
    fields_part_count: Annotated[int, Field(le=20001, strict=True, ge=0)] = Field(description="Total number of partially harvested fields.")
    elevators_count: Annotated[int, Field(le=501, strict=True, ge=0)] = Field(description="The total number of planned elevators.")
    factory_count: Annotated[int, Field(le=501, strict=True, ge=0)] = Field(description="The total number of planned factories.")
    markets_count: Annotated[int, Field(le=501, strict=True, ge=0)] = Field(description="The total number of planned markets.")
    total_distance: Annotated[int, Field(le=10000000000, strict=True, ge=0)] = Field(description="Total mileage, in km.")
    total_cost: Union[Annotated[float, Field(le=1000000000000, strict=True, ge=-1000000000000)], Annotated[int, Field(le=2147483647, strict=True, ge=-2147483648)]] = Field(description="The total cost of all transactions, in conventional monetary units.")
    unplanned_crops_count: Annotated[int, Field(le=501, strict=True, ge=0)] = Field(description="Total number of unused crops.")
    unplanned_fields_count: Annotated[int, Field(le=20001, strict=True, ge=0)] = Field(description="Total number of unharvested fields.")
    unplanned_elevators_count: Annotated[int, Field(le=10001, strict=True, ge=0)] = Field(description="Total number of unused elevators.")
    unplanned_factories_count: Annotated[int, Field(le=501, strict=True, ge=0)] = Field(description="Total number of unused factories.")
    unplanned_markets_count: Annotated[int, Field(le=501, strict=True, ge=0)] = Field(description="Total number of unused markets.")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["days_count", "crops_count", "fields_count", "fields_part_count", "elevators_count", "factory_count", "markets_count", "total_distance", "total_cost", "unplanned_crops_count", "unplanned_fields_count", "unplanned_elevators_count", "unplanned_factories_count", "unplanned_markets_count"]

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
        """Create an instance of PlanStatistics from a JSON string"""
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

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PlanStatistics from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "days_count": obj.get("days_count"),
            "crops_count": obj.get("crops_count"),
            "fields_count": obj.get("fields_count"),
            "fields_part_count": obj.get("fields_part_count"),
            "elevators_count": obj.get("elevators_count"),
            "factory_count": obj.get("factory_count"),
            "markets_count": obj.get("markets_count"),
            "total_distance": obj.get("total_distance"),
            "total_cost": obj.get("total_cost"),
            "unplanned_crops_count": obj.get("unplanned_crops_count"),
            "unplanned_fields_count": obj.get("unplanned_fields_count"),
            "unplanned_elevators_count": obj.get("unplanned_elevators_count"),
            "unplanned_factories_count": obj.get("unplanned_factories_count"),
            "unplanned_markets_count": obj.get("unplanned_markets_count")
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


