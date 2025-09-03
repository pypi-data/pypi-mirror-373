# ruff: noqa: E501
from __future__ import annotations

from typing import Any, Optional, Literal
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class GAMSOAPBaseModel(BaseModel):
    xsi_type: Optional[str] = Field(
        None,
        description="The xsi:type of the object"
    )

    @model_validator(mode="before")
    def set_xsi_type(cls, values):
        xsi_type_default = cls.model_fields["xsi_type"].default
        if xsi_type_default:
            values["xsi_type"] = xsi_type_default
        else:
            values["xsi_type"] = cls.__name__
        return values


class Date(GAMSOAPBaseModel):
    """
    <complexType name="Date">
    <annotation>
    <documentation> Represents a date. </documentation>
    </annotation>
    <sequence>
    <element maxOccurs="1" minOccurs="0" name="year" type="xsd:int">
    <annotation>
    <documentation> Year (e.g., 2009) </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="month" type="xsd:int">
    <annotation>
    <documentation> Month (1..12) </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="day" type="xsd:int">
    <annotation>
    <documentation> Day (1..31) </documentation>
    </annotation>
    </element>
    </sequence>
    </complexType>
    """
    year: int = Field(
        title="Year",
        description="Year (e.g., 2009)",
        # ge=datetime.now().year,
    )
    month: int = Field(
        title="Month",
        description="Month (1..12)",
        ge=1,
        le=12,
    )
    day: int = Field(
        title="Day",
        description="Day (1..31)",
        ge=1,
        le=31,
    )


class DateTime(GAMSOAPBaseModel):
    """
    <complexType name="DateTime">
    <annotation>
    <documentation> Represents a date combined with the time of day. </documentation>
    </annotation>
    <sequence>
    <element maxOccurs="1" minOccurs="0" name="date" type="tns:Date"/>
    <element maxOccurs="1" minOccurs="0" name="hour" type="xsd:int"/>
    <element maxOccurs="1" minOccurs="0" name="minute" type="xsd:int"/>
    <element maxOccurs="1" minOccurs="0" name="second" type="xsd:int"/>
    <element maxOccurs="1" minOccurs="0" name="timeZoneId" type="xsd:string"/>
    </sequence>
    </complexType>
    """
    date: Date
    hour: int = Field(
        ...,
        ge=0,
        le=24,
        description="Hour (0..24)",
    )
    minute: int = Field(
        ...,
        ge=0,
        le=60,
        description="Minute (0..60)",
    )
    second: int = Field(
        ...,
        ge=0,
        le=60,
        description="Second (0..60)",
    )
    timeZoneId: str = Field(
        ...,
        description="Time zone ID"
    )


class Money(GAMSOAPBaseModel):
    """
    <complexType name="Money">
    <annotation>
    <documentation> Represents a money amount. </documentation>
    </annotation>
    <sequence>
    <element maxOccurs="1" minOccurs="0" name="currencyCode" type="xsd:string">
    <annotation>
    <documentation> Three letter currency code in string format. </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="microAmount" type="xsd:long">
    <annotation>
    <documentation> Money values are always specified in terms of micros which are a millionth of the fundamental currency unit. For US dollars, $1 is 1,000,000 micros. </documentation>
    </annotation>
    </element>
    </sequence>
    </complexType>
    """
    currencyCode: str = Field(
        ...,
        description="Three letter currency code in string format.",
        min_length=3,
        max_length=3
    )
    microAmount: int = Field(
        ...,
        description=(
            "Money values are always specified in terms of micros which are a millionth of the "
            "fundamental currency unit. For US dollars, $1 is 1,000,000 micros."
        )
    )


class AppliedLabel(GAMSOAPBaseModel):
    """
    <complexType name="AppliedLabel">
    <annotation>
    <documentation> Represents a {@link Label} that can be applied to an entity. To negate an inherited label, create an {@code AppliedLabel} with {@code labelId} as the inherited label's ID and {@code isNegated} set to true. </documentation>
    </annotation>
    <sequence>
    <element maxOccurs="1" minOccurs="0" name="labelId" type="xsd:long">
    <annotation>
    <documentation> The ID of a created {@link Label}. </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="isNegated" type="xsd:boolean">
    <annotation>
    <documentation> {@code isNegated} should be set to {@code true} to negate the effects of {@code labelId}. </documentation>
    </annotation>
    </element>
    </sequence>
    </complexType>
    """
    labelId: int = Field(
        ...,
        description=(
            "The ID of a created https://developers.google.com/ad-manager/api/reference/v202502/LabelService.Label"
        )
    )
    isNegated: bool = Field(
        ...,
        description="isNegated should be set to true to negate the effects of labelId."
    )


