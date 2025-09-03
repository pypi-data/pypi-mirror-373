"""SlipperPy - A Python GraphQL client library for Slipper Energy Management."""

from slipperpy.__about__ import __version__
from slipperpy.client import SlipperClient
from slipperpy.exceptions import GraphQLError, NetworkError, SlipperError, AuthenticationError, TimeoutError, ValidationError
from slipperpy.models import (
    GraphQLResponse,
    HomeType,
    UserType,
    DeviceType,
    ConsumptionType,
    ElectricityPriceType,
    PlanType,
    ProviderType,
    NotificationSettingType,
    ReferralType,
    # Enums
    DeviceTypeChoices,
    HomeAreaChoices,
    HomeCountryChoices,
    HomeTypeChoices,
    HousingTypeChoices,
    ConstructionYearChoices,
    PrimaryHeatingTypeChoices,
    NotificationTypeChoices,
)

__all__ = [
    "__version__",
    "SlipperClient",
    "GraphQLResponse",
    # Exceptions
    "SlipperError",
    "GraphQLError", 
    "NetworkError",
    "AuthenticationError",
    "TimeoutError",
    "ValidationError",
    # Models
    "HomeType",
    "UserType",
    "DeviceType",
    "ConsumptionType",
    "ElectricityPriceType",
    "PlanType",
    "ProviderType",
    "NotificationSettingType",
    "ReferralType",
    # Enums
    "DeviceTypeChoices",
    "HomeAreaChoices",
    "HomeCountryChoices",
    "HomeTypeChoices",
    "HousingTypeChoices",
    "ConstructionYearChoices",
    "PrimaryHeatingTypeChoices",
    "NotificationTypeChoices",
]
