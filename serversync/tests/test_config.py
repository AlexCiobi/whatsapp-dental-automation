import os
import pytest


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test_key")
    monkeypatch.setenv("WHATSAPP_TOKEN", "test_token")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "123")
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "verify")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("VAPI_API_KEY", "vapi_key")
    monkeypatch.setenv("VAPI_PHONE_NUMBER_ID", "vapi_phone")

    import importlib
    import config
    importlib.reload(config)

    assert config.settings.supabase_url == "https://test.supabase.co"
    assert config.settings.whatsapp_phone_number_id == "123"
