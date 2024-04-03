import os.path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), '.env')


class Config(BaseSettings):
    discord_bot_token: SecretStr
    discord_client_id: SecretStr

    osu_client_id: SecretStr
    osu_client_secret: SecretStr

    ripple_token: SecretStr

    osu_db_url: SecretStr

    model_config = SettingsConfigDict(env_file=DOTENV, env_file_encoding='utf-8', case_sensitive=False)


config = Config()
