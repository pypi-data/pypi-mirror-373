"""Tests for Pydantic models."""

from datetime import datetime
from decimal import Decimal

from slipperpy.models import (
    HomeType,
    UserType,
    ConsumptionType,
    ElectricityPriceType,
    HomeAreaChoices,
    HomeCountryChoices,
    HomeTypeChoices,
)


def test_user_type_creation():
    """Test UserType model creation."""
    user_data = {
        "id": "user-1",
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "isActive": True,
        "isStaff": False,
        "isSuperuser": False,
    }
    
    user = UserType(**user_data)
    assert user.id == "user-1"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.email == "test@example.com"
    assert user.is_active is True


def test_home_type_creation():
    """Test HomeType model creation."""
    home_data = {
        "id": "home-1",
        "createdAt": "2025-01-01T10:00:00Z",
        "updatedAt": "2025-01-01T10:00:00Z",
        "meterId": "meter-123",
        "meterIdentification": "meter-ident-123",
        "name": "My Home",
        "street": "Test Street",
        "streetNumber": "123",
        "postalCode": "0123",
        "city": "Oslo",
        "country": "NO",
        "estimatedYearlyConsumption": 15000,
        "area": "NO1",
        "blocked": False,
        "isPlus": True,
        "isAutomatic": True,
        "maxKwh": 100,
        "type": "HOUSE"
    }
    
    home = HomeType(**home_data)
    assert home.id == "home-1"
    assert home.name == "My Home"
    assert home.street == "Test Street"
    assert home.country == HomeCountryChoices.NO
    assert home.area == HomeAreaChoices.NO1
    assert home.type == HomeTypeChoices.HOUSE


def test_consumption_type_creation():
    """Test ConsumptionType model creation."""
    consumption_data = {
        "id": "consumption-1",
        "createdAt": "2025-01-01T10:00:00Z",
        "updatedAt": "2025-01-01T10:00:00Z",
        "meterId": "meter-123",
        "date": "2025-01-01T00:00:00Z",
        "kwh": "25.5",
        "granularity": "DAY",
        "meteringType": "CONSUMPTION",
        "cost": "45.50",
        "tax": "11.38",
        "handout": "0.00",
        "tariff": "5.00",
        "tariffTax": "1.25",
        "enova": "0.01",
        "tariffAddition": "2.00",
        "planAddition": "1.50"
    }
    
    consumption = ConsumptionType(**consumption_data)
    assert consumption.id == "consumption-1"
    assert consumption.kwh == Decimal("25.5")
    assert consumption.cost == Decimal("45.50")
    assert consumption.granularity == "DAY"


def test_electricity_price_type_creation():
    """Test ElectricityPriceType model creation."""
    price_data = {
        "date": "2025-01-01T12:00:00Z",
        "area": "NO1",
        "price": "45.50",
        "granularity": "HOUR",
        "forecast": False
    }
    
    price = ElectricityPriceType(**price_data)
    assert price.area == "NO1"
    assert price.price == Decimal("45.50")
    assert price.granularity == "HOUR"
    assert price.forecast is False
