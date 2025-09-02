from typing import Any, List

from pydantic import BaseModel, Field

from vector_bridge.schema.helpers.enums import FilterOperator, SchemaDiffState


class Filter(BaseModel):
    name: str
    description: str
    supported: bool
    operator: FilterOperator
    operator_settings: dict


class StateFullFilter(Filter):
    state: SchemaDiffState = Field(default=SchemaDiffState.DEFAULT)


class Filtering(BaseModel):
    operators: List[Filter]

    def get_filter_by_name(self, name: str):
        for _operator in self.operators:
            if _operator.name == name:
                return _operator


class StateFullFiltering(Filtering):
    operators: List[StateFullFilter]


class Sorting(BaseModel):
    supported: bool


class Property(BaseModel):
    name: str
    description: str
    data_type: Any
    tokenization: Any
    filtering: Filtering
    sorting: Sorting
    returned: bool


class StateFullProperty(Property):
    state: SchemaDiffState
    filtering: StateFullFiltering


class Schema(BaseModel):
    name: str
    description: str
    properties: List[Property]
    vectorizer: str


class StateFullSchema(Schema):
    state: SchemaDiffState
    properties: List[StateFullProperty]
