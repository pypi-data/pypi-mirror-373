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
from vrt_lss_agro.models.crop import Crop
from vrt_lss_agro.models.elevator import Elevator
from vrt_lss_agro.models.factory import Factory
from vrt_lss_agro.models.leftover import Leftover
from vrt_lss_agro.models.market import Market
from vrt_lss_agro.models.model_field import ModelField
from vrt_lss_agro.models.movement_matrix_element import MovementMatrixElement
from vrt_lss_agro.models.plan_settings import PlanSettings
from typing import Optional, Set
from typing_extensions import Self

class PlanTask(BaseModel):
    """
    Initial task.
    """ # noqa: E501
    crops: Annotated[List[Crop], Field(min_length=1, max_length=501)] = Field(description="List of crops.")
    fields: Annotated[List[ModelField], Field(min_length=1, max_length=20001)] = Field(description="List of fields.")
    elevators: Optional[Annotated[List[Elevator], Field(min_length=1, max_length=501)]] = Field(default=None, description="List of elevators.")
    factories: Annotated[List[Factory], Field(min_length=1, max_length=501)] = Field(description="List of factories.")
    markets: Annotated[List[Market], Field(min_length=1, max_length=501)] = Field(description="List of markets.")
    movement_matrix: Annotated[List[MovementMatrixElement], Field(min_length=1, max_length=8040402)] = Field(description="Matrix describing the cost (in kilometers and monetary units) of moving grain between objects (in both directions). If there is no corresponding entry in the matrix between the objects, the movement of grain between them is considered impossible. ")
    leftovers: Optional[Annotated[List[Leftover], Field(min_length=0, max_length=25001)]] = Field(default=None, description="List of leftovers.")
    plan_settings: PlanSettings
    dataset_name: Optional[Annotated[str, Field(min_length=0, strict=True, max_length=512)]] = Field(default='', description="The name of the dataset. A technical field that does not affect calculation. ")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["crops", "fields", "elevators", "factories", "markets", "movement_matrix", "leftovers", "plan_settings", "dataset_name"]

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
        """Create an instance of PlanTask from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in crops (list)
        _items = []
        if self.crops:
            for _item_crops in self.crops:
                if _item_crops:
                    _items.append(_item_crops.to_dict())
            _dict['crops'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in fields (list)
        _items = []
        if self.fields:
            for _item_fields in self.fields:
                if _item_fields:
                    _items.append(_item_fields.to_dict())
            _dict['fields'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in elevators (list)
        _items = []
        if self.elevators:
            for _item_elevators in self.elevators:
                if _item_elevators:
                    _items.append(_item_elevators.to_dict())
            _dict['elevators'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in factories (list)
        _items = []
        if self.factories:
            for _item_factories in self.factories:
                if _item_factories:
                    _items.append(_item_factories.to_dict())
            _dict['factories'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in markets (list)
        _items = []
        if self.markets:
            for _item_markets in self.markets:
                if _item_markets:
                    _items.append(_item_markets.to_dict())
            _dict['markets'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in movement_matrix (list)
        _items = []
        if self.movement_matrix:
            for _item_movement_matrix in self.movement_matrix:
                if _item_movement_matrix:
                    _items.append(_item_movement_matrix.to_dict())
            _dict['movement_matrix'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in leftovers (list)
        _items = []
        if self.leftovers:
            for _item_leftovers in self.leftovers:
                if _item_leftovers:
                    _items.append(_item_leftovers.to_dict())
            _dict['leftovers'] = _items
        # override the default output from pydantic by calling `to_dict()` of plan_settings
        if self.plan_settings:
            _dict['plan_settings'] = self.plan_settings.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PlanTask from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "crops": [Crop.from_dict(_item) for _item in obj["crops"]] if obj.get("crops") is not None else None,
            "fields": [ModelField.from_dict(_item) for _item in obj["fields"]] if obj.get("fields") is not None else None,
            "elevators": [Elevator.from_dict(_item) for _item in obj["elevators"]] if obj.get("elevators") is not None else None,
            "factories": [Factory.from_dict(_item) for _item in obj["factories"]] if obj.get("factories") is not None else None,
            "markets": [Market.from_dict(_item) for _item in obj["markets"]] if obj.get("markets") is not None else None,
            "movement_matrix": [MovementMatrixElement.from_dict(_item) for _item in obj["movement_matrix"]] if obj.get("movement_matrix") is not None else None,
            "leftovers": [Leftover.from_dict(_item) for _item in obj["leftovers"]] if obj.get("leftovers") is not None else None,
            "plan_settings": PlanSettings.from_dict(obj["plan_settings"]) if obj.get("plan_settings") is not None else None,
            "dataset_name": obj.get("dataset_name") if obj.get("dataset_name") is not None else ''
        })
        # store additional fields in additional_properties
        for _key in obj.keys():
            if _key not in cls.__properties:
                _obj.additional_properties[_key] = obj.get(_key)

        return _obj


