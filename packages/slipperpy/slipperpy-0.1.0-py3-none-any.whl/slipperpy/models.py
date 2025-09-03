"""Pydantic models for Slipper Energy Management GraphQL API."""

from decimal import Decimal
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field


# Enums from GraphQL schema
class DeviceTypeChoices(str, Enum):
    """Device type choices."""
    ANDROID = "ANDROID"
    IOS = "IOS"
    WEB = "WEB"
    UBUNTU_TOUCH = "UBUNTU_TOUCH"
    API = "API"
    UNKNOWN = "UNKNOWN"


class HomeAreaChoices(str, Enum):
    """Home area choices."""
    NO1 = "NO1"
    NO2 = "NO2"
    NO3 = "NO3"
    NO4 = "NO4"
    NO5 = "NO5"
    UNKNOWN = "UNKNOWN"


class HomeCountryChoices(str, Enum):
    """Home country choices."""
    NO = "NO"


class HomeTypeChoices(str, Enum):
    """Home type choices."""
    HOUSE = "HOUSE"
    CABBIN = "CABBIN"
    CABIN = "CABIN"
    UNKNOWN = "UNKNOWN"


class HousingTypeChoices(str, Enum):
    """Housing type choices."""
    APARTMENT = "APARTMENT"
    HOUSE = "HOUSE"
    TOWNHOUSE = "TOWNHOUSE"
    COTTAGE = "COTTAGE"


class ConstructionYearChoices(str, Enum):
    """Construction year choices."""
    BEFORE_1988 = "BEFORE_1988"
    YEAR_1988_1997 = "YEAR_1988_1997"
    YEAR_1998_2009 = "YEAR_1998_2009"
    YEAR_2010_2017 = "YEAR_2010_2017"
    AFTER_2018 = "AFTER_2018"


class PrimaryHeatingTypeChoices(str, Enum):
    """Primary heating type choices."""
    PANEL_AND_HEATERS = "PANEL_AND_HEATERS"
    ELECTRIC_UNDERFLOOR_HEATING = "ELECTRIC_UNDERFLOOR_HEATING"
    AIR_TO_AIR_HEAT_PUMP = "AIR_TO_AIR_HEAT_PUMP"
    AIR_TO_WATER_HEAT_PUMP = "AIR_TO_WATER_HEAT_PUMP"
    DISTRICT_HEATING = "DISTRICT_HEATING"
    ROCK_HEATING = "ROCK_HEATING"
    OTHER = "OTHER"


class NotificationTypeChoices(str, Enum):
    """Notification type choices."""
    DAILY_CONSUMPTION = "DAILY_CONSUMPTION"
    PRICE = "PRICE"
    CHEAPER_PLAN = "CHEAPER_PLAN"
    POWERDATA_READY = "POWERDATA_READY"
    DATA_FETCH_FAILED = "DATA_FETCH_FAILED"
    HOME_SHARE_REQUEST = "HOME_SHARE_REQUEST"
    HOME_SHARE_ACCEPTED = "HOME_SHARE_ACCEPTED"
    PROVIDER_CHANGED = "PROVIDER_CHANGED"
    PLAN_CHANGED = "PLAN_CHANGED"


# GraphQL Response Models
class GraphQLError(BaseModel):
    """Represents a GraphQL error."""
    message: str
    locations: Optional[List[Dict[str, int]]] = None
    path: Optional[List[str]] = None
    extensions: Optional[Dict[str, Any]] = None


class GraphQLResponse(BaseModel):
    """Represents a GraphQL response."""
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[GraphQLError]] = None
    extensions: Optional[Dict[str, Any]] = None

    @property
    def has_errors(self) -> bool:
        """Check if the response has any errors."""
        return self.errors is not None and len(self.errors) > 0

    @property
    def is_successful(self) -> bool:
        """Check if the response is successful (has data and no errors)."""
        return self.data is not None and not self.has_errors


class GraphQLRequest(BaseModel):
    """Represents a GraphQL request."""
    query: str
    variables: Optional[Dict[str, Any]] = None
    operation_name: Optional[str] = Field(None, alias="operationName")

    class Config:
        validate_by_name = True


# Core Data Models
class UserType(BaseModel):
    """Represents a user."""
    id: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: str
    is_active: bool = Field(alias="isActive")
    is_staff: bool = Field(alias="isStaff")
    is_superuser: bool = Field(alias="isSuperuser")
    last_login: Optional[datetime] = Field(None, alias="lastLogin")
    phone_number: Optional[str] = Field(None, alias="phoneNumber")
    birth_date: Optional[date] = Field(None, alias="birthDate")
    rc_id: Optional[str] = Field(None, alias="rcId")

    class Config:
        validate_by_name = True


class DeviceType(BaseModel):
    """Represents a device."""
    id: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    user: Optional[UserType] = None
    firebase_registration_token: Optional[str] = Field(None, alias="firebaseRegistrationToken")
    api_key: str = Field(alias="apiKey")
    name: str
    type: DeviceTypeChoices

    class Config:
        validate_by_name = True


