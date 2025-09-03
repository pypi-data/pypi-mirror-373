import logging
import httpx

logger = logging.getLogger(__name__)


class KeyCloakAuth(httpx.Auth):
    """Auth class for KeyCloak authentication"""

    def __init__(
        self,
        keycloak_server_url: str,
        realm: str,
        client_id: str,
        username: str,
        password: str,
    ):
        """Initialize the KeyCloakAuth class"""
        self.token_url = (
            f"{keycloak_server_url}/realms/{realm}/protocol/openid-connect/token"
        )
        self.client_id = client_id
        self.username = username
        self.password = password
        self.realm = realm
        self._token = None

    def auth_flow(self, request):
        """Flow for the authentication.

        Note:
            See [httpx documentation](https://www.python-httpx.org/advanced/authentication) on custom authentication schemes
        """
        request.headers["Authorization"] = f"Bearer {self.token}"
        response = yield request
        if response.status_code == 401:
            logger.info("Token expired, retrieving new token")
            self._token = None  # Clear the token
            request.headers["Authorization"] = f"Bearer {self.token}"
            yield request

    @property
    def token(self):
        if self._token is None:
            self._token = self._retrieve_token()
        return self._token

    def _retrieve_token(self):
        # Use the token_url to get the token
        with httpx.Client() as client:
            logger.info(f"Retrieving token from {self.token_url}")
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "username": self.username,
                    "password": self.password,
                    "scope": "openid email profile",
                    "grant_type": "password",
                },
                headers=headers,
            )
            response.raise_for_status()
            return response.json()["access_token"]
