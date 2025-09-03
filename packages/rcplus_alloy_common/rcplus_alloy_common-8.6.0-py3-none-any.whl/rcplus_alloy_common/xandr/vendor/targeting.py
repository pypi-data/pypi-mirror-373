# ruff: noqa: E501
"""
Microsoft Xandr API doesn't have any formal specifications. Code below is based on its documentation:
https://learn.microsoft.com/en-us/xandr/digital-platform-api/targeting-key-service
https://learn.microsoft.com/en-us/xandr/digital-platform-api/targeting-value-service
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TargetingKeyType(str, Enum):
    STRING = "string"
    NUMERIC = "numeric"


class TargetingKeyState(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class TargetingKey(BaseModel):
    """
    | Field         | Type (Length) | Description                                                                                                                                                                               |
    |---------------|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | id            | int           | The ID of the targeting key. Default: Auto-generated number. Required On: `PUT`/`DELETE`, in query string                                                                                 |
    | type          | enum          | The data type of the key and its associated values. Must be one of the following values: `string`, `numeric`. Required On: `POST`                                                         |
    | name          | string        | The name of the targeting key. The value must be one word, with no spaces. This name must be unique within your member. Required On: POST                                                 |
    | label         | string        | A label for the key, to be used for reporting. This value is not required, but if you do include a value, it must be unique within your member. Label can be a maximum of 190 characters. |
    | state         | enum          | The state of the targeting key. Possible values are `active` or `inactive`. Default: `active`                                                                                             |
    | created_on    | date          | Read-only. The date and time the targeting key was created.                                                                                                                               |
    | last_modified | date          | Read-only. The date and time the targeting key was last modified.                                                                                                                         |
    """
    id: Optional[int] = Field(None, description="The ID of the targeting key.")
    type: Optional[TargetingKeyType] = Field(None, description="The data type of the key and its associated values.")
    name: Optional[str] = Field(None, description="The name of the targeting key. The value must be one word, with no spaces. This name must be unique within your member.")
    label: Optional[str] = Field(None, description="A label for the key, to be used for reporting. This value is not required, but if you do include a value, it must be unique within your member. Label can be a maximum of 190 characters.")
    state: Optional[TargetingKeyState] = Field(TargetingKeyState.ACTIVE, description="The state of the targeting key. Possible values are active and inactive.")
    created_on: Optional[str] = Field(None, description="Read-only. The date and time the targeting key was created.")
    last_modified: Optional[str] = Field(None, description="Read-only. The date and time the targeting key was last modified.")


class TargetingValue(BaseModel):
    """
    | Field            | Type   | Description                                                                                                                                                                              |
    |------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | id               | int    | The ID of the targeting value. Required On: `PUT` and `DELETE`. Default: auto-generated number.                                                                                          |
    | targeting_key_id | int    | The ID of the associated targeting key. The targeting key must exist before a value can be created. See Targeting Key Service. Required On: `POST` and `GET`                             |
    | name             | string | The name of the targeting value. This name must be unique within a given targeting key.                                                                                                  |
    | label            | string | A label for the value, used for reporting purposes. This value is not required, but if you supply a value it must be unique within the a key. Labels can be a maximum of 190 characters. |
    | created_on       | date   | Read-only. The date and time the targeting value was created.                                                                                                                            |
    | last_modified    | date   | Read-only. The date and time the targeting value was last modified.                                                                                                                      |
    """
    id: Optional[int] = Field(None, description="The ID of the targeting value. Required On: PUT and DELETE. Default: auto-generated number.")
    targeting_key_id: Optional[int] = Field(None, description="The ID of the associated targeting key. The targeting key must exist before a value can be created. See Targeting Key Service. Required On: POST and GET.")
    name: Optional[str] = Field(None, description="The name of the targeting value. This name must be unique within a given targeting key.")
    label: Optional[str] = Field(None, description="A label for the value, used for reporting purposes. This value is not required, but if you supply a value it must be unique within the a key. Labels can be a maximum of 190 characters.")
    created_on: Optional[str] = Field(None, description="Read-only. The date and time the targeting value was created.")
    last_modified: Optional[str] = Field(None, description="Read-only. The date and time the targeting value was last modified.")
