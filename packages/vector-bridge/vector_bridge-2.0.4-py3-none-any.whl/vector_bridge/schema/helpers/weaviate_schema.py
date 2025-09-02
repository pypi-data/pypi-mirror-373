from typing import Dict, List, Union

from pydantic import BaseModel, Field, model_validator
from weaviate.classes.config import DataType, Tokenization

from vector_bridge.schema.helpers.enums import (ChangeEntityType,
                                                FilterOperator,
                                                ProtectedSchemaNames,
                                                SchemaDiffState)


class SchemaChanges(BaseModel):
    name: str
    description: str


class PropertyChanges(BaseModel):
    name: str
    description: str
    data_type: Union[DataType, ProtectedSchemaNames, str] = Field(default=DataType.TEXT)  # Object is not supported
    tokenization: Tokenization = Field(default=Tokenization.FIELD)
    sorting: bool
    returned: bool


class FilterChanges(BaseModel):
    name: str
    description: str = Field(default="")
    supported: bool
    operator: FilterOperator
    operator_settings: dict


class Changes(BaseModel):
    type: ChangeEntityType
    path: str
    diff_state: SchemaDiffState
    item: Union[SchemaChanges, PropertyChanges, FilterChanges]

    @model_validator(mode="before")
    def create_item_based_on_type(cls, values):
        type = values.get("type")
        item = values.get("item")

        # Mapping of ChangeEntityType to the model
        type_to_model = {
            ChangeEntityType.FILTER.value: FilterChanges,
            ChangeEntityType.PROPERTY.value: PropertyChanges,
            ChangeEntityType.SCHEMA.value: SchemaChanges,
        }

        if isinstance(item, dict):
            # Instantiate the correct model for 'item'
            if type in type_to_model:
                model = type_to_model[type]
                values["item"] = model(**item)
            else:
                raise ValueError("Invalid item type or data")

        return values

    @property
    def is_deleted(self):
        return self.diff_state == SchemaDiffState.DELETED

    @property
    def is_created(self):
        return self.diff_state == SchemaDiffState.CREATED

    @property
    def is_updated(self):
        return self.diff_state == SchemaDiffState.UPDATED

    @property
    def is_default(self):
        return self.diff_state == SchemaDiffState.DEFAULT

    @property
    def is_schema(self):
        return self.type == ChangeEntityType.SCHEMA

    @property
    def is_property(self):
        return self.type == ChangeEntityType.PROPERTY

    @property
    def is_filter(self):
        return self.type == ChangeEntityType.FILTER

    def set_deleted(self):
        self.diff_state = SchemaDiffState.DELETED

    def set_default(self):
        self.diff_state = SchemaDiffState.DEFAULT

    def set_created(self):
        self.diff_state = SchemaDiffState.CREATED

    @property
    def schema_name(self):
        return self.path.split(".")[0]

    @property
    def property_name(self):
        return self.path.split(".")[1]

    @property
    def filter_name(self):
        return self.path.split(".")[2]


class Filter(BaseModel):
    name: str
    description: str
    supported: bool = Field(default=False)
    operator: FilterOperator = Field(default=FilterOperator.EQUAL)
    operator_settings: dict = Field(default={})


class Filtering(BaseModel):
    operators: List[Filter] = Field(default=[])


class Sorting(BaseModel):
    supported: bool = Field(default=False)


class Property(BaseModel):
    name: str
    description: str
    data_type: Union[DataType, ProtectedSchemaNames, str]  # Object is not supported
    tokenization: Tokenization = Field(default=Tokenization.WORD)
    filtering: Filtering = Field(default=Filtering())
    sorting: Sorting = Field(default=Sorting())
    returned: bool = Field(default=False)


class Schema(BaseModel):
    name: str
    description: str
    properties: List[Property] = Field(default_factory=list)
    vectorizer: str = Field(default="text2vec-openai")  # TODO: Change to weaviate

    def get_property_by_name(self, name: str):
        for _property in self.properties:
            if _property.name == name:
                return _property


class WeaviateInternals(BaseModel):
    schemas: List[Schema]
    changeset: Dict[str, Changes] = Field(default_factory=dict)
    other: dict = Field(default_factory=dict)
    schemas_ready: bool = Field(default=False)

    def get_schema_by_name(self, name: str):
        for schema in self.schemas:
            if schema.name == name:
                return schema
