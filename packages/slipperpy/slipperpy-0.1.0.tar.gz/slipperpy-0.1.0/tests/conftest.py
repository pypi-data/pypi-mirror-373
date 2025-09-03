"""Test configuration and fixtures."""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime


@pytest.fixture
def mock_httpx_response():
    """Mock httpx response."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "data": {
            "homes": [
                {
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
            ]
        }
    }
    return response


@pytest.fixture
def sample_consumption_data():
    """Sample consumption data."""
    return {
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


@pytest.fixture
def sample_user_data():
    """Sample user data."""
    return {
        "id": "user-1",
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "isActive": True,
        "isStaff": False,
        "isSuperuser": False,
        "phoneNumber": "+47123456789"
    }
