"""pytest session fixtures"""

import tomllib

import pytest
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for tests"""

    ldap_address: str
    ldap_user_bind_dn: str
    ldap_password: SecretStr
    ldap_port: int = 636

    model_config = SettingsConfigDict(env_prefix="TEST_CONF_")


def pytest_addoption(parser: pytest.Parser) -> None:

    parser.addoption("--config", action="store", default="./test_config.toml")


@pytest.fixture(scope="session")
def external_settings(
    request: pytest.FixtureRequest,
) -> Settings:
    config = request.config.getoption("config", default=None)
    config_dict = {}
    if config:
        with open(request.config.getoption("config"), "rb") as fp:
            config_dict = tomllib.load(fp)
    return Settings.model_validate(config_dict)
