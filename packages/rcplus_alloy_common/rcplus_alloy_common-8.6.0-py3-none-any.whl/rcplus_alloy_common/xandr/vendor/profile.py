# ruff: noqa: E501
"""
Microsoft Xandr API doesn't have any formal specifications. Code below is based on its documentation:
https://learn.microsoft.com/en-us/xandr/digital-platform-api/profile-service
"""
from __future__ import annotations
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class GraphId(int, Enum):
    NO_GRAPH = 0
    TAPAD_GRAPH = 3
    XANDR_GRAPH = 4


class EngagementRateType(str, Enum):
    VIDEO_COMPLETION = "video_completion"
    VIEW = "view"
    VIEW_OVER_TOTAL = "view_over_total"
    PREDICTED_IAB_VIDEO_VIEW_RATE = "predicted_iab_video_view_rate"
    PREDICTED_IAB_VIDEO_VIEW_RATE_OVER_TOTAL = "predicted_iab_video_view_rate_over_total"
    PREDICTED_100PV50PD_VIDEO_VIEW_RATE = "predicted_100pv50pd_video_view_rate"
    PREDICTED_100PV50PD_VIDEO_VIEW_RATE_OVER_TOTAL = "predicted_100pv50pd_video_view_rate_over_total"
    PREDICTED_100PV1S_DISPLAY_VIEW_RATE = "predicted_100pv1s_display_view_rate"
    PREDICTED_100PV1S_DISPLAY_VIEW_RATE_OVER_TOTAL = "predicted_100pv1s_display_view_rate_over_total"


class Action(str, Enum):
    INCLUDE = "include"
    EXCLUDE = "exclude"


class Operator(str, Enum):
    AND = "and"
    OR = "or"


class Gender(str, Enum):
    MALE = "m"
    FEMALE = "f"


class Day(str, Enum):
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    ALL = "all"


class DomainListType(str, Enum):
    BLACK = "black"
    WHITE = "white"


class Trust(str, Enum):
    SELLER = "seller"
    APPNEXUS = "appnexus"


class SessionFreqType(str, Enum):
    PLATFORM = "platform"
    PUBLISHER = "publisher"


class IntendedAudienceTarget(str, Enum):
    GENERAL = "general"
    CHILDREN = "children"
    YOUNG_ADULT = "young_adult"
    MATURE = "mature"


class SupplyTypeTarget(str, Enum):
    WEB = "web"
    MOBILE_WEB = "mobile_web"
    MOBILE_APP = "mobile_app"


class Position(str, Enum):
    ABOVE = "above"
    BELOW = "below"


class DeviceTypeTarget(str, Enum):
    phone = "phone"
    tablet = "tablet"
    pc = "pc"
    tv = "tv"
    gameconsole = "gameconsole"
    stb = "stb"
    mediaplayer = "mediaplayer"


class ListType(str, Enum):
    ALLOWLIST = "allowlist"
    BLOCKLIST = "blocklist"
    BLACKLIST = "blacklist"


class ExpOperator(str, Enum):
    AND = "and"
    OR = "or"
    NOT = "not"
    IN = "in"
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    NEQ = "neq"


class ExpValueType(str, Enum):
    num = "num"
    str = "str"
    nma = "nma"
    sta = "sta"


class DaypartTarget(BaseModel):
    """
    | Field      | Type | Description                                                                                                                                                            |
    |------------|------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | day        | enum | The day of the week. Possible values: sunday, monday, tuesday, wednesday, thursday, friday, saturday, or all. Note: These strings must be in lower case.               |
    | start_hour | int  | The start hour for the daypart. This must be an integer between 0 and 23. The campaign will start serving at the beginning of the hour (6 is equivalent to "6:00" am). |
    | end_hour   | int  | The end hour for the daypart. This must be an integer between 0 and 23. The campaign will stop serving at the end of the hour (23 is equivalent to "23:59").           |
    """
    day: Optional[Day] = Field(None, description="The day of the week. Must be one of: sunday, monday, tuesday, wednesday, thursday, friday, saturday, or all.")
    start_hour: Optional[int] = Field(None, ge=0, le=23, description="The start hour for the daypart. Must be an integer between 0 and 23.")
    end_hour: Optional[int] = Field(None, ge=0, le=23, description="The end hour for the daypart. Must be an integer between 0 and 23.")


class SegmentTarget(BaseModel):
    """
    | Field          | Type   | Description                                                                                               |
    |----------------|--------|-----------------------------------------------------------------------------------------------------------|
    | id             | int    | The ID of the segment.Required On: POST                                                                   |
    | code           | string | The custom code for the segment.                                                                          |
    | action         | enum   | Possible values: include or exclude.Default: include                                                      |
    | start_minutes  | int    | The lower bound for the amount of time since a user was added to the segment.Default: 0                   |
    | expire_minutes | int    | The upper bound for the amount of time since a user was added to the segment.Default: -1                  |
    | other_equals   | int    | The exact segment value to target.Note: If you use other_in_list, you cannot use this field.Default: null |
    | other_less     | int    | The non-inclusive upper bound for segment value targeting.Default: null                                   |
    | other_greater  | int    | The non-inclusive lower bound for segment value targeting.Default: null                                   |
    | other_in_list  | array  | The list of segment values to target.If you use other_equals, you cannot use this field.Default: null     |
    """
    id: Optional[int] = Field(None, description="The ID of the segment. Required On: POST.")
    code: Optional[str] = Field(None, description="The custom code for the segment.")
    action: Optional[Action] = Field(None, description="Possible values: include or exclude. Default: include.")
    start_minutes: Optional[int] = Field(None, ge=0, description="The lower bound for the amount of time since a user was added to the segment. Default: 0.")
    expire_minutes: Optional[int] = Field(None, description="The upper bound for the amount of time since a user was added to the segment. Default: -1.")
    other_equals: Optional[int] = Field(None, description="The exact segment value to target. Note: If you use other_in_list, you cannot use this field. Default: null.")
    other_less: Optional[int] = Field(None, description="The non-inclusive upper bound for segment value targeting. Default: null.")
    other_greater: Optional[int] = Field(None, description="The non-inclusive lower bound for segment value targeting. Default: null.")
    other_in_list: Optional[List[int]] = Field(None, description="The list of segment values to target. If you use other_equals, you cannot use this field. Default: null.")


