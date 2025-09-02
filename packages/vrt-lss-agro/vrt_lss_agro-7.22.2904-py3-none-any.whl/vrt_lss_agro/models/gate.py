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
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from vrt_lss_agro.models.attribute import Attribute
from vrt_lss_agro.models.capacity_forecast_element import CapacityForecastElement
from vrt_lss_agro.models.cost_forecast_element import CostForecastElement
from typing import Optional, Set
from typing_extensions import Self

class Gate(BaseModel):
    """
    Grain process. 
    """ # noqa: E501
    key: Annotated[str, Field(min_length=1, strict=True, max_length=1024)] = Field(description="Key, unique identifier.")
    input_capacity_forecast: Annotated[List[CapacityForecastElement], Field(min_length=0, max_length=3653)] = Field(description="Capacity forecast.")
    input_cost_forecast: Optional[Annotated[List[CostForecastElement], Field(min_length=0, max_length=3653)]] = Field(default=None, description="Cost forecast.")
    output_capacity_forecast: Annotated[List[CapacityForecastElement], Field(min_length=0, max_length=3653)] = Field(description="Capacity forecast.")
    output_cost_forecast: Optional[Annotated[List[CostForecastElement], Field(min_length=0, max_length=3653)]] = Field(default=None, description="Cost forecast.")
    attributes: Optional[Annotated[List[Attribute], Field(min_length=0, max_length=250)]] = Field(default=None, description="Attributes. Used to add service information.")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["key", "input_capacity_forecast", "input_cost_forecast", "output_capacity_forecast", "output_cost_forecast", "attributes"]

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
        """Create an instance of Gate from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in input_capacity_forecast (list)
        _items = []
        if self.input_capacity_forecast:
            for _item_input_capacity_forecast in self.input_capacity_forecast:
                if _item_input_capacity_forecast:
                    _items.append(_item_input_capacity_forecast.to_dict())
            _dict['input_capacity_forecast'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in input_cost_forecast (list)
        _items = []
        if self.input_cost_forecast:
            for _item_input_cost_forecast in self.input_cost_forecast:
                if _item_input_cost_forecast:
                    _items.append(_item_input_cost_forecast.to_dict())
            _dict['input_cost_forecast'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in output_capacity_forecast (list)
        _items = []
        if self.output_capacity_forecast:
            for _item_output_capacity_forecast in self.output_capacity_forecast:
                if _item_output_capacity_forecast:
                    _items.append(_item_output_capacity_forecast.to_dict())
            _dict['output_capacity_forecast'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in output_cost_forecast (list)
        _items = []
        if self.output_cost_forecast:
            for _item_output_cost_forecast in self.output_cost_forecast:
                if _item_output_cost_forecast:
                    _items.append(_item_output_cost_forecast.to_dict())
            _dict['output_cost_forecast'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in attributes (list)
        _items = []
        if self.attributes:
            for _item_attributes in self.attributes:
                if _item_attributes:
                    _items.append(_item_attributes.to_dict())
            _dict['attributes'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Gate from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "key": obj.get("key"),
            "input_capacity_forecast": [CapacityForecastElement.from_dict(_item) for _item in obj["input_capacity_forecast"]] if obj.get("input_capacity_forecast") is not None else None,
            "input_cost_forecast": [CostForecastElement.from_dict(_item) for _item in obj["input_cost_forecast"]] if obj.get("input_cost_forecast") is not None else None,
            "output_capacity_forecast": [CapacityForecastElement.from_dict(_item) for _item in obj["output_capacity_forecast"]] if obj.get("output_capacity_forecast") is not None else None,
            "output_cost_forecast": [CostForecastElement.from_dict(_item) for _item in obj["output_cost_forecast"]] if obj.get("output_cost_forecast") is not None else None,
            "attributes": [Attribute.from_dict(_item) for _item in obj["attributes"]] if obj.get("attributes") is not None else None
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


