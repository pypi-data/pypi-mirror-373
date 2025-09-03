# ruff: noqa: E501, W605
"""
Microsoft Xandr API doesn't have any formal specifications. Code below is based on its documentation:
https://learn.microsoft.com/en-us/xandr/digital-platform-api/segment-service
"""
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class SegmentState(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class PiggybackPixelType(str, Enum):
    JS = "js"
    IMG = "img"


class PiggybackPixel(BaseModel):
    """
    | Field      | Type   | Description                                                     |
    |------------|--------|-----------------------------------------------------------------|
    | url        | string | The URL of the pixel to piggyback.                              |
    | pixel_type | enum   | The type of pixel to piggyback. Possible values: "js" or "img". |
    """
    url: Optional[str] = Field(None, description="The URL of the pixel to piggyback.")
    pixel_type: Optional[PiggybackPixelType] = Field(PiggybackPixelType.IMG, description='The type of pixel to piggyback. Possible values: "js" or "img".')


class QueryStringValueType(str, Enum):
    TEXT = "text"
    NUMERIC = "numeric"
    NONE = "none"


class QueryStringMapping(BaseModel):
    """
    | Field            | Type    | Description                                                                                                                                                                                                                                                                                                                                                                   |
    |------------------|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | param            | string  | The query string parameter.                                                                                                                                                                                                                                                                                                                                                   |
    | value_type       | enum    | The type of value accompanying the parameter. Possible values: "text", "numeric", or "none".                                                                                                                                                                                                                                                                                  |
    | values           | array   | The strings that can accompany the parameter when value_type is "text". If value_type is "numeric" or "none", this field cannot be used.                                                                                                                                                                                                                                      |
    | allow_empty_text | boolean | When true, the values array may be null. May only be used when the value_type is "text". Default: false                                                                                                                                                                                                                                                                       |
    | publishers       | array   | The publishers from which you expect the query string. Users associated with these publishers' placements will be added to the segment.                                                                                                                                                                                                                                       |
    | sites            | array   | The placement groups (sites) from which you expect the query string. Users associated with these placements will be added to the segment. Note: This field overrides publishers. If you specify a site that doesn't belong to one of the specified publishers, users associated with the placements in a placement group will nonetheless be added to the segment.            |
    | placements       | array   | The placements in which you expect the query string. Users associated with these placements will be added to the segment. Note: This field overrides placement groups and publishers. That is, if you specify a placement that doesn't belong to one of the specified placement groups or publishers, users associated with the placement will still be added to the segment. |
    | include_shared   | boolean | Set this value to false to avoid retrieving shared segments.                                                                                                                                                                                                                                                                                                                  |
    """
    param: Optional[str] = Field(None, description="The query string parameter.")
    value_type: Optional[QueryStringValueType] = Field(QueryStringValueType.TEXT, description='The type of value accompanying the parameter. Possible values: "text", "numeric", or "none".')
    values: Optional[List[str]] = Field(None, description='The strings that can accompany the parameter when value_type is "text". Cannot be used if value_type is "numeric" or "none".')
    allow_empty_text: Optional[bool] = Field(False, description='When true, the values array may be null. May only be used when the value_type is "text". Default: false.')
    publishers: Optional[List[str]] = Field(None, description="The publishers from which you expect the query string.")
    sites: Optional[List[str]] = Field(None, description="The placement groups (sites) from which you expect the query string. Overrides publishers.")
    placements: Optional[List[str]] = Field(None, description="The placements in which you expect the query string. Overrides placement groups and publishers.")
    include_shared: Optional[bool] = Field(None, description="Set this value to false to avoid retrieving shared segments.")


class QueryStringMappingKeyValue(BaseModel):
    """
    | Field    | Type   | Description                                                                                                                                                         |
    |----------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | qs_key   | string | The query string parameter.                                                                                                                                         |
    | qs_value | string | A value for the query string key. The value can be empty or null. Multiple values can be added using the same key. A qs_value must be provided if a qs_key is used. |
    """
    qs_key: Optional[str] = Field(None, description="The query string parameter.")
    qs_value: Optional[str] = Field(None, description="A value for the query string key. Can be empty or null. Must be provided if a qs_key is used.")


class Segment(BaseModel):
    """
    | Field                         | Type        | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    |-------------------------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | id                            | int         | The Xandr ID assigned by the API to reference the segment. When switching a segment from advertiser-owned to network-owned, you must pass this information in the query-string. Required On: PUT, in query-string                                                                                                                                                                                                                                                                 |
    | code                          | string(50)  | The user-defined code for calling the segment. Note: The value of the code field is not case-sensitive (e.g., "Test" is the same as "test"), so each code must be unique regardless of case. However, when referring to the code in query string targeting, case-sensitivity matters (e.g., if the value of the code field is "Test", the parameter in a query string referring to it must also be "Test").                                                                       |
    | state                         | enum        | The state of the segment. This determines whether the segment can be used. Possible values: active or inactive. Default: active                                                                                                                                                                                                                                                                                                                                                   |
    | short_name                    | string(255) | The short name used to describe the segment.                                                                                                                                                                                                                                                                                                                                                                                                                                      |
    | description                   | string(500) | The optional description for this segment. Maximum 500 characters. Restricted characters: ' \                                                                                                                                                                                                                                                                                                                                                                                     |
    | member_id                     | int         | The ID of the member that owns this segment. Note: When switching a segment from advertiser-owned to network-owned, you must pass this information in the query string. See Examples for more details.                                                                                                                                                                                                                                                                            |
    | category                      | string      | Deprecated. This field is read-only.                                                                                                                                                                                                                                                                                                                                                                                                                                              |
    | expire_minutes                | int         | The number of minutes the user is kept in the segment. Segments with no expiration time will be expired from the Xandr server-side data store within 90 days. If you want to add the user to the segment only for the duration of the ad call, set to 0. Changing this value does not retroactively affect users already in the segment. Also, if a user is re-added, the expiration window resets. Note: To keep users in the segment for the 180-day maximum, set this to null. |
    | enable_rm_piggyback           | boolean     | If true, piggybacking RM pixels is enabled.                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | max_usersync_pixels           | int         | The maximum number of third-party user sync pixels to piggyback onto the segment pixel. Set to 0 to block all third-party user sync pixels. If blank (null), the segment defaults to 0. Note: Invalid, if querystring_mapping_key_value object is also included. Default: 0                                                                                                                                                                                                       |
    | last_modified                 | timestamp   | The date and time when the segment was last modified.                                                                                                                                                                                                                                                                                                                                                                                                                             |
    | provider_id                   | int         | The ID of the data provider that owns the segment. It is read-only and can be used for filtering segments. Default: null                                                                                                                                                                                                                                                                                                                                                          |
    | advertiser_id                 | int         | The ID of the advertiser using the segment if the segment should be on the Advertiser level rather than the Network level. If null, the segment will be usable by all advertisers for that member. This information is for reference in Console. Default: null                                                                                                                                                                                                                    |
    | piggyback_pixels              | array       | The URLs of the pixels you want us to fire when the segment pixel fires. See Piggyback Pixels below for more details.                                                                                                                                                                                                                                                                                                                                                             |
    | price                         | double      | Deprecated. This field is currently not operational. Default: 0                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | parent_segment_id             | int         | The ID of the parent segment. If the parent segment is targeted in a profile, the direct child segments are targeted as well.  Note: The parent_segment_id field was deprecated on January 1, 2019.                                                                                                                                                                                                                                                                               |
    | querystring_mapping           | object      | A query string that allows you to assign a set of parameters and values to a segment. See About Query Strings for a general description of query strings and Query String Mapping for more details.                                                                                                                                                                                                                                                                               |
    | querystring_mapping_key_value | object      | A query string that allows you to reuse a key and assign a single key-value pair to a segment. See About Query Strings for a general description of query strings and Query String Mapping Key Value for more details. Note: Invalid, if a querystring_mapping object is also included. The value of the querystring_mapping_key_value field is case-insensitive when it is looked up in an auction.                                                                              |
    """
    id: Optional[int] = Field(None, description="The Xandr ID assigned by the API to reference the segment.")
    code: Optional[str] = Field(None, max_length=50, description="The user-defined code for calling the segment. Case-sensitive in query string targeting.")
    state: Optional[SegmentState] = Field(SegmentState.ACTIVE, description="The state of the segment. Possible values: active or inactive.")
    short_name: Optional[str] = Field(None, max_length=255, description="The short name used to describe the segment.")
    description: Optional[str] = Field(None, max_length=500, description="The optional description for this segment. Restricted characters: ' \\")
    member_id: Optional[int] = Field(None, description="The ID of the member that owns this segment.")
    category: Optional[str] = Field(None, description="Deprecated. This field is read-only.")
    expire_minutes: Optional[int] = Field(None, description="The number of minutes the user is kept in the segment. Set to null for 180-day maximum.")
    enable_rm_piggyback: Optional[bool] = Field(None, description="If true, piggybacking RM pixels is enabled.")
    max_usersync_pixels: Optional[int] = Field(0, description="The maximum number of third-party user sync pixels to piggyback onto the segment pixel.")
    last_modified: Optional[str] = Field(None, description="The date and time when the segment was last modified.")
    provider_id: Optional[int] = Field(None, description="The ID of the data provider that owns the segment. Read-only.")
    advertiser_id: Optional[int] = Field(None, description="The ID of the advertiser using the segment if it should be on the Advertiser level.")
    piggyback_pixels: Optional[List[PiggybackPixel]] = Field(None, description="The URLs of the pixels to fire when the segment pixel fires.")
    price: Optional[float] = Field(0.0, description="Deprecated. This field is currently not operational.")
    parent_segment_id: Optional[int] = Field(None, description="The ID of the parent segment. Deprecated since January 1, 2019.")
    querystring_mapping: Optional[QueryStringMapping] = Field(None, description="A query string to assign a set of parameters and values to a segment.")
    querystring_mapping_key_value: Optional[QueryStringMappingKeyValue] = Field(None, description="A query string to reuse a key and assign a single key-value pair to a segment.")