class SegmentGroupTarget(BaseModel):
    """
    | Field            | Type   | Description                                                                                                                                                                                                                                                                                                                  |
    |------------------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | boolean_operator | enum   | The boolean logic between segments in a segment group. Possible values: and or or. The value of boolean_operator field for all objects in the segment_group_targets array needs to be same.In short, you cannot have boolean_operator of one object as "and" and other as "or" in the same profile.Default: orRequired: POST |
    | id               | int    | The ID of the segment.Required: POST                                                                                                                                                                                                                                                                                         |
    | code             | string | The custom code for the segment.                                                                                                                                                                                                                                                                                             |
    | action           | enum   | Possible values: include or exclude.Default: include                                                                                                                                                                                                                                                                         |
    | start_minutes    | int    | The lower bound for the amount of time since a user was added to the segment.Default: 0                                                                                                                                                                                                                                      |
    | expire_minutes   | int    | The upper bound for the amount of time since a user was added to the segment.Default: -1                                                                                                                                                                                                                                     |
    | other_equals     | string | The exact segment value to target.Note: If you use other_in_list, you cannot use this field.Default: null                                                                                                                                                                                                                    |
    | other_less       | int    | The non-inclusive upper bound for segment value targeting.Default: null                                                                                                                                                                                                                                                      |
    | other_greater    | int    | The non-inclusive lower bound for segment value targeting.Default: null                                                                                                                                                                                                                                                      |
    | other_in_list    | array  | The list of segment values to target.Note: If you use other_equals, you cannot use this field.Default: null                                                                                                                                                                                                                  |
    """
    boolean_operator: Optional[Operator] = Field(None, description="The boolean logic between segments in a segment group. Possible values: and or or. Default: or. Required: POST.")
    id: Optional[int] = Field(None, description="The ID of the segment. Required: POST.")
    code: Optional[str] = Field(None, description="The custom code for the segment.")
    action: Optional[Action] = Field(None, description="Possible values: include or exclude. Default: include.")
    start_minutes: Optional[int] = Field(None, ge=0, description="The lower bound for the amount of time since a user was added to the segment. Default: 0.")
    expire_minutes: Optional[int] = Field(None, description="The upper bound for the amount of time since a user was added to the segment. Default: -1.")
    other_equals: Optional[str] = Field(None, description="The exact segment value to target. Note: If you use other_in_list, you cannot use this field. Default: null.")
    other_less: Optional[int] = Field(None, description="The non-inclusive upper bound for segment value targeting. Default: null.")
    other_greater: Optional[int] = Field(None, description="The non-inclusive lower bound for segment value targeting. Default: null.")
    other_in_list: Optional[List[int]] = Field(None, description="The list of segment values to target. Note: If you use other_equals, you cannot use this field. Default: null.")


class AgeRange(BaseModel):
    low: Optional[int] = Field(None, ge=13, description="The lower bound of the age range (min 13).")
    high: Optional[int] = Field(None, le=100, description="The upper bound of the age range (max 100).")


class AgeTarget(BaseModel):
    allow_unknown: Optional[bool] = Field(None, description="Determines whether to include targets where age is not know.")
    ages: Optional[List[AgeRange]] = Field(None, description="The age ranges targeted in this profile.")


class GenderTarget(BaseModel):
    gender: Optional[Gender] = Field(None, description="The gender of the user. Possible values: m (male), or f (female).")
    allow_unknown: Optional[bool] = Field(None, description="If true, target ad calls where the gender of the user is not available.")


class CountryTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the country. You can use the Country Service to retrieve a complete list of country IDs.")
    name: Optional[str] = Field(None, description="Read-only. The name of the country.")
    code: Optional[str] = Field(None, description="Read-only. The code for the country.")


class RegionTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the region. You can use the Region Service to retrieve a list of region IDs.")
    name: Optional[str] = Field(None, description="Read-only. The name of the region.")
    code: Optional[str] = Field(None, description="Read-only. The code for the region.")
    country_name: Optional[str] = Field(None, description="Read-only. The name of the country to which the region belongs.")
    country_code: Optional[str] = Field(None, description="Read-only. The code for the country to which the region belongs.")


class DmaTarget(BaseModel):
    dma: Optional[int] = Field(None, description="The ID of designated market area. You can use the Designated Market Area Service to retrieve a list of DMA IDs.")


class CityTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the city to target. You can use the City Service to retrieve a list of city IDs.")
    name: Optional[str] = Field(None, description="Read-only. The name of the city to target.")
    region_name: Optional[str] = Field(None, description="Read-only. The name of the region to which the city belongs.")
    region_code: Optional[str] = Field(None, description="Read-only. The code of the region to which the city belongs.")
    country_name: Optional[str] = Field(None, description="Read-only. The name of the country to which the region belongs.")
    country_code: Optional[str] = Field(None, description="Read-only. The code of the country to which the region belongs.")


class DomainTarget(BaseModel):
    profile_id: Optional[int] = Field(None, description="The profile ID associated with the domain.")
    domain: Optional[str] = Field(None, description="The domain name.")


class DomainListTarget(BaseModel):
    """
    | Field         | Type        | Description                                                                                                                                                                                                                                                                                              |
    |---------------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | description   | string(100) | A description of the domain list.                                                                                                                                                                                                                                                                        |
    | domains       | array       | Array of domains in the format ["domain1.com", "domain2.com", ... , "domain10.com"].Note: "www" is stripped from domains.Domains which begin with "www" will have the "www" substring stripped out before being stored in our system. For example, "www.example.org" will be shortened to "example.org". |
    | id            | int         | The internal system identifier for the domain list.Required On: PUT                                                                                                                                                                                                                                      |
    | last_modified | string      | Read-only timestamp of when the domain list was last changed.                                                                                                                                                                                                                                            |
    | name          | string(100) | The name of the domain list as specified by the user. This name must be unique.Required On: POST                                                                                                                                                                                                         |
    | type          | string      | The type of domain list. Possible values are black and white. This value is strictly informational; it does not determine whether the list is included or excluded in targeting.Default: "white"                                                                                                         |
    """
    id: Optional[int] = Field(None, description="The internal system identifier for the domain list. Required On: PUT.")
    name: Optional[str] = Field(None, max_length=100, description="The name of the domain list as specified by the user. This name must be unique. Required On: POST.")
    description: Optional[str] = Field(None, max_length=100, description="A description of the domain list.")
    domains: Optional[List[str]] = Field(None, description='Array of domains in the format ["domain1.com", "domain2.com", ... , "domain10.com"]. "www" is stripped from domains.')
    last_modified: Optional[str] = Field(None, description="Read-only timestamp of when the domain list was last changed.")
    type: Optional[DomainListType] = Field(None, description='The type of domain list. Possible values are black and white. Default: "white".')


class SizeTarget(BaseModel):
    width: Optional[int] = Field(None, description="The width of the size target.")
    height: Optional[int] = Field(None, description="The height of the size target.")


class SellerMemberGroupTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the seller member group target.")
    action_include: Optional[bool] = Field(None, description="The action include flag.")


class MemberTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the member target.")
    action: Optional[Action] = Field(None, description="The action for the member target.")
    third_party_auditor_id: Optional[int] = Field(None, description="The ID of the third-party auditor, if applicable.")
    billing_name: Optional[str] = Field(None, description="The billing name associated with the member target.")


class VideoTarget(BaseModel):
    allow_unknown_playback_method: Optional[bool] = Field(None, description="Use this field to target inventory where the playback method is unknown.")
    allow_unknown_context: Optional[bool] = Field(None, description="Use this field to target inventory where the context is unknown.")
    allow_unknown_player_size: Optional[bool] = Field(None, description="Use this field to target inventory where the player size is unknown.")


class EngagementRateTarget(BaseModel):
    engagement_rate_type: Optional[EngagementRateType] = Field(None, description="The targeting criteria.")
    engagement_rate_pct: Optional[int] = Field(None, ge=1, le=100, description="Engagement rate PCT")


class PublisherTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the publisher target.")
    action: Optional[Action] = Field(None, description="The action for the publisher target.")


class SiteTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the site target.")


class PlacementTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the placement target.")


