# ruff: noqa: E501
"""
Microsoft Xandr API doesn't have any formal specifications. Code below is based on its documentation:
https://learn.microsoft.com/en-us/xandr/digital-platform-api/report-service

NOTE: Xandr API has many reports and related services. At the moment only `network-analytics` reports are supported:
https://learn.microsoft.com/en-us/xandr/digital-platform-api/network-analytics
"""
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ReportType(str, Enum):
    NETWORK_ANALYTICS = "network_analytics"
    NETWORK_BILLING = "network_billing"
    BUYER_INVOICE_REPORT = "buyer_invoice_report"
    SELLER_INVOICE_REPORT = "seller_invoice_report"
    NETWORK_ADVERTISER_ANALYTICS = "network_advertiser_analytics"
    NETWORK_PUBLISHER_ANALYTICS = "network_publisher_analytics"
    NETWORK_SITE_DOMAIN_PERFORMANCE = "network_site_domain_performance"
    ADVERTISER_ANALYTICS = "advertiser_analytics"
    VIDEO_ANALYTICS_NETWORK = "video_analytics_network"
    VIDEO_ANALYTICS_NETWORK_ADVERTISER = "video_analytics_network_advertiser"
    VIDEO_ANALYTICS_NETWORK_PUBLISHER = "video_analytics_network_publisher"
    BUYER_SEGMENT_PERFORMANCE = "buyer_segment_performance"
    SELLER_BRAND_REVIEW = "seller_brand_review"
    PUBLISHER_BRAND_REVIEW = "publisher_brand_review"
    PUBLISHER_ANALYTICS = "publisher_analytics"
    NETWORK_CREATIVE_SEARCH = "network_creative_search"
    PUBLISHER_CREATIVE_SEARCH = "publisher_creative_search"
    NETWORK_ADVERTISER_FREQUENCY_RECENCY = "network_advertiser_frequency_recency"
    ADVERTISER_FREQUENCY_RECENCY = "advertiser_frequency_recency"
    SITE_DOMAIN_PERFORMANCE = "site_domain_performance"
    SELLER_SITE_DOMAIN = "seller_site_domain"
    INVENTORY_DOMAIN_ANALYTICS = "inventory_domain_analytics"
    INVENTORY_SOURCE_ANALYTICS = "inventory_source_analytics"
    INVENTORY_DAILY_UNIQUES = "inventory_daily_uniques"
    SEGMENT_LOAD = "segment_load"
    ATTRIBUTED_CONVERSIONS = "attributed_conversions"
    PIXEL_FIRED = "pixel_fired"
    NETWORK_ANALYTICS_FEED = "network_analytics_feed"
    CLICKTRACKERS = "clicktrackers"
    KEY_VALUE_ANALYTICS = "key_value_analytics"
    PREBID_SERVER_ANALYTICS = "prebid_server_analytics"
    PSP_HEALTH_ANALYTICS = "psp_health_analytics"


class ReportInterval(str, Enum):
    CURRENT_HOUR = "current_hour"
    LAST_HOUR = "last_hour"
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_48_HOURS = "last_48_hours"
    LAST_2_DAYS = "last_2_days"
    LAST_7_DAYS = "last_7_days"
    LAST_14_DAYS = "last_14_days"
    LAST_30_DAYS = "30_days"
    MONTH_TO_YESTERDAY = "month_to_yesterday"
    MONTH_TO_DATE = "month_to_date"
    QUARTER_TO_DATE = "quarter_to_date"
    LAST_MONTH = "last_month"
    LIFETIME = "lifetime"


class FormatType(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    HTML = "html"


class ReportingDecimalType(str, Enum):
    COMMA = "comma"
    DECIMAL = "decimal"  # period


class Report(BaseModel):
    """
    | Field                  | Type             | Description                                                                                                                                                                                                                               |
    |------------------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | report_type            | enum             | This determines which information will be returned.                                                                                                                                                                                       |
    | timezone               | string (50)      | This determines which timezone the data will be reported in.                                                                                                                                                                              |
    | filters                | array of strings | The list of filter objects to apply to the report. See step 1 of How to run a report section below.                                                                                                                                       |
    | group_filters          | array of objects | Allows you to specify an operation to perform on one or more filters. For example, if you're selecting total impressions grouped by campaign, you can use this field to filter out campaigns that don't have at least 10,000 impressions. |
    | columns                | array of strings | The list of columns to include in the report. See Create a JSON-formatted report request below. At least one column must be specified.                                                                                                    |
    | start_date             | string           | The start date for the report. For report types that offer hourly data, this must be formatted as "YYYY-MM-DD HH:MM:SS".Note: MM:SS must be 00:00, as data is not available for minutes and seconds.                                      |
    | end_date               | string           | The end date for the report.Note: The end_date is non-inclusive. Format: 'YYYY-MM-DD HH:MM:SS'.                                                                                                                                           |
    | report_interval        | enum             | The time range for the report. Not all reports accept all intervals. See each report's documentation and metadata for details.                                                                                                            |
    | orders                 | array of objects | The list of columns to sort by. See How to run a report below.                                                                                                                                                                            |
    | format                 | enum             | The format in which the report data will be returned. If this field is not specified, it will default to "csv".Possible values:- "csv": Comma-separated values- "excel": Tab-separated values- "html"                                     |
    | reporting_decimal_type | enum             | The decimal mark used in the report. Possible values:- "comma"- "decimal" (period)If this field is passed, it overrides any reporting decimal preferences set at the user and member levels.                                              |
    | emails                 | array of strings | The list of email addresses to which the reporting data will be sent.                                                                                                                                                                     |
    | escape_fields          | boolean          | When true, it adds quotes around each field in the report output to allow for safer import into Excel. This only applies to CSV and tab-delimited reports.                                                                                |
    """
    report_type: Optional[ReportType] = Field(None, description="This determines which information will be returned.")
    timezone: Optional[str] = Field(None, max_length=50, description="This determines which timezone the data will be reported in.")
    filters: Optional[List[dict]] = Field(None, description="The list of filter objects to apply to the report.")
    group_filters: Optional[List[dict]] = Field(None, description="Allows you to specify an operation to perform on one or more filters.")
    columns: Optional[List[str]] = Field(None, description="The list of columns to include in the report. At least one column must be specified.")
    start_date: Optional[str] = Field(None, description="The start date for the report. Format: 'YYYY-MM-DD HH:MM:SS'.")
    end_date: Optional[str] = Field(None, description="The end date for the report. Non-inclusive. Format: 'YYYY-MM-DD HH:MM:SS'.")
    report_interval: Optional[ReportInterval] = Field(None, description="The time range for the report.")
    orders: Optional[List[dict]] = Field(None, description="The list of columns to sort by.")
    format: Optional[FormatType] = Field(None, description="The format in which the report data will be returned. Defaults to 'csv'.")
    reporting_decimal_type: Optional[ReportingDecimalType] = Field(None, description="The decimal mark used in the report.")
    emails: Optional[List[str]] = Field(None, description="The list of email addresses to which the reporting data will be sent.")
    escape_fields: Optional[bool] = Field(None, description="When true, adds quotes around each field in the report output for safer import into Excel.")
