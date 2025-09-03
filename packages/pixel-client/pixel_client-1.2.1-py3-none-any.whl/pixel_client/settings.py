from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class PixelApiSettings(BaseSettings):
    """
    Settings for the Pixel API client
    """

    @classmethod
    def from_env_file(cls, env_file: Path | str) -> "PixelApiSettings":
        """Instantiate the settings from an environment file.

        Warning:
            Environment variables will always take precedence over the values in the file.
        """
        return cls(_env_file=env_file)  # type: ignore

    model_config = SettingsConfigDict(frozen=True)  # Makes it hashable

    PIXEL_API_URL: str
    """The URL of the Pixel API"""

    KEYCLOAK_SERVER_URL: str
    """The URL for the Keycloak server"""

    KEYCLOAK_CLIENT_ID: str = "frontend"
    """The client ID for the Keycloak server"""

    KEYCLOAK_USERNAME: str
    """The client secret for the Keycloak server"""

    KEYCLOAK_PASSWORD: SecretStr
    """The password for the Keycloak"""

    KEYCLOAK_REALM: SecretStr
    """The realm for the Keycloak server"""

    PIXEL_CLIENT_NO_VERSION_CHECK: bool = False
    """If True, the client will not check for a newer version of the pixel-client package on startup."""
