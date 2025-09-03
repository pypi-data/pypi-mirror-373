from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from vector_bridge.schema.helpers.enums import UserStatus, UserType
from vector_bridge.schema.security_group import SecurityGroup
from vector_bridge.schema.user_integrations import \
    UserIntegrationWithPermissions


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    full_name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str] = ""
    country: Optional[str] = ""
    state_region: Optional[str] = ""
    city: Optional[str] = ""
    address: Optional[str] = ""
    zip_code: Optional[str] = ""
    company_name: Optional[str] = ""
    user_role: Optional[str] = ""  # job title
    avatar_url: Optional[str] = ""
    user_type: UserType
    user_status: UserStatus
    organization_id: Optional[str] = "None"
    ws_connections: Dict[str, bool] = Field(default_factory=dict)

    @property
    def uuid(self):
        return self.id

    def __init__(self, **data):
        for key, value in data.items():
            if value == "":
                data[key] = None
            elif value == str(None):
                data[key] = None

        super().__init__(**data)
        if self.id == self.email:
            self.email = None

    @property
    def is_owner(self):
        return self.user_type == UserType.OWNER


class UserWithIntegrations(User):
    model_config = ConfigDict(from_attributes=True)

    integrations: List[UserIntegrationWithPermissions] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)


class UserWithSecurityGroup(User):
    model_config = ConfigDict(from_attributes=True)

    security_group: Optional[SecurityGroup] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)


class UserInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    full_name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str] = None
    country: Optional[str] = None
    state_region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    zip_code: Optional[str] = None
    company_name: Optional[str] = None
    user_role: Optional[str] = None
    avatar_url: Optional[str] = None
    user_type: UserType
    user_status: UserStatus
    organization_id: str
    hashed_password: Optional[str]
    user_data: Optional[Dict[str, Any]]
    ws_connections: Dict[str, bool] = Field(default_factory=dict)

    @property
    def uuid(self):
        return self.id


class UserPrivate(User):
    model_config = ConfigDict(from_attributes=True)

    hashed_password: Optional[str]
    user_data: Optional[Dict[str, Any]]
    ws_connections: Dict[str, bool] = Field(default_factory=dict)


class UserCreate(BaseModel):
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    email: str
    password: str
    user_type: UserType = Field(default=UserType.USER)


class ConfirmUserEmail(BaseModel):
    email: str
    code: str


class ForgotUserPassword(BaseModel):
    email: str
    code: str
    password: str


class ChangeUserPassword(BaseModel):
    old_password: str
    new_password: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str]
    phone_number: Optional[str] = None
    country: Optional[str] = None
    state_region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    zip_code: Optional[str] = None
    company_name: Optional[str] = None
    user_role: Optional[str] = None
    avatar_url: Optional[str] = None


class OtherUserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str] = None
    country: Optional[str] = None
    state_region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    zip_code: Optional[str] = None
    company_name: Optional[str] = None
    user_role: Optional[str] = None
    organization_id: Optional[str]


class UsersList(BaseModel):
    users: List[Union[UserWithIntegrations, User]]
    limit: int
    last_evaluated_key: Union[str, None]
    has_more: bool = Field(default=False)

    def __init__(self, **data):
        if data["users"]:
            if "integrations" in data["users"][0]:
                data["users"] = [UserWithIntegrations.model_validate(user) for user in data["users"]]
            else:
                data["users"] = [User.model_validate(user) for user in data["users"]]

        super().__init__(**data)