class BaseCustomFieldValue(GAMSOAPBaseModel):
    """
    <complexType abstract="true" name="BaseCustomFieldValue">
    <annotation>
    <documentation> The value of a {@link CustomField} for a particular entity. </documentation>
    </annotation>
    <sequence>
    <element maxOccurs="1" minOccurs="0" name="customFieldId" type="xsd:long">
    <annotation>
    <documentation> Id of the {@code CustomField} to which this value belongs. This attribute is required. </documentation>
    </annotation>
    </element>
    </sequence>
    </complexType>
    """
    customFieldId: int = Field(
        ...,
        description="Id of the CustomField to which this value belongs. This attribute is required."
    )


class CustomFieldValue(BaseCustomFieldValue):
    """
    <complexType name="CustomFieldValue">
    <annotation>
    <documentation> The value of a {@link CustomField} that does not have a {@link CustomField#dataType} of {@link CustomFieldDataType#DROP_DOWN}. </documentation>
    </annotation>
    <complexContent>
    <extension base="tns:BaseCustomFieldValue">
    <sequence>
    <element maxOccurs="1" minOccurs="0" name="value" type="tns:Value">
    <annotation>
    <documentation> The value for this field. The appropriate type of {@code Value} is determined by the {@link CustomField#dataType} of the {@code CustomField} that this conforms to. <table> <tr><th>{@link CustomFieldDataType}</th><th>{@link Value} type</th></tr> <tr><td>{@link CustomFieldDataType#STRING STRING}</td><td>{@link TextValue}</td></tr> <tr><td>{@link CustomFieldDataType#NUMBER NUMBER}</td><td>{@link NumberValue}</td></tr> <tr><td>{@link CustomFieldDataType#TOGGLE TOGGLE}</td><td>{@link BooleanValue}</td></tr> </table> </documentation>
    </annotation>
    </element>
    </sequence>
    </extension>
    </complexContent>
    </complexType>
    """
    value: Any = Field(
        ...,
        description="The value for this field. The appropriate type of Value is determined by the CustomField.dataType of the CustomField that this conforms to."
    )


class DropDownCustomFieldValue(BaseCustomFieldValue):
    """"
    <complexType name="DropDownCustomFieldValue">
    <annotation>
    <documentation> A {@link CustomFieldValue} for a {@link CustomField} that has a {@link CustomField#dataType} of {@link CustomFieldDataType#DROP_DOWN} </documentation>
    </annotation>
    <complexContent>
    <extension base="tns:BaseCustomFieldValue">
    <sequence>
    <element maxOccurs="1" minOccurs="0" name="customFieldOptionId" type="xsd:long">
    <annotation>
    <documentation> The {@link CustomFieldOption#id ID} of the {@link CustomFieldOption} for this value. </documentation>
    </annotation>
    </element>
    </sequence>
    </extension>
    </complexContent>
    </complexType>
    """
    customFieldOptionId: int = Field(
        ...,
        description="The ID of the CustomFieldOption for this value."
    )


class Size(GAMSOAPBaseModel):
    """
    <complexType name="Size">
    <annotation>
    <documentation> Represents the dimensions of an {@link AdUnit}, {@link LineItem} or {@link Creative}. <p>For interstitial size (out-of-page), native, ignored and fluid size, {@link Size} must be 1x1. </documentation>
    </annotation>
    <sequence>
    <element maxOccurs="1" minOccurs="0" name="width" type="xsd:int">
    <annotation>
    <documentation> The width of the {@link AdUnit}, {@link LineItem} or {@link Creative}. </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="height" type="xsd:int">
    <annotation>
    <documentation> The height of the {@link AdUnit}, {@link LineItem} or {@link Creative}. </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="isAspectRatio" type="xsd:boolean">
    <annotation>
    <documentation> Whether this size represents an aspect ratio. </documentation>
    </annotation>
    </element>
    </sequence>
    </complexType>
    """
    width: int = Field(
        ...,
        gt=0,
        description="The width of the AdUnit, LineItem or Creative."
    )
    height: int = Field(
        ...,
        gt=0,
        description="The height of the AdUnit, LineItem or Creative."
    )
    isAspectRatio: Optional[bool] = Field(  # NOTE: apparently this is not required
        default=None,
        description="Whether this size represents an aspect ratio."
    )