class GridType(BaseModel):
    """Represents an electricity grid."""
    id: str
    name: str
    area: Optional[str] = None
    tariff: Optional[Decimal] = None

    class Config:
        validate_by_name = True


class HomePlanType(BaseModel):
    """Represents a home plan."""
    id: str

    class Config:
        validate_by_name = True


class HomeType(BaseModel):
    """Represents a home."""
    id: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    meter_id: str = Field(alias="meterId")
    meter_identification: str = Field(alias="meterIdentification")
    name: Optional[str] = Field(None, alias="name")
    street: str
    street_number: str = Field(alias="streetNumber")
    postal_code: str = Field(alias="postalCode")
    city: str
    country: HomeCountryChoices
    estimated_yearly_consumption: int = Field(alias="estimatedYearlyConsumption")
    user: Optional[UserType] = None
    grid: Optional[GridType] = None
    shared_with: Optional[List[UserType]] = Field(None, alias="sharedWith")
    share_requests: Optional[List[UserType]] = Field(None, alias="shareRequests")
    area: HomeAreaChoices
    blocked: bool
    is_plus: bool = Field(alias="isPlus")
    is_automatic: bool = Field(alias="isAutomatic")
    max_kwh: int = Field(alias="maxKwh")
    type: HomeTypeChoices
    current_plan: Optional[HomePlanType] = Field(None, alias="currentPlan")

    class Config:
        validate_by_name = True


class ConsumptionType(BaseModel):
    """Represents energy consumption data."""
    id: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    meter_id: str = Field(alias="meterId")
    date: datetime
    kwh: Decimal
    granularity: str
    metering_type: str = Field(alias="meteringType")
    cost: Decimal
    tax: Decimal
    handout: Decimal
    tariff: Decimal
    tariff_tax: Decimal = Field(alias="tariffTax")
    enova: Decimal
    tariff_addition: Decimal = Field(alias="tariffAddition")
    plan_addition: Decimal = Field(alias="planAddition")

    class Config:
        validate_by_name = True


class ConsumptionGroupType(BaseModel):
    """Represents grouped consumption data."""
    date: datetime
    total_kwh: Decimal = Field(alias="totalKwh")
    total_cost: Decimal = Field(alias="totalCost")
    average_price: Decimal = Field(alias="averagePrice")
    granularity: str

    class Config:
        validate_by_name = True


class ElectricityPriceType(BaseModel):
    """Represents electricity price data."""
    date: datetime
    area: str
    priceKwh: Decimal
    granularity: str
    forecast: bool = False

    class Config:
        validate_by_name = True


class ElectricityPriceGroupType(BaseModel):
    """Represents grouped electricity price data."""
    date: datetime
    area: str
    average_price: Decimal = Field(alias="averagePrice")
    min_price: Decimal = Field(alias="minPrice")
    max_price: Decimal = Field(alias="maxPrice")
    granularity: str

    class Config:
        validate_by_name = True


class ProviderType(BaseModel):
    """Represents an electricity provider."""
    id: str
    name: str
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        validate_by_name = True


class PlanType(BaseModel):
    """Represents an electricity plan."""
    id: str
    name: str
    provider: Optional[ProviderType] = None
    price_per_kwh: Decimal = Field(alias="pricePerKwh")
    fixed_fee: Decimal = Field(alias="fixedFee")
    offer_type: Optional[str] = Field(None, alias="offerType")

    class Config:
        validate_by_name = True


class NotificationSettingType(BaseModel):
    """Represents notification settings."""
    id: str
    notification_type: NotificationTypeChoices = Field(alias="notificationType")
    enabled: bool
    delivery_method: str = Field(alias="deliveryMethod")
    frequency: Optional[str] = None

    class Config:
        validate_by_name = True


class ReferralType(BaseModel):
    """Represents a referral."""
    id: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    invited_by: UserType = Field(alias="invitedBy")
    status: str
    invited_short_name: Optional[str] = Field(None, alias="invitedShortName")
    access_level: Optional[str] = Field(None, alias="accessLevel")

    class Config:
        validate_by_name = True

class DeviceType(BaseModel):
    """Represents a device."""
    id: str
    firebase_registration_token: Optional[str] = Field(None, alias="firebaseRegistrationToken")
    name: str
    type: str
    fingerprint: Optional[str] = None

    class Config:
        validate_by_name = True


# Response wrapper types for common queries
class HomesResponse(BaseModel):
    """Response for homes query."""
    homes: List[HomeType]


class ConsumptionsResponse(BaseModel):
    """Response for consumptions query."""
    consumptions: List[ConsumptionType]


class ElectricityPricesResponse(BaseModel):
    """Response for electricity prices query."""
    electricity_prices: List[ElectricityPriceType] = Field(alias="electricityPrices")

    class Config:
        validate_by_name = True


class PlansResponse(BaseModel):
    """Response for plans query."""
    plans: List[PlanType]


class ProvidersResponse(BaseModel):
    """Response for providers query."""
    providers: List[ProviderType]

class DevicesResponse(BaseModel):
    """Response for devices query."""
    devices: List[DeviceType]