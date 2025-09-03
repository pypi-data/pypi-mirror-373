from typing import Optional, List, Dict, Literal
from enum import Enum

from pydantic import BaseModel, TypeAdapter


class GAM(BaseModel):
    network_id: int


class XANDR(BaseModel):
    member_id: int
    aws_region: str
    ppid_source: str


class DAS(BaseModel):
    network_id: int


class ActivationChannels(BaseModel):
    gam: Optional[GAM] = None
    xandr: Optional[XANDR] = None
    das: Optional[DAS] = None


class Features(BaseModel):
    sso_data: bool = False
    enterprise: bool = False
    dcr: bool = False
    byok: bool = False
    gotom: bool = False
    coops: bool = False
    audience_segment_service: bool = False


class Prediction(BaseModel):
    name: str
    params_path: str


class CustomAttributeType(str, Enum):
    training = "training"
    direct = "direct"
    external_id = "external_id"
    content = "content"
    tracking = "tracking"
    audience_segment = "audience_segment"


class CustomAttributeRawDataFormat(str, Enum):
    parquet = "parquet"
    json = "json"


class CustomAttributeWhenCondition(BaseModel):
    operator: Literal["in", "not in"]
    value: List[str]
    attribute: str


class BaseAttribute(BaseModel):
    string: str
    separator: str | None = None


class LiteralAttributeResult(BaseAttribute):
    """Result containing a literal string value"""
    type: Literal["literal"]


class JsonPathAttributeResult(BaseAttribute):
    """Result obtained via JSONPath expression"""
    type: Literal["jsonpath"]
    jsonpath: str


class RegexAttributeResult(BaseAttribute):
    """Result obtained via regular expression"""
    type: Literal["regex"]
    pattern: str


class CustomAttributeQueryItem(BaseModel):
    condition: CustomAttributeWhenCondition
    result: LiteralAttributeResult | JsonPathAttributeResult | RegexAttributeResult


class CustomAttributeQuery(BaseModel):
    conditions: list[CustomAttributeQueryItem] | None = None
    result: LiteralAttributeResult | JsonPathAttributeResult | RegexAttributeResult | None = None


class CustomAttributeMapValues(BaseModel):
    """Mapping of values for a custom attribute"""
    values: List[str]
    name: str


class CustomAttribute(BaseModel):
    name: str
    target_external_id_name: str | None = None
    display_name: str | None = None
    category: str | None = None
    active: bool
    external_id_name: str | None = None
    raw_data_format: CustomAttributeRawDataFormat | None = None
    incremental: bool | None = None
    type: CustomAttributeType
    id_pii: bool | None = None
    value_pii: bool = False
    s3_predictions_params_path: str | None = None
    query: CustomAttributeQuery | None = None
    buckets: List[int] | None = None
    map_values: List[CustomAttributeMapValues] | None = None


class Taxonomies(BaseModel):
    name: str
    score: float


class CanonicalIdExtraction(BaseModel):
    uri_provider: str
    id_regex: str | None = None
    use_uri_path_hash_as_extracted_id: bool | None = None


class ScmiSiteType(str, Enum):
    SPA = "SPA"
    STATIC = "STATIC"


class ContentProvider(BaseModel):
    name: str
    section_prefixes: List[str]
    source_system: str | None = None
    content_id_extraction_query: str | None = None
    hardcoded_taxonomies: List[Taxonomies] | None = None
    canonical_id_extraction: CanonicalIdExtraction | None = None
    is_uri_extracted_id_external_id: bool | None = None
    uri_prefixes: List[str]
    scmi_site_id: str | None = None
    scmi_site_type: ScmiSiteType | None = None
    tracking_based_crawler: bool = False
    app_ids: List[str] | None = None


class DataLayerAutoTrackingEvent(BaseModel):
    key_name: str
    key_value: str
    event_path: str | None = None


class TrackerConfig(BaseModel):
    app_ids: list[str]
    id_regex: str | None = None
    use_uri_path_hash_as_extracted_id: bool = False
    data_layer_auto_tracking_events: List[DataLayerAutoTrackingEvent] | None = None


class TrackingProvider(BaseModel):
    tracker: str
    logical_paths: List[str]
    configs: list[TrackerConfig] | None = None


class TenantConfig(BaseModel):
    name: str
    timezone: str | None = None
    activation_channels: ActivationChannels
    features: Features
    predictions: List[Prediction]
    kropka_tenants: List[str]
    content_providers: List[ContentProvider]
    tracking_providers: List[TrackingProvider] | None = None
    custom_attributes: List[CustomAttribute] | None = None
    is_test_tenant: bool = False
    cron_schedule: Dict[str, str] | None = None


def get_json_schema():
    adapter = TypeAdapter(List[TenantConfig])
    return adapter.json_schema()