class Stats(GAMSOAPBaseModel):
    """
    <complexType name="Stats">
    <annotation>
    <documentation> {@code Stats} contains trafficking statistics for {@link LineItem} and {@link LineItemCreativeAssociation} objects </documentation>
    </annotation>
    <sequence>
    <element maxOccurs="1" minOccurs="0" name="impressionsDelivered" type="xsd:long">
    <annotation>
    <documentation> The number of impressions delivered. </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="clicksDelivered" type="xsd:long">
    <annotation>
    <documentation> The number of clicks delivered. </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="videoCompletionsDelivered" type="xsd:long">
    <annotation>
    <documentation> The number of video completions delivered. </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="videoStartsDelivered" type="xsd:long">
    <annotation>
    <documentation> The number of video starts delivered. </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="viewableImpressionsDelivered" type="xsd:long">
    <annotation>
    <documentation> The number of viewable impressions delivered. </documentation>
    </annotation>
    </element>
    </sequence>
    </complexType>
    """
    impressionsDelivered: int = Field(
        ...,
        ge=0,
        description="The number of impressions delivered."
    )
    clicksDelivered: int = Field(
        ...,
        ge=0,
        description="The number of clicks delivered."
    )
    videoCompletionsDelivered: int = Field(
        ...,
        ge=0,
        description="The number of video completions delivered."
    )
    videoStartsDelivered: int = Field(
        ...,
        ge=0,
        description="The number of video starts delivered."
    )
    viewableImpressionsDelivered: int = Field(
        ...,
        description="The number of viewable impressions delivered."
    )


class FrequencyCap(GAMSOAPBaseModel):
    """
    <complexType name="FrequencyCap">
    <annotation>
    <documentation> Represents a limit on the number of times a single viewer can be exposed to the same {@link LineItem} in a specified time period. </documentation>
    </annotation>
    <sequence>
    <element maxOccurs="1" minOccurs="0" name="maxImpressions" type="xsd:int">
    <annotation>
    <documentation> The maximum number of impressions than can be served to a user within a specified time period. </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="numTimeUnits" type="xsd:int">
    <annotation>
    <documentation> The number of {@code FrequencyCap#timeUnit} to represent the total time period. </documentation>
    </annotation>
    </element>
    <element maxOccurs="1" minOccurs="0" name="timeUnit" type="tns:TimeUnit">
    <annotation>
    <documentation> The unit of time for specifying the time period. </documentation>
    </annotation>
    </element>
    </sequence>
    </complexType>
    """
    maxImpressions: int = Field(
        ...,
        gt=0,
        description="The maximum number of impressions than can be served to a user within a specified time period."
    )
    numTimeUnits: int = Field(
        ...,
        gt=0,
        description="The number of FrequencyCap#timeUnit to represent the total time period."
    )
    timeUnit: Literal["MINUTE", "HOUR", "DAY", "WEEK", "MONTH", "LIFETIME", "POD", "STREAM", "UNKNOWN"] = Field(
        ...,
        description="The unit of time for specifying the time period."
    )


class EnvironmentType(str, Enum):
    """
    <simpleType name="EnvironmentType">
    <annotation>
    <documentation> Enum for the valid environments in which ads can be shown. </documentation>
    </annotation>
    <restriction base="xsd:string">
    <enumeration value="BROWSER">
    <annotation>
    <documentation> A regular web browser. </documentation>
    </annotation>
    </enumeration>
    <enumeration value="VIDEO_PLAYER">
    <annotation>
    <documentation> Video players. </documentation>
    </annotation>
    </enumeration>
    </restriction>
    </simpleType>
    """
    BROWSER = "BROWSER"
    VIDEO_PLAYER = "VIDEO_PLAYER"