class ContentCategory(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the content category.")
    action: Optional[Action] = Field(None, description="The action for the content category.")


class ContentCategoryTargets(BaseModel):
    allow_unknown: Optional[bool] = Field(None, description="Flag indicating whether unknown content categories are allowed.")
    content_categories: Optional[List[ContentCategory]] = Field(None, description="List of content categories with their actions.")


class DealTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the deal. To retrieve the IDs of your deals, use the Deal Buyer Access Service.")
    name: Optional[str] = Field(None, description="Read-only. The name of the deal.")
    code: Optional[str] = Field(None, description="Read-only. The custom code for the deal. For deals with external supply partners, this is generally the string that you will use to identify the deal.")


class DealListTarget(BaseModel):
    id: Optional[str] = Field(None, description="The ID of the deal list.")


class PlatformPublisherTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the platform publisher target.")
    action: Optional[Action] = Field(None, description="The action for the platform publisher target.")
    name: Optional[str] = Field(None, description="The name of the platform publisher target.")
    deleted: Optional[bool] = Field(None, description="Flag indicating whether the platform publisher target is deleted.")


class InventoryAttributeTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the inventory attribute target.")
    name: Optional[str] = Field(None, description="The name of the inventory attribute target.")
    deleted: Optional[bool] = Field(None, description="Flag indicating whether the inventory attribute target is deleted.")


class LanguageTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the language target.")
    name: Optional[str] = Field(None, description="The name of the language target.")
    code: Optional[str] = Field(None, description="The code of the language target, e.g., 'EN'.")
    deleted: Optional[bool] = Field(None, description="Flag indicating whether the language target is deleted.")


class PostalCodeTarget(BaseModel):
    id: Optional[str | int] = Field(None, description="Postal code ID.")
    code: Optional[str] = Field(None, description="Postal code.")
    country_id: Optional[int] = Field(None, description="Postal code country ID.")
    active: Optional[bool] = Field(None, description="Postal code status.")


class PostalCodeListTarget(BaseModel):
    id: Optional[str] = Field(None, description="Postal code list ID.")


class Group(BaseModel):
    low: Optional[int] = Field(None, description="The lower bound of the group range.")
    high: Optional[int] = Field(None, description="The upper bound of the group range.")


class UserGroupTarget(BaseModel):
    include_cookieless_users: Optional[bool] = Field(None, description="Flag indicating whether cookieless users are included.")
    groups: Optional[List[Group]] = Field(None, description="List of groups with their range bounds.")


class PositionTarget(BaseModel):
    allow_unknown: Optional[bool] = Field(None, description="Flag indicating whether unknown positions are allowed.")
    positions: Optional[List[Position]] = Field(None, description="List of positions.")


class BrowserTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the browser target.")
    name: Optional[str] = Field(None, description="The name of the browser target.")
    deleted: Optional[bool] = Field(None, description="Flag indicating whether the browser target is deleted.")


class DeviceModelTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the device model target.")
    name: Optional[str] = Field(None, description="The name of the device model target.")


class CarrierTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the carrier target.")
    name: Optional[str] = Field(None, description="The name of the carrier target.")
    country: Optional[str] = Field(None, description="The country associated with the carrier target.")


class InventoryUrlListTarget(BaseModel):
    deleted: Optional[bool] = Field(None, description="Flag indicating whether the inventory URL list target is deleted.")
    id: Optional[int] = Field(None, description="The ID of the inventory URL list target.")
    list_type: Optional[ListType] = Field(None, description="The type of the list, e.g., 'blocklist'.")
    name: Optional[str] = Field(None, description="The name of the inventory URL list target.")
    exclude: Optional[bool] = Field(None, description="Flag indicating whether the list is used to exclude items.")


class OperatingSystemFamilyTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the operating system family target.")
    name: Optional[str] = Field(None, description="The name of the operating system family target.")


class OperatingSystemExtendedTarget(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the operating system extended target.")
    name: Optional[str] = Field(None, description="The name of the operating system extended target.")
    action: Optional[Action] = Field(None, description="The action for the operating system extended target, e.g., 'exclude'.")


class MobileAppInstanceTarget(BaseModel):
    id: Optional[int] = Field(None, description="The unique ID of the mobile app instance.")
    bundle_id: Optional[str] = Field(None, description="The bundle ID of this mobile app instance.")
    os_family_id: Optional[int] = Field(None, description="The OS family ID associated with this mobile app instance.")


class MobileAppInstanceListTarget(BaseModel):
    id: Optional[int] = Field(None, description="The unique ID of the mobile app instance list.")
    name: Optional[str] = Field(None, description="The name of this mobile app instance list.")
    description: Optional[str] = Field(None, description="An optional description of the list's purpose or contents.")


class IpRangeListModel(BaseModel):
    id: Optional[int] = Field(None, description="The unique ID of this IP range list.")
    name: Optional[str] = Field(None, description="Read-only. The name of this IP range list.")
    include: Optional[bool] = Field(None, description="Read-only. Whether to include or exclude the IP ranges in the IP range list.")
    description: Optional[str] = Field(None, description="Read-only. An optional description of the list's purpose or contents.")


class Header(BaseModel):
    an_version: Optional[str] = Field(None, description="The version of the back-end engine evaluating the expression. Current version is 1.0. This field is required on PUT and POST.")
    client_version: Optional[str] = Field(None, description="The version of the client-facing implementation of the expression (the format shown in the example below). Current version is 1.0. This field is required on PUT and POST.")


class Exp(BaseModel):
    typ: Optional[ExpOperator] = Field(None, description="The operators used in the expression. Possible values include: and, or, not, in, eq, gt, lt, gte, lte, neq. Operators and, or, and not can be used only with sub-expressions. Operators gt, lt, gte, and lte can be used only with numeric values. All operators must be lowercase.")
    sbe: Optional[Exp | List[Exp]] = Field(None, description="An object containing the sub-expression (the elements of the expression).")
    key: Optional[str] = Field(None, description="The name of the targeting key.")
    vtp: Optional[ExpValueType] = Field(None, description="This field identifies the data type of the expression value. Valid values: num, str, nma, sta.")
    vnm: Optional[float] = Field(None, description="The value as a 32-bit signed float. Numbers can be up to 13 digits (with a maximum of six digits to the right of the decimal point).")
    vst: Optional[str] = Field(None, description="The value as a string.")
    vna: Optional[List[float]] = Field(None, description="A set of values as an array of floats.")
    vsa: Optional[List[str]] = Field(None, description="A set of values as an array of strings.")


class KvExpression(BaseModel):
    header: Optional[Header] = Field(None, description="Versioning information used to evaluate the expression.")
    exp: Optional[Exp] = Field(None, description="The regular expression that defines the combination of key/values.")


class KeyValueTarget(BaseModel):
    kv_expression: Optional[KvExpression] = Field(None, description="This is a wrapper object that contains all the key/value targeting objects, including the header and exp objects.")


class InventoryUrlAllowlistSettings(BaseModel):
    apply_to_managed: Optional[bool] = Field(None, description="Flag indicating whether the allowlist applies to managed inventory.")
    apply_to_rtb: Optional[bool] = Field(None, description="Flag indicating whether the allowlist applies to RTB inventory.")


class PoliticalDistrictTarget(BaseModel):
    id: Optional[str] = Field(None, description="The ID of the political district target.")


class Profile(BaseModel):
    """
    | Field                                             | Type                         | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    |---------------------------------------------------|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | id                                                | int                          | The ID of the profile.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
    | code                                              | string                       | Custom code for the profile.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
    | description                                       | string                       | Optional description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
    | is_template                                       | Boolean                      | If true, the profile has been saved as a targeting template in.                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
    | last_modified                                     | timestamp                    | Time of last modification to this profile.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | is_archived                                       | boolean                      | Read-only. Indicates whether the profile has been automatically archived due to its parent line item not being used (and therefore, having been archived).                                                                                                                                                                                                                                                                                                                                                                    |
    | archived_on                                       | timestamp                    | Read-only. The date and time on which the profile was archived (i.e., when the is_archived field was set to true).                                                                                                                                                                                                                                                                                                                                                                                                            |
    | max_lifetime_imps                                 | int                          | The maximum number of impressions per person. If set, this value must be between 0 and 255. Default: null                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | min_session_imps                                  | int                          | The minimum number of impressions per person per session. If set, this value must be between 0 and 255. Default: null                                                                                                                                                                                                                                                                                                                                                                                                         |
    | max_session_imps                                  | int                          | The maximum number of impressions per person per session. If set, this value must be between 0 and 255. Default: null                                                                                                                                                                                                                                                                                                                                                                                                         |
    | max_day_imps                                      | int                          | The maximum number of impressions per person per day. If set, this value must be between 0 and 255. Default: null                                                                                                                                                                                                                                                                                                                                                                                                             |
    | max_hour_imps                                     | int                          | The maximum number of impressions per person per hour. If set, this value must be between 0 and 255. Default: null                                                                                                                                                                                                                                                                                                                                                                                                            |
    | max_week_imps                                     | int                          | The maximum number of impressions per person per week. If set, this value must be between 0 and 255. Default: null                                                                                                                                                                                                                                                                                                                                                                                                            |
    | max_month_imps                                    | int                          | The maximum number of impressions per person per month. If set, this value must be between 0 and 255. Default: null                                                                                                                                                                                                                                                                                                                                                                                                           |
    | min_minutes_per_imp                               | int                          | The minimum number of minutes between impressions per person. This field may not be set to 0. Default: null                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | max_page_imps                                     | int                          | The maximum number of impressions per page load (seller's ad request).Note: Only relevant for multi-tag auctions. Default: null                                                                                                                                                                                                                                                                                                                                                                                               |
    | require_cookie_for_freq_cap                       | Boolean                      | Indicates whether you'll exclusively serve to users with known identifiers to maintain your frequency cap settings.                                                                                                                                                                                                                                                                                                                                                                                                           |
    | graph_id                                          | int                          | - Null if the line item is targeting your member seat's default graph selection.  - 0 if the line item is targeting no graph.  - 3 if the line item is targeting the TapAd Graph.- 4 if the line item is targeting the Xandr Graph.                                                                                                                                                                                                                                                                                           |
    | daypart_timezone                                  | string                       | The timezone to be used with the daypart_targets. For more details, see API Timezones.Note: null is equivalent to the user's timezone.Default: null                                                                                                                                                                                                                                                                                                                                                                           |
    | daypart_targets                                   | array of objects             | The day parts during which to serve the campaign. For more details, see Daypart Targets below. Note: If you do not set any daypart targets, the campaign will serve on all days of the week at all times.                                                                                                                                                                                                                                                                                                                     |
    | segment_targets                                   | array of objects             | Note: If you use segment_targets and edit the associated campaign in our UI, the segments will be converted to a group in the segment_group_targets array. Therefore, it's recommended to use segment_group_targets when working via the API.The segment IDs to target, each of which has an associated action (include or exclude). You define the Boolean logic between segments with the segment_boolean_operator field outside of the array. For more details, see Segment Targets and example below.                     |
    | segment_group_targets                             | array of objects             | The segment groups to target. Whereas the segment_targets array allows you to define Boolean logic between individual segments, this array allows you to establish groups of segments, defining Boolean logic between the groups as well as between the segments within each group.                                                                                                                                                                                                                                           |
    | segment_boolean_operator                          | enum                         | If using segment_targets, this defines the Boolean logic between the segments specified. If using segment_group_targets, this defines the Boolean logic between the segment groups (the Boolean logic between segments in a group is defined directly in the segment_group_targets array).Possible values: and or or.Default: and                                                                                                                                                                                             |
    | age_targets                                       | array of objects             | The list of age ranges to target for this profile. The allow_unknown field is available as a Boolean in order to account for ad calls where the age of the user is not available. For more description and examples, see the Age Targets section below.                                                                                                                                                                                                                                                                       |
    | gender_targets                                    | object                       | The gender targeting used for the profile. Possible values for gender are m or f. The allow_unknown field is available as a Boolean in order to account for ad calls where the gender of the user is not available. See the Gender Targets section below.                                                                                                                                                                                                                                                                     |
    | country_targets                                   | array of objects             | The country IDs to be either excluded or included in a profile, as defined by the country_action field. You can use the Country Service to retrieve a list of country IDs. For more details and format, see Country Targets.Required: POST/PUT, when country_action is include.                                                                                                                                                                                                                                               |
    | country_action                                    | enum                         | Action to be taken on the country_targets list. Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                          |
    | region_targets                                    | array of objects             | The region/state IDs to be either excluded or included in a profile, as defined by the region_action field. You can use the Region Service to retrieve a list of region IDs. For more details and format, see Region Targets below.Required On: POST/PUT, when region_action is include.                                                                                                                                                                                                                                      |
    | require_transparency_and_consent_framework_string | boolean                      | - If true, only allow associated objects to purchase inventory where valid TCF string is present.- If false, allow associated objects to purchase any inventory that falls within pre-defined targeting declarations.- This is only supported on advertiser level as targeting at other levels may lead to undefined behavior.Note: This parameter is only applicable to the traffic coming from territories where GDPR applies.Default: false                                                                                |
    | region_action                                     | enum                         | Action to be taken on the region_targets list.Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                            |
    | dma_targets                                       | array of objects             | The IDs of designated market areas to be either excluded or included in a profile, as defined by the dma_action field. You can use the Designated Market Area Service to retrieve a list of DMA IDs. See format example.                                                                                                                                                                                                                                                                                                      |
    | dma_action                                        | enum                         | Action to be taken on the dma_targets list.Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                               |
    | city_targets                                      | array of objects             | The IDs of cities to be either included or excluded in a profile, as defined by the city_action field. You can use the City Service to retrieve a list of city IDs. For more details and format, see City Targets below.Required On: POST/PUT, when city_action is include.                                                                                                                                                                                                                                                   |
    | city_action                                       | enum                         | Action to be taken on the city_targets list. Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                             |
    | domain_targets                                    | array of objects             | List of domains to be either included or excluded in a profile, as defined by the domain_action field. For format, see the example below.                                                                                                                                                                                                                                                                                                                                                                                     |
    | domain_action                                     | enum                         | Action to be taken on the domain_targets list. For details on domains, see the Create a Domain or App List in documentation.Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                              |
    | domain_list_targets                               | array of objects             | The IDs of domains lists to either include or exclude in a profile, as defined by the domain_list_action field. You can use the Domain List Service to retrieve domain list IDs. See the example below for format.Note: You can use no more than 100 domain lists in a single profile.                                                                                                                                                                                                                                        |
    | domain_list_action                                | enum                         | Action to be taken on the domain_list_targets list. For details on domains, see Working with Targeting Lists in documentation. Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                           |
    | platform_placement_targets                        | array of objects             | RTB or other Networks' inventory you can target. You can use Inventory Resold or Reporting services to find platform placements.                                                                                                                                                                                                                                                                                                                                                                                              |
    | size_targets                                      | array of objects             | List of eligible sizes to be included in the profile.The sizes are in an array size objects, each object containing the width and height of each target size. See example below.Note: When you enable roadblocking on a guaranteed line item, this value is combined with creative sizes on the line item and campaign to produce forecasting. The size with the lowest forecasted number of impressions will be returned as the forecasted capacity.                                                                         |
    | seller_member_group_targets                       | array of objects             | The seller member groups to be excluded or included in a profile. To target Xandr's direct supply, see the format below.                                                                                                                                                                                                                                                                                                                                                                                                      |
    | member_targets                                    | array of objects             | Seller member IDs to be either excluded or included in a profile. The specific format can be found in the example at the bottom of the page.                                                                                                                                                                                                                                                                                                                                                                                  |
    | video_targets                                     | object                       | Video target IDs to be included in a profile. For the specific format, see Video Targets below.                                                                                                                                                                                                                                                                                                                                                                                                                               |
    | engagement_rate_targets                           | array of objects             | Target specific, highly performant inventory based on historic performance. For details, see Engagement Rate Targets below.Default: null                                                                                                                                                                                                                                                                                                                                                                                      |
    | publisher_targets                                 | array of objects             | Managed/direct publisher IDs to be either excluded or included in a profile.                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
    | site_targets                                      | array of objects             | The sites IDs to be either excluded or included in a profile. Exclude or include is inherited from the publisher_targets field.Default: If you do not provide action with site_targets, action will default to NULL and profile.inventory_action will be used.                                                                                                                                                                                                                                                                |
    | placement_targets                                 | array of objects             | The placement IDs to be either excluded or included in a profile. Exclude or include is inherited from the publisher_targets field.Default: If you do not provide action with placement_targets, action will default to NULL and profile.inventory_action will be used.                                                                                                                                                                                                                                                       |
    | inventory_action                                  | enum                         | Action to be taken on the inventory_targets, publisher_targets, site_targets, and placement_targets list. Possible values: include or exclude. If action is include, then any targeted publisher, site, or placement will be included.Default: exclude                                                                                                                                                                                                                                                                        |
    | content_category_targets                          | object with string and array | The content categories to target for this profile as well as whether to allow unknown categories. For more details and format, see Content Category Targets below. To retrieve content category IDs, use the Content Category Service.                                                                                                                                                                                                                                                                                        |
    | deal_targets                                      | array of objects             | The deal IDs to be targeted by this profile. A deal is an agreement between a seller and buyer that may provide the buyer preferential pricing, access to exclusive inventory, reduced competition on inventory, or other opportunities. For more details and format, see Deal Targets below.For more information on how the value of this field and the deal_action_include field affect targeting results, see Targeting Results for deal_action_include AND deal_targets fields below.                                     |
    | deal_list_targets                                 | array of objects             | The deal list IDs to be targeted by this profile. See example below.Deal list IDs can be fetched using the Deal List Service.                                                                                                                                                                                                                                                                                                                                                                                                 |
    | platform_publisher_targets                        | array of objects             | Third party publisher IDs to be either excluded or included in a profile. For a list of IDs the Inventory Resold Service.                                                                                                                                                                                                                                                                                                                                                                                                     |
    | platform_content_category_targets                 | array of objects             | List of network resold content categories to target for this profile. For a list of IDs, see the Inventory Resold Service.                                                                                                                                                                                                                                                                                                                                                                                                    |
    | use_inventory_attribute_targets                   | Boolean                      | If true, the profile will allow inventory that has the sensitive attributes included in inventory_attribute_targets.Default: false                                                                                                                                                                                                                                                                                                                                                                                            |
    | trust                                             | enum                         | Indicates the level of audit which inventory must meet in order to be eligible.Possible values: appnexus or "seller". If this field is set to "appnexus", the allow_unaudited field must be set to false.Default: seller                                                                                                                                                                                                                                                                                                      |
    | allow_unaudited                                   | Boolean                      | If true, this profile will allow unaudited inventory to pass targeting. If the trust field is set to appnexus, this must be set to false.Note:- This setting overrides the seller trust settings in the inventory_trust object of the Member Service.- For Programmatic Guaranteed Buying Line Items, allow_unaudited must be set to true.Default: false                                                                                                                                                                      |
    | session_freq_type                                 | enum                         | Indicates how the number of impressions seen by the user are counted during the current browsing session. Possible values: platform (across all publishers in the current session) or publisher (for the specific publisher).Default: platform                                                                                                                                                                                                                                                                                |
    | inventory_attribute_targets                       | array of objects             | The IDs of inventory attributes to target for this profile. You can use the Inventory Attribute Service to retrieve a list of IDs.                                                                                                                                                                                                                                                                                                                                                                                            |
    | intended_audience_targets                         | array of strings             | The intended audience targets. Possible values: general, children, young_adult, or mature. Note: You can only choose to include (not exclude) intended audience targets.See example.Note: To use the intended audience targeting, default_trust under inventory_trust (an attribute under the member) must be set to seller. Without this setting, the intended audience targeting will not be applied.                                                                                                                       |
    | language_targets                                  | array of objects             | The IDs of the browser languages to either include or exclude in the profile, as defined by the language_action field. You can use the Language Service to retrieve language IDs.                                                                                                                                                                                                                                                                                                                                             |
    | language_action                                   | enum                         | Action to be taken on language_targets. Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                                  |
    | querystring_targets                               | array of objects             | The query string targets to either include or exclude in the profile, as defined by the querystring_action field.                                                                                                                                                                                                                                                                                                                                                                                                             |
    | querystring_action                                | enum                         | Action to be taken on the querystring_targets. Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                           |
    | querystring_boolean_operator                      | enum                         | Boolean logic to be applied to the querystring_targets. Possible values: and or or.Default: and                                                                                                                                                                                                                                                                                                                                                                                                                               |
    | postal_code_targets                               | array of objects             | The postal code IDs to target. See example.IDs can be fetched using the Postal Code Service.                                                                                                                                                                                                                                                                                                                                                                                                                                  |
    | postal_code_list_targets                          | array of objects             | The postal code list IDs to target. See example.IDs can be fetched using the Postal Code List Service.                                                                                                                                                                                                                                                                                                                                                                                                                        |
    | postal_code_action_include                        | boolean                      | Whether to include the postal codes defined in postal_code_targets, postal code lists defined in postal_code_list_targets in your targeting, and political districts defined in political_district_targets.Default: true                                                                                                                                                                                                                                                                                                      |
    | zip_targets                                       | array of objects             | Deprecated. Use postal_code_targets instead.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
    | supply_type_targets                               | array of strings             | The type(s) of supply to either include in or exclude from targeting, as defined by the supply_type_action field. Possible values: web, mobile_web and mobile_app.Note: The facebook_sidebar option has been deprecated.                                                                                                                                                                                                                                                                                                      |
    | supply_type_action                                | enum                         | Supply types are web, mobile_web, and mobile_app. Possible values: include or exclude. If this field is set to include, only inventory of types included in supply_type_targets will be targeted. If exclude, only inventory not in supply_type_targets will be targeted (except facebook_sidebar, which has been deprecated).Default: exclude                                                                                                                                                                                |
    | user_group_targets                                | object                       | Every user is randomly assigned to 1 of 100 user groups, no group holding any advantage over another. You can use this field to target a specific range of these user groups. Also, you can use the include_cookieless_users field to include or exclude users without cookies. For formatting, see the View a profile example below.                                                                                                                                                                                         |
    | position_targets                                  | object                       | The fold positions to target. For more details, see Position Targets below.                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | browser_targets                                   | array of objects             | The IDs of browsers to either include in or exclude from your targeting, as defined by the browser_action field. You can use the Browser Service to retrieve a list of browser IDs. For the format, see the example below.                                                                                                                                                                                                                                                                                                    |
    | browser_action                                    | enum                         | Action to be taken on the browser_targets. Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                               |
    | location_target_latitude                          | double                       | The latitude of the user's location. This must be between -90 and 90, with up to 6 decimal places, where south is negative and north is positive. A profile can be targeted to a specific location when GPS data is available from a mobile device. When lat/long targeting is set, users will only be targeted within the area defined by the center (location_target_latitude, location_target_longitude) and radius location_target_radius. Users will not be targeted when GPS data is not available for the impression.  |
    | location_target_longitude                         | double                       | The longitude of the user's location. This must be between -180 and 180, with up to 6 decimal places, where west is negative and east is positive. A profile can be targeted to a specific location when GPS data is available from a mobile device. When lat/long targeting is set, users will only be targeted within the area defined by the center (location_target_latitude, location_target_longitude) and radius location_target_radius. Users will not be targeted when GPS data is not available for the impression. |
    | location_target_radius                            | integer length in meters     | For more information, see location_target_latitude.                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
    | device_model_targets                              | array of objects             | The models of mobile devices (i.e., iPhone) to either include in or exclude from your targeting, as defined by the device_model_action field. To retrieve a complete list of device models registered in our system, use the read-only Device Model Service. For more details and format, see Device Model Targets below.                                                                                                                                                                                                     |
    | device_model_action                               | enum                         | Action to be taken on device_model_targets. Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                              |
    | device_type_targets                               | array of strings             | The types of devices to either include in or exclude from your targeting, as defined by the device_type_action field.Possible values:- phone- tablet- pc- tv- gameconsole- stb- mediaplayerFor format, see Device Type Targets below.                                                                                                                                                                                                                                                                                         |
    | device_type_action                                | enum                         | Action to be taken on device_type_targets. Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                               |
    | carrier_targets                                   | array of objects             | The mobile carriers to either include in or exclude from your targeting, as defined by the carrier_action field. To retrieve a complete list of mobile carriers registered in our system, use the read-only Carrier Service. For more details and format, see Carrier Targets below.                                                                                                                                                                                                                                          |
    | carrier_action                                    | enum                         | Action to be taken on the carrier_targets. Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                               |
    | inventory_url_list_targets                        | array of objects             | Contains a list of inventory list IDs (allowlists and/or blocklists). Used to attach a single allowlist and/or one or more blocklists to the profile.- The allowlist contains a list of domains or apps to be targeted by the line item using the profile. If an allowlist is included, domains and apps not in the allowlist will not be targeted.- Each blocklist contains a list of domains or apps that are to be excluded from targeting by line item that uses the profile.For more details, see Inventory Lists below. |
    | operating_system_family_targets                   | array of objects             | The operating systems as a whole (e.g., Android, Apple iOS, Windows 7, etc.) to either include in or exclude from your targeting, as defined by the operating_system_family_action field. Note: This field is used to target all versions of operating systems, whereas operating_system_extended_targets is used to target specific versions of operating systems. For more details and format, see Operating System Family Targets below.                                                                                   |
    | operating_system_family_action                    | enum                         | Action to be taken on operating_system_family_targets. Possible values: include or exclude.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | use_operating_system_extended_targeting           | Boolean                      | Read-only. If true, the operating_system_extended_targets field will be respected.                                                                                                                                                                                                                                                                                                                                                                                                                                            |
    | operating_system_extended_targets                 | array of objects             | The list of specific operating systems to either include in or exclude from your targeting. Note: This array is used to target specific operating system versions, whereas operating_system_family_targets is used to target all versions of operating systems. For more details and format, see Operating System Extended Targets below.Note: This field will be respected only if use_operating_system_extended_targeting is true.                                                                                          |
    | operating_system_action                           | enum                         | Deprecated. Use operating_system_extended_targets instead.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | operating_system_targets                          | array of objects             | Deprecated. Use operating_system_extended_targets instead.                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | mobile_app_instance_targets                       | array of objects             | A list of mobile app instances that you'd like to include or exclude from targeting. For field definitions, see Mobile App Instance Targets below. For more details about what mobile app instances are and how they work, see the Mobile App Instance Service.                                                                                                                                                                                                                                                               |
    | mobile_app_instance_action_include                | Boolean                      | Whether to include the mobile app instances defined in mobile_app_instance_targets in your campaign targeting.Default: false                                                                                                                                                                                                                                                                                                                                                                                                  |
    | mobile_app_instance_list_targets                  | array of objects             | This list contains mobile app instance lists (in other words, it's a list of lists). For field definitions, see Mobile App Instance List Targets below. For more information about mobile app instance lists are and how they work, see the Mobile App Instance List Service.                                                                                                                                                                                                                                                 |
    | mobile_app_instance_list_action_include           | Boolean                      | Whether to include the mobile app instance lists defined in mobile_app_instance_list_targets in your campaign targeting.Default: false                                                                                                                                                                                                                                                                                                                                                                                        |
    | deal_action_include                               | Boolean                      | Whether to include or exclude deals defined in deal_targets and deal lists defined in deal_list_targets in campaign and/or line item targeting. When set to true, deals and deal lists will be included.                                                                                                                                                                                                                                                                                                                      |
    | ip_range_list_targets                             | array of objects             | A list of IP address ranges to be included or excluded from campaign targeting. For more information, see IP Range List Targets below, as well as the documentation for the IP Range List Service.                                                                                                                                                                                                                                                                                                                            |
    | key_value_targets                                 | array of objects             | A list of custom key/value targets. For details and examples, see Key value targets below.                                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | ad_slot_position_action_include                   | Boolean                      | Intent to target specific slots in an ad pod. Note that you can target ad slots or ad bumpers, but not both.Default: false                                                                                                                                                                                                                                                                                                                                                                                                    |
    | ad_slot_position_targets                          | array of ints                | The ad slot positions a buyer wants to serve on. -1 represents the last position, 0 represents the first. By default when ad_slot_position_action_include is set to false, an empty array means spending can happen on any position. Set ad_slot_position_action_include to true first if you want to use ad_slot_position_targets to specify positions to target.Default: empty row                                                                                                                                          |
    | ad_slot_intro_bumper_action_include               | Boolean                      | This controls if the creative will target video intro positions for VAST video auctions. The default is true. To ensure that your creative does not target the intro adpod position, set this field to false. Note: You can target ad slots or ad bumpers, but not both.Default: true                                                                                                                                                                                                                                         |
    | ad_slot_outro_bumper_action_include               | Boolean                      | This controls if the creative will target video outro positions for VAST video auctions. The default is true. To ensure that your creative does not target the outro adpod position, set this field to false. Note: You can target ad slots or ad bumpers, but not both.Default: true                                                                                                                                                                                                                                         |
    | screen_size_action                                | string                       | Deprecated.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | screen_size_targets                               | array of objects             | Deprecated.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | optimization_zone_action                          | string                       | Not currently supported.Default: exclude                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
    | optimization_zone_targets                         | array of objects             | Not currently supported.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
    | created_on                                        | timestamp                    | Read-only. The date and time when the profile was created.                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | is_expired                                        | Boolean                      | Read-only. If true, the object associated with the profile is expired. This parameter is only supported for internal purposes.Default: false                                                                                                                                                                                                                                                                                                                                                                                  |
    | inventory_network_resold_targets                  | array of objects             | Deprecated.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | exelate_targets                                   | array of objects             | Deprecated.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | inventory_url_allowlist_settings                  | object                       | This object contains fields used to determine how allowlists are applied to line item buying. See Inventory URL Allowlist Settings.                                                                                                                                                                                                                                                                                                                                                                                           |
    | ads_txt_authorized_only                           | Boolean                      | When true, the line item will only target web inventory from authorized sellers of domains that have an ads.txt file.Note: The ads_txt_authorized_only targeting parameter only applies to Open Exchange inventory. It does not affect targeting of deal inventory. It also does not apply to app inventory (since use of an ads.txt file for app inventory has not yet been adopted by the industry). For more information, see Ads.txt FAQ for Buyers.Default: false                                                        |
    | political_district_targets                        | array of objects             | The political district IDs to target. See example.IDs can be fetched using the Political District Service.                                                                                                                                                                                                                                                                                                                                                                                                                    |
    """
    id: Optional[int] = Field(None, description="The ID of the profile.")
    code: Optional[str] = Field(None, description="Custom code for the profile.")
    description: Optional[str] = Field(None, description="Optional description.")
    is_template: Optional[bool] = Field(None, description="If true, the profile has been saved as a targeting template.")
    last_modified: Optional[str] = Field(None, description="Time of last modification to this profile.")
    is_archived: Optional[bool] = Field(None, description="Read-only. Indicates whether the profile has been automatically archived.")
    archived_on: Optional[str] = Field(None, description="Read-only. The date and time on which the profile was archived.")
    max_lifetime_imps: Optional[int] = Field(None, ge=0, le=255, description="The maximum number of impressions per person. If set, this value must be between 0 and 255.")
    min_session_imps: Optional[int] = Field(None, ge=0, le=255, description="The minimum number of impressions per person per session. If set, this value must be between 0 and 255.")
    max_session_imps: Optional[int] = Field(None, ge=0, le=255, description="The maximum number of impressions per person per session. If set, this value must be between 0 and 255.")
    max_day_imps: Optional[int] = Field(None, ge=0, le=255, description="The maximum number of impressions per person per day. If set, this value must be between 0 and 255.")
    max_hour_imps: Optional[int] = Field(None, ge=0, le=255, description="The maximum number of impressions per person per hour. If set, this value must be between 0 and 255.")
    max_week_imps: Optional[int] = Field(None, ge=0, le=255, description="The maximum number of impressions per person per week. If set, this value must be between 0 and 255.")
    max_month_imps: Optional[int] = Field(None, ge=0, le=255, description="The maximum number of impressions per person per month. If set, this value must be between 0 and 255.")
    min_minutes_per_imp: Optional[int] = Field(None, gt=0, description="The minimum number of minutes between impressions per person. This field may not be set to 0.")
    max_page_imps: Optional[int] = Field(None, description="The maximum number of impressions per page load (seller's ad request). Note: Only relevant for multi-tag auctions.")
    require_cookie_for_freq_cap: Optional[bool] = Field(None, description="Indicates whether you'll exclusively serve to users with known identifiers to maintain your frequency cap settings.")
    graph_id: Optional[GraphId] = Field(None, description="Null if the line item is targeting your member seat's default graph selection. 0 if targeting no graph. 3 for TapAd Graph. 4 for Xandr Graph.")
    daypart_timezone: Optional[str] = Field(None, description="The timezone to be used with the daypart_targets. Default: null.")
    daypart_targets: Optional[List[DaypartTarget]] = Field(None, description="The day parts during which to serve the campaign. If not set, the campaign serves on all days and times.")
    segment_targets: Optional[List[SegmentTarget]] = Field(None, description="Segment IDs to target, each with an associated action (include or exclude).")
    segment_group_targets: Optional[List[SegmentGroupTarget]] = Field(None, description="Segment groups to target, allowing Boolean logic between groups and segments.")
    segment_boolean_operator: Optional[Operator] = Field(None, description="Defines Boolean logic between segments or segment groups. Possible values: 'and', 'or'. Default: 'and'.")
    age_targets: Optional[List[AgeTarget]] = Field(None, description="List of age ranges to target, with an allow_unknown field for unknown ages.")
    gender_targets: Optional[GenderTarget] = Field(None, description="Gender targeting for the profile. Possible values: 'm', 'f'. Includes allow_unknown for unknown genders.")
    country_targets: Optional[List[CountryTarget]] = Field(None, description="Country IDs to include or exclude, as defined by country_action.")
    country_action: Optional[Action] = Field(None, description="Action for country_targets. Possible values: 'include', 'exclude'. Default: 'exclude'.")
    region_targets: Optional[List[RegionTarget]] = Field(None, description="Region/state IDs to include or exclude, as defined by region_action.")
    require_transparency_and_consent_framework_string: Optional[bool] = Field(None, description="If true, only allow inventory with valid TCF string. Default: false.")
    region_action: Optional[Action] = Field(None, description="Action for region_targets. Possible values: 'include', 'exclude'. Default: 'exclude'.")
    dma_targets: Optional[List[DmaTarget]] = Field(None, description="IDs of designated market areas to include or exclude, as defined by dma_action.")
    dma_action: Optional[Action] = Field(None, description="Action for dma_targets. Possible values: 'include', 'exclude'. Default: 'exclude'.")
    city_targets: Optional[List[CityTarget]] = Field(None, description="IDs of cities to include or exclude, as defined by city_action.")
    city_action: Optional[Action] = Field(None, description="Action for city_targets. Possible values: 'include', 'exclude'. Default: 'exclude'.")
    domain_targets: Optional[List[DomainTarget]] = Field(None, description="List of domains to include or exclude, as defined by domain_action.")
    domain_action: Optional[Action] = Field(None, description="Action for domain_targets. Possible values: 'include', 'exclude'. Default: 'exclude'.")
    domain_list_targets: Optional[List[DomainListTarget]] = Field(None, description="IDs of domain lists to include or exclude, as defined by domain_list_action.")
    domain_list_action: Optional[Action] = Field(None, description="Action for domain_list_targets. Possible values: 'include', 'exclude'. Default: 'exclude'.")
    # NOTE: There are no any docs or examples for this field
    platform_placement_targets: Optional[List[dict]] = Field(None, description="RTB or other Networks' inventory to target.")
    size_targets: Optional[List[SizeTarget]] = Field(None, description="List of eligible sizes to include in the profile, each with width and height.")
    seller_member_group_targets: Optional[List[SellerMemberGroupTarget]] = Field(None, description="Seller member groups to include or exclude in a profile.")
    member_targets: Optional[List[MemberTarget]] = Field(None, description="Seller member IDs to include or exclude in a profile.")
    video_targets: Optional[VideoTarget] = Field(None, description="Video target IDs to be included in a profile.")
    engagement_rate_targets: Optional[List[EngagementRateTarget]] = Field(None, description="Target specific, highly performant inventory based on historic performance.")
    # NOTE: There are no any docs or examples for this field. The definition inferred from docs
    publisher_targets: Optional[List[PublisherTarget]] = Field(None, description="Managed/direct publisher IDs to be either excluded or included in a profile.")
    # NOTE: There are no any docs or examples for this field. The definition inferred from docs
    site_targets: Optional[List[SiteTarget]] = Field(None, description="Site IDs to be either excluded or included in a profile.")
    # NOTE: There are no any docs or examples for this field. The definition inferred from docs
    placement_targets: Optional[List[PlacementTarget]] = Field(None, description="Placement IDs to be either excluded or included in a profile.")
    inventory_action: Optional[Action] = Field(None, description="Action to be taken on inventory targets. Possible values: include or exclude.")
    content_category_targets: Optional[ContentCategoryTargets] = Field(None, description="Content categories to target for this profile.")
    deal_targets: Optional[List[DealTarget]] = Field(None, description="Deal IDs to be targeted by this profile.")
    deal_list_targets: Optional[List[DealListTarget]] = Field(None, description="Deal list IDs to be targeted by this profile.")
    platform_publisher_targets: Optional[List[PlatformPublisherTarget]] = Field(None, description="Third-party publisher IDs to be either excluded or included in a profile.")
    # NOTE: There are no any docs or examples for this field
    platform_content_category_targets: Optional[List[dict]] = Field(None, description="Network resold content categories to target for this profile.")
    use_inventory_attribute_targets: Optional[bool] = Field(None, description="If true, allows inventory with sensitive attributes included in inventory_attribute_targets.")
    trust: Optional[Trust] = Field(None, description="Indicates the level of audit inventory must meet. Possible values: appnexus or seller.")
    allow_unaudited: Optional[bool] = Field(None, description="If true, allows unaudited inventory to pass targeting.")
    session_freq_type: Optional[SessionFreqType] = Field(None, description="Indicates how impressions are counted during the current browsing session.")
    inventory_attribute_targets: Optional[List[InventoryAttributeTarget]] = Field(None, description="IDs of inventory attributes to target for this profile.")
    intended_audience_targets: Optional[List[IntendedAudienceTarget]] = Field(None, description="Intended audience targets. Possible values: general, children, young_adult, or mature.")
    language_targets: Optional[List[LanguageTarget]] = Field(None, description="IDs of browser languages to include or exclude in the profile.")
    language_action: Optional[Action] = Field(None, description="Action to be taken on language_targets. Possible values: include or exclude.")
    # NOTE: There are no any docs or examples for this field
    querystring_targets: Optional[List[dict]] = Field(None, description="Query string targets to include or exclude in the profile.")
    querystring_action: Optional[Action] = Field(None, description="Action to be taken on querystring_targets. Possible values: include or exclude.")
    querystring_boolean_operator: Optional[Operator] = Field(None, description="Boolean logic to be applied to querystring_targets. Possible values: and or or.")
    postal_code_targets: Optional[List[PostalCodeTarget]] = Field(None, description="Postal code IDs to target.")
    postal_code_list_targets: Optional[List[PostalCodeListTarget]] = Field(None, description="Postal code list IDs to target.")
    postal_code_action_include: Optional[bool] = Field(None, description="Whether to include postal codes and postal code lists in targeting.")
    supply_type_targets: Optional[List[SupplyTypeTarget]] = Field(None, description="Types of supply to include or exclude from targeting.")
    supply_type_action: Optional[Action] = Field(None, description="Action to be taken on supply_type_targets. Possible values: include or exclude.")
    user_group_targets: Optional[UserGroupTarget] = Field(None, description="User group targeting for A/B testing or other strategies.")
    position_targets: Optional[PositionTarget] = Field(None, description="Fold positions to target.")
    browser_targets: Optional[List[BrowserTarget]] = Field(None, description="IDs of browsers to include or exclude in targeting.")
    browser_action: Optional[Action] = Field(None, description="Action to be taken on browser_targets. Possible values: include or exclude.")
    location_target_latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude of the user's location.")
    location_target_longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude of the user's location.")
    location_target_radius: Optional[int] = Field(None, description="Radius in meters for location targeting.")
    device_model_targets: Optional[List[DeviceModelTarget]] = Field(None, description="Models of mobile devices to include or exclude in targeting.")
    device_model_action: Optional[Action] = Field(None, description="Action to be taken on device_model_targets. Possible values: include or exclude.")
    device_type_targets: Optional[List[DeviceTypeTarget]] = Field(None, description="Types of devices to include or exclude in targeting.")
    device_type_action: Optional[Action] = Field(None, description="Action to be taken on device_type_targets. Possible values: include or exclude.")
    carrier_targets: Optional[List[CarrierTarget]] = Field(None, description="Mobile carriers to include or exclude in targeting.")
    carrier_action: Optional[Action] = Field(None, description="Action to be taken on carrier_targets. Possible values: include or exclude.")
    inventory_url_list_targets: Optional[List[InventoryUrlListTarget]] = Field(None, description="List of inventory list IDs (allowlists and/or blocklists).")
    operating_system_family_targets: Optional[List[OperatingSystemFamilyTarget]] = Field(None, description="Operating systems to include or exclude in targeting.")
    operating_system_family_action: Optional[Action] = Field(None, description="Action to be taken on operating_system_family_targets. Possible values: include or exclude.")
    use_operating_system_extended_targeting: Optional[bool] = Field(None, description="If true, operating_system_extended_targets will be respected.")
    operating_system_extended_targets: Optional[List[OperatingSystemExtendedTarget]] = Field(None, description="Specific operating systems to include or exclude in targeting.")
    mobile_app_instance_targets: Optional[List[MobileAppInstanceTarget]] = Field(None, description="Mobile app instances to include or exclude in targeting.")
    mobile_app_instance_action_include: Optional[bool] = Field(None, description="Whether to include mobile app instances in targeting.")
    mobile_app_instance_list_targets: Optional[List[MobileAppInstanceListTarget]] = Field(None, description="List of mobile app instance lists to include or exclude in targeting.")
    mobile_app_instance_list_action_include: Optional[bool] = Field(None, description="Whether to include mobile app instance lists in targeting.")
    deal_action_include: Optional[bool] = Field(None, description="Whether to include deals and deal lists in targeting.")
    ip_range_list_targets: Optional[List[IpRangeListModel]] = Field(None, description="List of IP address ranges to include or exclude from targeting.")
    key_value_targets: Optional[List[KeyValueTarget] | KeyValueTarget] = Field(None, description="List of custom key/value targets.")
    ad_slot_position_action_include: Optional[bool] = Field(None, description="Intent to target specific slots in an ad pod. Default: false.")
    ad_slot_position_targets: Optional[List[int]] = Field(None, description="Ad slot positions to target. -1 for last, 0 for first. Default: empty.")
    ad_slot_intro_bumper_action_include: Optional[bool] = Field(None, description="Target video intro positions for VAST video auctions. Default: true.")
    ad_slot_outro_bumper_action_include: Optional[bool] = Field(None, description="Target video outro positions for VAST video auctions. Default: true.")
    created_on: Optional[str] = Field(None, description="Read-only. Date and time when the profile was created.")
    is_expired: Optional[bool] = Field(None, description="Read-only. If true, the object associated with the profile is expired. Default: false.")
    inventory_url_allowlist_settings: Optional[InventoryUrlAllowlistSettings] = Field(None, description="Fields used to determine how allowlists are applied to line item buying.")
    ads_txt_authorized_only: Optional[bool] = Field(None, description="If true, targets web inventory from authorized sellers with ads.txt. Default: false.")
    political_district_targets: Optional[List[PoliticalDistrictTarget]] = Field(None, description="Political district IDs to target.")
