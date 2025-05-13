import pytest
from unittest.mock import patch, Mock
import sys
import json
from list_models import get_models

# filepath: src/test_list_models.py

@pytest.fixture
def valid_models_response():
    return {
        "data": [
            {
                "id": "test-model",
                "created": 1699000000,
                "top_provider": {
                    "context_length": 4096
                },
                "pricing": {
                    "prompt": "0.0001",
                    "completion": "0.0002"
                }
            }
        ]
    }

@pytest.fixture
def mock_config():
    return {
        "api_url": "https://test-api.com",
        "api_key": "test-key-123"
    }

def test_get_models_success(mock_config, valid_models_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: valid_models_response
        )
        
        result = get_models(mock_config["api_url"], mock_config["api_key"])
        
        mock_get.assert_called_once_with(
            f"{mock_config['api_url']}/models",
            headers={"Authorization": f"Bearer {mock_config['api_key']}"}
        )
        assert result == valid_models_response["data"]

def test_get_models_api_error(mock_config):
    with patch('requests.get') as mock_get:
        mock_get.return_value = Mock(
            status_code=401,
            text="Unauthorized"
        )
        
        with pytest.raises(SystemExit) as exc_info:
            get_models(mock_config["api_url"], mock_config["api_key"])
        
        assert exc_info.type == SystemExit
        assert exc_info.value.code == 1

def test_get_models_missing_data(mock_config):
    with patch('requests.get') as mock_get:
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {"error": "No data"}
        )
        
        with pytest.raises(KeyError):
            get_models(mock_config["api_url"], mock_config["api_key"])