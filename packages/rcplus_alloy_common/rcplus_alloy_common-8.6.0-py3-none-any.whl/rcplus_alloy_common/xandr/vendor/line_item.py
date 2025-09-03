# ruff: noqa: E501
"""
Microsoft Xandr API doesn't have any formal specifications. Code below is based on its documentation:
https://learn.microsoft.com/en-us/xandr/digital-platform-api/line-item-service---ali

NOTE: There is an old deprecated Line Item API. We use a new Line Item ALI API. ALI - Augmented Line Item.
"""
from enum import Enum
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class State(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class LineItemType(str, Enum):
    STANDARD_V1 = "standard_v1"
    STANDARD_V2 = "standard_v2"
    GUARANTEED_DELIVERY = "guaranteed_delivery"
    CURATED = "curated"


class AdType(str, Enum):
    BANNER = "banner"
    VIDEO = "video"
    NATIVE = "native"
    AUDIO = "audio"


class GoalType(str, Enum):
    NONE = "none"
    CPC = "cpc"
    CPA = "cpa"
    CTR = "ctr"
    CUSTOM = "custom"


class TriggerType(str, Enum):
    VIEW = "view"
    CLICK = "click"
    HYBRID = "hybrid"


class AuditStatus(str, Enum):
    NO_AUDIT = "no_audit"
    PENDING = "pending"
    REJECTED = "rejected"
    AUDITED = "audited"
    UNAUDITABLE = "unauditable"


class Format(str, Enum):
    URL_HTML = "url-html"
    URL_XML = "url-xml"
    URL_JS = "url-js"
    FLASH = "flash"
    IMAGE = "image"
    RAW_JS = "raw-js"
    RAW_HTML = "raw-html"
    IFRAME_HTML = "iframe-html"
    TEXT = "text"
    NATIVE = "native"


class ValuationStrategy(str, Enum):
    RETARGETING = "retargeting"
    PROSPECTING = "prospecting"


class CreativeDistributionType(str, Enum):
    EVEN = "even"
    WEIGHTED = "weighted"
    CTR_OPTIMIZED = "ctr-optimized"


class LineItemSubtype(str, Enum):
    STANDARD_BUYING = "standard_buying"
    PG_BUYING = "pg_buying"
    PG_DEAL_IMP = "pg_deal_imp"
    PSP = "psp"
    GD_BUYING_IMP = "gd_buying_imp"
    GD_BUYING_EXCLUSIVE = "gd_buying_exclusive"
    STANDARD_CURATED = "standard_curated"
    STANDARD_DEAL = "standard_deal"
    HOUSE_DEFAULT = "house_default"


class AdvertiserRef(BaseModel):
    id: Optional[int] = Field(None, description="The unique identifier for this advertiser.")
    name: Optional[str] = Field(None, description="The name of the advertiser associated with the unique ID above.")


class LabelRef(BaseModel):
    id: Optional[Literal[7, 8, 11]] = Field(None, description="The ID of the label.")
    name: Optional[Literal["Trafficker", "Sales Rep", "Line Item Type"]] = Field(None, description=" The name of the label.")
    value: Optional[str] = Field(None, max_length=100, description="The value assigned to the label.")


class PublisherRef(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the publisher to which the impression tracker is associated.")
    name: Optional[str] = Field(None, description="The name of the publisher to which the impression tracker is associated.")


class TagRef(BaseModel):
    """
    NOTE: They call it tag in docs but it refers to `Placement Service`.
    """
    id: Optional[int] = Field(None, description="The ID of the placement to which the impression tracker is associated.")
    name: Optional[str] = Field(None, description="The name of the placement to which the impression tracker is associated.")


class PaymentRuleRef(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the payment rule to which the impression tracker is associated.")
    name: Optional[str] = Field(None, description="The name of the payment rule to which the impression tracker is associated.")


class LineItemRef(BaseModel):
    id: Optional[int] = Field(None, description="The ID of the line item to which the impression tracker is associated.")
    name: Optional[str] = Field(None, description="The name of the line item to which the impression tracker is associated.")


class PartnerFeeRef(BaseModel):
    id: Optional[int] = Field(None, description=" 	The ID of a partner fee applied to this line item.")


class Pixel(BaseModel):
    """
    | Field              | Type   | Description                                              |
    |--------------------|--------|----------------------------------------------------------|
    | id                 | int    | The ID of the conversion pixel.                          |
    | state              | enum   | The state of the pixel.                                  |
    | post_click_revenue | double | The post click revenue value for the pixel.              |
    | post_view_revenue  | double | The post view revenue value for the pixel.               |
    | name               | string | The name of the conversion pixel. **Read Only.**         |
    | trigger_type       | enum   | The type of event required for an attributed conversion. |
    """
    id: Optional[int] = Field(None, description="ID of the conversion pixel")
    state: Optional[State] = Field(None, description="State of the pixel")
    post_click_revenue: Optional[float] = Field(None, description="Post click revenue value")
    post_view_revenue: Optional[float] = Field(None, description="Post view revenue value")
    name: Optional[str] = Field(None, description="Name of the conversion pixel")
    trigger_type: Optional[TriggerType] = Field(None, description="Event type for conversion")


class GoalPixel(BaseModel):
    """
    | Field                     | Type   | Description                                                             |
    |---------------------------|--------|-------------------------------------------------------------------------|
    | id                        | int    | The ID of the conversion pixel.                                         |
    | state                     | enum   | The state of the pixel.                                                 |
    | trigger_type              | enum   | The type of event required for an attributed conversion.                |
    | post_click_goal_target    | double | The advertiser goal value for post-click conversions for the pixel.     |
    | post_view_goal_target     | double | The advertiser goal value for post-view conversions for the pixel.      |
    | post_click_goal_threshold | double | The advertiser goal threshold for post-click conversions for the pixel. |
    | post_view_goal_threshold  | double | The advertiser goal threshold for post-view conversions for the pixel.  |
    """
    id: Optional[int] = Field(None, description="ID of the pixel")
    state: Optional[State] = Field(None, description="State of the pixel")
    trigger_type: Optional[TriggerType] = Field(None, description="Event type for conversion")
    post_click_goal_target: Optional[float] = Field(None, description="Goal value for post-click conversions")
    post_view_goal_target: Optional[float] = Field(None, description="Goal value for post-view conversions")
    post_click_goal_threshold: Optional[float] = Field(None, description="Threshold for post-click conversions")
    post_view_goal_threshold: Optional[float] = Field(None, description="Threshold for post-view conversions")


class CustomDateRange(BaseModel):
    start_date: Optional[str] = Field(None, description="The start date of the custom date range. Format must be YYYY-MM-DD hh:mm:ss (hh:mm:ss should be hh:00:00).")
    end_date: Optional[str] = Field(None, description="The end date of the budget interval. Format must be YYYY-MM-DD hh:mm:ss (hh:mm:ss should be set to hh:59:59).")


class Creative(BaseModel):
    """
    | Field                | Type             | Description                                                                                                                               |
    |----------------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
    | id                   | int              | The ID of the creative. Either id or code is required when updating creative association.                                                 |
    | code                 | string           | The custom code for the creative. Either id or code is required when updating creative association.                                       |
    | state                | enum             | The state of the creative. Possible values: "active" or "inactive".                                                                       |
    | is_expired           | boolean          | If true, the creative is expired. If false, the creative is active.                                                                       |
    | is_prohibited        | boolean          | If true, the creative falls into a prohibited category on the Xandr platform.                                                             |
    | width                | int              | The width of the creative.                                                                                                                |
    | audit_status         | enum             | The audit status of the creative. Possible values: "no_audit", "pending", "rejected", "audited", or "unauditable".                        |
    | name                 | string           | The name of the creative.                                                                                                                 |
    | pop_window_maximize  | boolean          | If true, the publisher's tag will maximize the window. Only relevant for creatives with format "url-html" and "url-js".                   |
    | height               | int              | The height of the creative.                                                                                                               |
    | format               | enum             | The format of the creative file. Possible values: "url-html", "url-js", "flash", "image", "raw-js", "raw-html", "iframe-html", or "text". |
    | is_self_audited      | boolean          | If true, the creative is self-audited.                                                                                                    |
    | weight               | int              | A user-supplied weight that determines the creative rotation strategy for same-sized creatives managed at the line item level.            |
    | ad_type              | string           | The creative ad type. Possible values: "banner", "video", "native", "audio".                                                              |
    | all_budget_intervals | boolean          | Indicates whether the creative will serve during all budget intervals, including all future budget intervals.                             |
    | custom_date_ranges   | array of objects | The date ranges setting the periods when the creative will serve.                                                                         |
    """
    id: Optional[int] = Field(None, description="ID of the creative")
    code: Optional[str] = Field(None, description="Custom code for the creative")
    state: Optional[State] = Field(None, description="State of the creative")
    is_expired: Optional[bool] = Field(None, description="Indicates if the creative is expired")
    is_prohibited: Optional[bool] = Field(None, description="Indicates if the creative is prohibited")
    width: Optional[int] = Field(None, description="Width of the creative")
    audit_status: Optional[AuditStatus] = Field(None, description="Audit status of the creative")
    name: Optional[str] = Field(None, description="Name of the creative")
    pop_window_maximize: Optional[bool] = Field(None, description="Maximizes the window if true")
    height: Optional[int] = Field(None, description="Height of the creative")
    format: Optional[Format] = Field(None, description="Format of the creative file")
    is_self_audited: Optional[bool] = Field(None, description="Indicates if the creative is self-audited")
    weight: Optional[int] = Field(None, description="Weight for creative rotation")
    ad_type: Optional[AdType] = Field(None, description="Ad type of the creative")
    all_budget_intervals: Optional[bool] = Field(None, description="Indicates if creative serves during all intervals")
    custom_date_ranges: Optional[List[CustomDateRange]] = Field(None, description="Date ranges for serving the creative")


class BudgetInterval(BaseModel):
    """
    | Field                | Type      | Description                                                                                                   |
    |----------------------|-----------|---------------------------------------------------------------------------------------------------------------|
    | id                   | int       | The ID of the budget interval.                                                                                |
    | start_date           | timestamp | The start date of the budget interval. Format must be YYYY-MM-DD hh:mm:ss (hh:mm:ss should be hh:00:00).      |
    | end_date             | timestamp | The end date of the budget interval. Format must be YYYY-MM-DD hh:mm:ss (hh:mm:ss should be set to hh:59:59). |
    | timezone             | string    | The timezone by which budget and spend are counted.                                                           |
    | lifetime_budget      | double    | The lifetime budget in revenue for the budget interval.                                                       |
    | lifetime_budget_imps | double    | The lifetime budget in impressions for the budget interval.                                                   |
    | lifetime_pacing      | boolean   | If true, the line item will attempt to pace the lifetime budget evenly over the budget interval.              |
    | daily_budget         | double    | The daily budget in revenue for the budget interval.                                                          |
    | daily_budget_imps    | double    | The daily budget in impressions.                                                                              |
    | enable_pacing        | boolean   | If true, then spending will be paced over the course of the day.                                              |
    | creatives            | array     | Specifies the creatives associated with this budget interval.                                                 |
    """
    id: Optional[int] = Field(None, description="ID of the budget interval")
    start_date: Optional[str] = Field(None, description="Start date of the budget interval")
    end_date: Optional[str] = Field(None, description="End date of the budget interval")
    timezone: Optional[str] = Field(None, description="Timezone for budget and spend")
    lifetime_budget: Optional[float] = Field(None, description="Lifetime budget in revenue")
    lifetime_budget_imps: Optional[float] = Field(None, description="Lifetime budget in impressions")
    lifetime_pacing: Optional[bool] = Field(None, description="Pace lifetime budget evenly")
    daily_budget: Optional[float] = Field(None, description="Daily budget in revenue")
    daily_budget_imps: Optional[float] = Field(None, description="Daily budget in impressions")
    enable_pacing: Optional[bool] = Field(None, description="Pace spending over the day")
    creatives: Optional[List[Creative]] = Field(None, description="Creatives associated with the budget interval")


class InsertionOrder(BaseModel):
    """
    | Field            | Type             | Description                                                                   |
    |------------------|------------------|-------------------------------------------------------------------------------|
    | id               | int              | The unique ID of the insertion order.                                         |
    | state            | enum             | The state of this insertion order.                                            |
    | code             | string           | An optional custom code used to identify this insertion order.                |
    | name             | string           | The name of this insertion order.                                             |
    | advertiser_id    | int              | The unique identifier of the advertiser associated with this insertion order. |
    | start_date       | date             | The start date for this insertion order.                                      |
    | end_date         | date             | The end date for this insertion order.                                        |
    | timezone         | enum             | The timezone that this insertion order is associated with.                    |
    | last_modified    | date             | The date at which this insertion order object was last updated.               |
    | currency         | enum             | The currency type associated with this insertion order.                       |
    | budget_intervals | array of objects | The metadata for the budget intervals from the associated insertion order.    |
    """
    id: Optional[int] = Field(None, description="Unique ID of the insertion order")
    state: Optional[State] = Field(None, description="State of the insertion order")
    code: Optional[str] = Field(None, description="Custom code for the insertion order")
    name: Optional[str] = Field(None, description="Name of the insertion order")
    advertiser_id: Optional[int] = Field(None, description="Advertiser's unique identifier")
    start_date: Optional[str] = Field(None, description="Start date of the insertion order")
    end_date: Optional[str] = Field(None, description="End date of the insertion order")
    timezone: Optional[str] = Field(None, description="Timezone of the insertion order")
    last_modified: Optional[str] = Field(None, description="Last updated date of the insertion order")
    currency: Optional[str] = Field(None, description="Currency type of the insertion order")
    budget_intervals: Optional[List[BudgetInterval]] = Field(None, description="Budget intervals metadata")


class ImpressionTracker(BaseModel):
    """
    | Field         | Type      | Description                                                             |
    |---------------|-----------|-------------------------------------------------------------------------|
    | id            | int       | The ID of the impression tracker.                                       |
    | member_id     | int       | The ID of the member to which the advertiser belongs.                   |
    | advertiser_id | int       | The ID of the advertiser that owns the impression tracker.              |
    | name          | string    | The name for the impression tracker.                                    |
    | code          | string    | The custom code for the impression tracker.                             |
    | state         | enum      | The state of the impression tracker.                                    |
    | publisher     | object    | The publisher to which the impression tracker is associated.            |
    | tag           | array     | The placement to which the impression tracker is associated.            |
    | payment_rule  | object    | The payment rule to which the impression tracker is associated.         |
    | line_item     | object    | The advertiser line item to which the impression tracker is associated. |
    | last_modified | timestamp | The date and time when the impression tracker was last modified.        |
    """
    id: Optional[int] = Field(None, description="ID of the impression tracker")
    member_id: Optional[int] = Field(None, description="ID of the member")
    advertiser_id: Optional[int] = Field(None, description="ID of the advertiser")
    name: Optional[str] = Field(None, description="Name of the impression tracker")
    code: Optional[str] = Field(None, description="Custom code for the impression tracker")
    state: Optional[State] = Field(None, description="State of the impression tracker")
    publisher: Optional[PublisherRef] = Field(None, description="Associated publisher details")
    tag: Optional[List[TagRef] | TagRef] = Field(None, description="Associated placement details")
    payment_rule: Optional[PaymentRuleRef] = Field(None, description="Associated payment rule details")
    line_item: Optional[LineItemRef] = Field(None, description="Associated advertiser line item")
    last_modified: Optional[str] = Field(None, description="Last modified date and time")


class ClickTracker(BaseModel):
    """
    | Field         | Type      | Description                                                        |
    |---------------|-----------|--------------------------------------------------------------------|
    | id            | int       | The ID of the click tracker.                                       |
    | member_id     | int       | The ID of the member to which the advertiser belongs.              |
    | advertiser_id | int       | The ID of the advertiser that owns the click tracker.              |
    | name          | string    | The name for the click tracker.                                    |
    | code          | string    | The custom code for the click tracker.                             |
    | state         | enum      | The state of the click tracker.                                    |
    | click_url     | string    | The target landing page for the creative.                          |
    | publisher     | object    | The publisher to which the click tracker is associated.            |
    | line_item     | object    | The advertiser line item to which the click tracker is associated. |
    | tag           | array     | The placement to which the click tracker is associated.            |
    | payment_rule  | array     | The payment rule to which the click tracker is associated.         |
    | last_modified | timestamp | The date and time when the click tracker was last modified.        |
    """
    id: Optional[int] = Field(None, description="ID of the click tracker")
    member_id: Optional[int] = Field(None, description="ID of the member")
    advertiser_id: Optional[int] = Field(None, description="ID of the advertiser")
    name: Optional[str] = Field(None, description="Name of the click tracker")
    code: Optional[str] = Field(None, description="Custom code for the click tracker")
    state: Optional[State] = Field(None, description="State of the click tracker")
    click_url: Optional[str] = Field(None, description="Target landing page for the creative")
    publisher: Optional[PublisherRef] = Field(None, description="Associated publisher details")
    line_item: Optional[LineItemRef] = Field(None, description="Associated advertiser line item")
    tag: Optional[List[TagRef] | TagRef] = Field(None, description="Associated placement details")
    payment_rule: Optional[List[PaymentRuleRef]] = Field(None, description="Associated payment rule details")
    last_modified: Optional[str] = Field(None, description="Last modified date and time")


class Valuation(BaseModel):
    """
    | Field                             | Type    | Description                                                           |
    |-----------------------------------|---------|-----------------------------------------------------------------------|
    | min_margin_pct                    | decimal | Only set this field if you have set prefer_delivery_over_performance. |
    | goal_threshold                    | decimal | The performance goal threshold.                                       |
    | goal_target                       | decimal | The performance goal target.                                          |
    | campaign_group_valuation_strategy | enum    | The campaign group valuation strategy.                                |
    | min_avg_cpm                       | double  | The value below which the average CPM may not fall.                   |
    | max_avg_cpm                       | double  | The value above which the average CPM may not rise.                   |
    | min_margin_cpm                    | double  | Margin Value when Margin Type is CPM.                                 |
    | min_margin_pct                    | double  | Margin Value when Margin Type is Percentage.                          |
    """
    min_margin_pct: Optional[float] = Field(None, description="Minimum margin percentage")
    goal_threshold: Optional[float] = Field(None, description="Performance goal threshold")
    goal_target: Optional[float] = Field(None, description="Performance goal target")
    campaign_group_valuation_strategy: Optional[ValuationStrategy] = Field(None, description="Valuation strategy for campaign group")
    min_avg_cpm: Optional[float] = Field(None, description="Minimum average CPM")
    max_avg_cpm: Optional[float] = Field(None, description="Maximum average CPM")
    min_margin_cpm: Optional[float] = Field(None, description="Minimum margin CPM")


class SupplyStrategy(BaseModel):
    """
    | Field                   | Type    | Description                                                                               |
    |-------------------------|---------|-------------------------------------------------------------------------------------------|
    | rtb                     | boolean | Designates whether you wish to target inventory on the Open Exchange.                     |
    | managed                 | boolean | Designates whether you wish to target managed inventory.                                  |
    | deals                   | boolean | Designates whether you wish to target deal inventory.                                     |
    | programmatic_guaranteed | boolean | Designates whether you wish to target a programmatic guaranteed deal with this line item. |
    """
    rtb: Optional[bool] = Field(None, description="Target Open Exchange inventory")
    managed: Optional[bool] = Field(None, description="Target managed inventory")
    deals: Optional[bool] = Field(None, description="Target deal inventory")
    programmatic_guaranteed: Optional[bool] = Field(None, description="Target programmatic guaranteed deals")


class AuctionEventType(str, Enum):
    IMPRESSION = "impression"
    VIEW = "view"
    CLICK = "click"
    VIDEO = "video"


class AuctionEventTypeCode(str, Enum):
    IMPRESSION = "impression"
    VIEW_DISPLAY_50PV1S_AN = "view_display_50pv1s_an"
    CLICK = "click"
    VIDEO_COMPLETION = "video_completion"


class KpiValueType(str, Enum):
    NONE = "none"
    GOAL_VALUE = "goal_value"
    RATE_THRESHOLD = "rate_threshold"


class AuctionEvent(BaseModel):
    """
    Auction event configuration for line items, used to specify revenue and KPI auction settings.
    | Field                           | Type   | Description                                                                           |
    |---------------------------------|--------|---------------------------------------------------------------------------------------|
    | revenue_auction_event_type      | string | Event type for revenue calculation (impression, view, click, video)                   |
    | revenue_auction_event_type_code | string | Event type code for revenue (impression, view_display_50pv1s_an, click, video_completion) |
    | revenue_auction_type_id         | int    | Event type ID for revenue (1=impression, 2=view, 3=click, 10=video)                 |
    | kpi_auction_event_type          | string | Event type for KPI optimization (impression, view, click, video)                      |
    | kpi_auction_event_type_code     | string | Event type code for KPI (impression, view_display_50pv1s_an, video_completion)       |
    | kpi_auction_type_id             | int    | Event type ID for KPI (1=impression/optimization, 2=view, 10=video)                 |
    | kpi_value                       | double | KPI goal value (null for CPC/CPA/CTR, goal value for others)                        |
    | kpi_value_type                  | string | KPI value type (none, goal_value, rate_threshold)                                    |
    | payment_auction_event_type      | string | Payment event type for RTB inventory (impression, view, click, video)                |
    | payment_auction_event_type_code | string | Payment event type code for RTB (impression, view_display_50pv1s_an, video_completion) |
    | payment_auction_type_id         | int    | Payment event type ID for RTB (1=impression, 2=view, 10=video)                      |
    """
    revenue_auction_event_type: Optional[AuctionEventType] = Field(None, description="Event type for revenue calculation")
    revenue_auction_event_type_code: Optional[AuctionEventTypeCode] = Field(None, description="Event type code for revenue")
    revenue_auction_type_id: Optional[int] = Field(None, description="Event type ID for revenue")
    kpi_auction_event_type: Optional[AuctionEventType] = Field(None, description="Event type for KPI optimization")
    kpi_auction_event_type_code: Optional[AuctionEventTypeCode] = Field(None, description="Event type code for KPI")
    kpi_auction_type_id: Optional[int] = Field(None, description="Event type ID for KPI")
    kpi_value: Optional[float] = Field(None, description="KPI goal value")
    kpi_value_type: Optional[KpiValueType] = Field(None, description="KPI value type")
    payment_auction_event_type: Optional[AuctionEventType] = Field(None, description="Payment event type for RTB inventory")
    payment_auction_event_type_code: Optional[AuctionEventTypeCode] = Field(None, description="Payment event type code for RTB")
    payment_auction_type_id: Optional[int] = Field(None, description="Payment event type ID for RTB")


class LineItem(BaseModel):
    """
    NOTE: Because the line item model is very large in Xandr all fields marked as `deprecated` or `do not use` or
    similar were skipped and are not used in this class. Also descriptions are quite large so the were shortened.
    Use the documentation link in the beginning to get all the details.

    | Field                            | Type             | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
    |----------------------------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | id                               | int              | The ID of the line item. **Required On:** PUT, in query string.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
    | code                             | string (100)     | A custom code for the line item. The code may only contain alphanumeric characters, periods, underscores or dashes.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | name                             | string (255)     | The name of the line item. **Required On:** POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
    | advertiser_id                    | int              | The ID of the advertiser to which the line item belongs.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
    | state                            | enum             | The state of the line item. Possible values: "active" or "inactive". **Default:** "active"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
    | line_item_type                   | enum             | The type of line item. Possible values are: - "standard_v1": Standard line item (non-ALI). - "standard_v2": Augmented line item (ALI). - "guaranteed_delivery": Guaranteed line item (GDLI). - "curated": Curated line item.                                                                                                                                                                                                                                                                                                                                                                                                              |
    | timezone                         | enum             | The timezone by which budget and spend are counted.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | ad_types                         | array of strings | The type of creative used for this line item. Possible values: - "banner" - "video" - "native" - "audio" The array should only have a single value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | revenue_value                    | double           | The amount paid to the network by the advertiser.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
    | revenue_type                     | enum             | The way the advertiser has agreed to pay you (also called Booked Revenue).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
    | goal_type                        | enum             | For line items that make use of performance goals. Possible values: null, "cpc", "cpa", "ctr", or "custom".                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
    | last_modified                    | timestamp        | The time of last modification to this line item. Read Only.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
    | click_url                        | string (1000)    | The click URL to apply at the line item level.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
    | currency                         | string (3)       | The currency used for this line item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | require_cookie_for_tracking      | boolean          | Indicates whether you want to serve only to identified users for conversion-tracking purposes.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
    | profile_id                       | int              | You may associate an optional profile_id with this line item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
    | member_id                        | int              | ID of the member that owns the line item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
    | comments                         | string           | Comments about the line item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
    | remaining_days                   | int              | The number of days between today and the end_date for the line item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
    | total_days                       | int              | The number of days between the start_date and end_date for the line item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
    | advertiser                       | object           | An object describing the advertiser with which this line item is associated.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
    | labels                           | array            | The optional labels applied to the line item. Currently, the labels available are: "Trafficker" and "Sales Rep". For more details, see Labels below.Note:You can report on line item labels with the Network Analytics and Network Advertiser Analytics reports. For example, if you use the "Trafficker" label to specify the name of the trafficker responsible for each line item, you could run the Network Analytics report filtered by "trafficker_for_line_item" to focus on the line items that a particular trafficker is responsible for, or grouped by "trafficker_for_line_item" to rank the performance of your traffickers. |
    | pixels                           | array of objects | The conversion pixels used to track CPA revenue. Both post-click and post-view revenue may be specified. You may only attach 20 pixels to a line item. If you need to attach more, speak with your Xandr Implementation Consultant or Support. For more details, see Pixels and the example below for a sample of the format.Default: null                                                                                                                                                                                                                                                                                                |
    | insertion_orders                 | array of objects | Objects containing metadata for the insertion orders this line item is associated with.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | goal_pixels                      | array of objects | For a line item with the goal_type "cpa", the pixels used for conversion tracking, as well as the post-view and post-click revenue.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | imptrackers                      | array of objects | The third-party impression trackers associated with the line item. For more details, see Impression Tracker Service.Read Only.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
    | clicktrackers                    | array of objects | The third-party click trackers associated with the line item. For more details, see Click Tracker Service.Read Only.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
    | valuation                        | object           | For a line item with the goal_type "cpc" or "cpa", the performance goal threshold, which determines the bid/no bid cutoff on optimized line items, and the performance goal target, which represents the desired clicks (conversions for "cpa" are set in the Goal Pixels array of objects).                                                                                                                                                                                                                                                                                                                                              |
    | creatives                        | array of objects | The creatives that are associated with the line item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | budget_intervals                 | array of objects | Budget intervals enable multiple date intervals to be attached to a line item, each with corresponding budget values.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
    | enable_pacing                    | boolean          | If true, the daily budgeted spend is spread out evenly throughout a day. Only applicable if there is a daily budget.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
    | lifetime_pacing                  | boolean          | If true, the line item will attempt to spend its overall lifetime budget evenly over the line item flight dates.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
    | lifetime_pacing_pct              | double           | A double integer between-- and including-- 50 and 150, used to set pacing throughout a budget interval.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | payout_margin                    | double           | The payout margin on performance offer line items.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
    | insertion_order_id               | int              | The ID of the current active insertion order (when applicable). Must append include_insertion_order_id=true to return this field in a GET call.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
    | all_stats                        | array            | To show Rapid Reports for all available intervals (today, yesterday, the last 7 days, life time), pass all_status=true in the query string of a GET request.Read Only.                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | first_run                        | timestamp        | The date and time when the line item had its first impression, refreshed on an hourly basis. This value reflects the UTC time zone.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | last_run                         | timestamp        | The date and time when the line item had its last impression, refreshed on an hourly basis. This value reflects the UTC time zone.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
    | alerts                           | object           | The conditions that are preventing the line item from serving.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
    | supply_strategies                | object           | An object containing several boolean fields used to designate which inventory supply sources you would like to target.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
    | creative_distribution_type       | enum             | When multiple creatives of the same size are trafficked via a line item, this field's setting is used to determine the creative rotation strategy that will be used.                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
    | prefer_delivery_over_performance | boolean          | This field is used to indicate your goal priority (whether you wish to give greater priority to delivery, performance, or margin).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
    | use_ip_tracking                  | boolean          | Determines whether IP Attribution is enabled or not for a given line item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
    | viewability_vendor               | string           | This field determines what provider measures the viewability of the ad unit.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
    | is_archived                      | boolean          | Read-only. Indicates whether the line item has been automatically archived due to not being used.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
    | archived_on                      | timestamp        | The date and time on which the line item was archived (i.e., when the is_archived field was set to true).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
    | partner_fees                     | array            | An array of partner fees applied to this line item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
    | line_item_subtype                | enum             | The subtype of the line item. The line_item_subtype field cannot be changed after the line item is created.
    | flat_fee_type                    | string           | The type of flat fee applied to the line item. Required when revenue_type is flat_fee. Available values: daily, one_time
    | auction_event                    | object           | The ID of the auction event associated with the line item.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
    """
    id: Optional[int] = Field(None, description="The ID of the line item")
    code: Optional[str] = Field(None, max_length=100, description="Custom code for the line item")
    name: Optional[str] = Field(None, max_length=255, description="Name of the line item")
    advertiser_id: Optional[int] = Field(None, description="ID of the advertiser")
    state: Optional[State] = Field(State.ACTIVE, description="State of the line item")
    line_item_type: Optional[LineItemType] = Field(LineItemType.STANDARD_V2, description="Type of line item")
    timezone: Optional[str] = Field("UTC", description="Timezone for budget and spend")
    ad_types: Optional[List[AdType]] = Field([AdType.BANNER], description="Type of creative used")
    revenue_value: Optional[float] = Field(None, description="Amount paid to the network")
    # NOTE: The field below doesn't have dedicated type because of its perplexed description in the docs
    revenue_type: Optional[str] = Field(None, description="Payment method agreed by the advertiser")
    goal_type: Optional[GoalType] = Field(None, description="Performance goal type")
    last_modified: Optional[str] = Field(None, description="The time of last modification to this line item. Read Only.")
    click_url: Optional[str] = Field(None, max_length=1000, description="Click URL at the line item level")
    currency: Optional[str] = Field(None, max_length=3, description="Currency used for the line item")
    require_cookie_for_tracking: Optional[bool] = Field(True, description="Serve only to identified users for tracking")
    profile_id: Optional[int] = Field(None, description="Optional profile ID for targeting inventory")
    member_id: Optional[int] = Field(None, description="ID of the member owning the line item")
    comments: Optional[str] = Field(None, description="Comments about the line item")
    remaining_days: Optional[int] = Field(None, description="Number of days between today and the end_date")
    total_days: Optional[int] = Field(None, description="Number of days between start_date and end_date")
    advertiser: Optional[AdvertiserRef] = Field(None, description="Details of the associated advertiser")
    labels: Optional[List[LabelRef]] = Field(None, description="Optional labels applied to the line item")
    pixels: Optional[List[Pixel]] = Field(None, description="Conversion pixels for CPA revenue tracking")
    insertion_orders: Optional[List[InsertionOrder]] = Field(None, description="Metadata for associated insertion orders")
    goal_pixels: Optional[List[GoalPixel]] = Field(None, description="Pixels for conversion tracking with goal_type 'cpa'")
    imptrackers: Optional[List[ImpressionTracker]] = Field(None, description="Third-party impression trackers")
    clicktrackers: Optional[List[ClickTracker] | ClickTracker] = Field(None, description="Third-party click trackers")
    valuation: Optional[Valuation] = Field(None, description="Performance goal thresholds and targets")
    creatives: Optional[List[Creative]] = Field(None, description="Creatives associated with the line item")
    budget_intervals: Optional[List[BudgetInterval]] = Field(None, description="Multiple date intervals with corresponding budgets")
    enable_pacing: Optional[bool] = Field(None, description="Spread daily budgeted spend evenly throughout a day")
    lifetime_pacing: Optional[bool] = Field(None, description="Spend lifetime budget evenly over flight dates")
    lifetime_pacing_pct: Optional[float] = Field(None, description="Pacing percentage for budget intervals")
    payout_margin: Optional[float] = Field(None, description="Payout margin on performance offer line items")
    insertion_order_id: Optional[int] = Field(None, description="ID of the current active insertion order")
    # NOTE:
    # There is no clear model definition for stats, this field appears only if `all_stats=true` is set in the API query
    all_stats: Optional[List[dict]] = Field(None, description="Rapid Reports for all available intervals")
    first_run: Optional[str] = Field(None, description="Date and time of the first impression")
    last_run: Optional[str] = Field(None, description="Date and time of the last impression")
    # NOTE:
    # There is no clear model definition for alerts, this field appears only if `show_alerts=true` is set in the API
    # query, even more alerts are show if `show_alerts=true&pauses=true` is set.
    # Even more options available for pauses (for example, various filters), see the documentation.
    alerts: Optional[dict] = Field(None, description="Conditions preventing the line item from serving")
    supply_strategies: Optional[SupplyStrategy] = Field(None, description="Inventory supply sources targeting settings")
    creative_distribution_type: Optional[CreativeDistributionType] = Field(None, description="Creative rotation strategy")
    prefer_delivery_over_performance: Optional[bool] = Field(None, description="Indicates priority between delivery and performance")
    use_ip_tracking: Optional[bool] = Field(None, description="Enables or disables IP Attribution")
    viewability_vendor: Optional[str] = Field("appnexus", description="Provider measuring ad unit viewability")
    is_archived: Optional[bool] = Field(None, description="Indicates if the line item is automatically archived")
    archived_on: Optional[str] = Field(None, description="Date and time when the line item was archived")
    partner_fees: Optional[List[PartnerFeeRef]] = Field(None, description="Partner fees applied to the line item")
    line_item_subtype: Optional[LineItemSubtype] = Field(None, description="Subtype of the line item")
    flat_fee_type: Optional[str] = Field(None, description="Type of flat fee applied to the line item")
    auction_event: Optional[AuctionEvent] = Field(None, description="Auction event configuration for the line item")
