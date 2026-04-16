from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GA Training Portal"
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite:///./ga_training.db"
    session_cookie_name: str = "ga_training_session"
    secure_cookies: bool = False
    aws_region: str = ""
    aws_default_region: str = ""
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    handbook_path: str = "app/data/student_handbook.txt"
    training_content_path: str = "app/templates"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
