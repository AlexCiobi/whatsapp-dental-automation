from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    whatsapp_token: str
    whatsapp_phone_number_id: str
    whatsapp_verify_token: str
    anthropic_api_key: str
    vapi_api_key: str
    vapi_phone_number_id: str

    model_config = {"env_file": ".env"}


settings = Settings()
