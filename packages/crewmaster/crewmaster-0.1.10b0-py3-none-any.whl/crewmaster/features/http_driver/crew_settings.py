from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class CrewSettings(BaseSettings):
    """
    Clase de Pydantinc para manejar los settings

    Ver: https://fastapi.tiangolo.com/advanced/settings/
    """
    app_name: str
    app_version: str
    app_summary: str
    app_root_path: str = "/"
    # api key para Open AI
    llm_api_key_open_ai: str = ""
    llm_model_open_ai: str = ""
    llm_temperature_open_ai: int = 0

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env"
    )
