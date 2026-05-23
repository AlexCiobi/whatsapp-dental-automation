import os
import pytest
from unittest.mock import MagicMock


# Set env vars before any module imports
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test_key")
os.environ.setdefault("WHATSAPP_TOKEN", "test_token")
os.environ.setdefault("WHATSAPP_PHONE_NUMBER_ID", "123")
os.environ.setdefault("WHATSAPP_VERIFY_TOKEN", "verify_me")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test")
os.environ.setdefault("VAPI_API_KEY", "vapi_key")
os.environ.setdefault("VAPI_PHONE_NUMBER_ID", "vapi_phone")


@pytest.fixture
def mock_supabase():
    client = MagicMock()
    client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
    return client


@pytest.fixture
def app_client():
    try:
        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app)
    except ImportError:
        # main.py not created yet in this task
        return None
