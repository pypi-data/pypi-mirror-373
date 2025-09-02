from openapi.api_client import ApiClient
from openapi.configuration import Configuration
from openapi.api.auth_api import AuthApi
from openapi.models.login_request import LoginRequest
import jwt
from datetime import datetime, timedelta
from openapi.rest import RESTClientObject


class VayuClient:
    __access_token: str = None
    __expires_at: datetime = None
    __api_key: str = None
    __host: str = None
    __token_expiry_threshold = timedelta(minutes=5)

    def __init__(self, api_key: str, host: str = None):
        self.__access_token = None
        self.__host = host
        self.__api_key = api_key

    @property
    def access_token(self):
        return self.__access_token

    @property
    def is_logged_in(self):
        return self.__access_token is not None

    @property
    def client(self):
        configuration = Configuration(host=self.__host, api_key=self.__access_token)
        client = ApiClient(configuration)
        client.rest_client = AutoTokenRefresherRESTClient(self, configuration)
        return client

    def login(self):
        configuration = Configuration(host=self.__host)
        client = ApiClient(configuration)
        api = AuthApi(client)
        login_request = LoginRequest(refreshToken=self.__api_key)
        refresh_response = api.login(login_request)

        self.__access_token = refresh_response.access_token

        decoded_token = jwt.decode(
            self.__access_token, options={"verify_signature": False}
        )
        self.__expires_at = datetime.fromtimestamp(decoded_token["exp"])

    def refresh_token(self):
        if (
            self.__access_token is None
            or datetime.now() + self.__token_expiry_threshold > self.__expires_at
        ):
            
            self.login()

    def validate_logged_in(self):
        if not self.is_logged_in:
            raise RuntimeError(
                "Vayu client is not logged in. Please login before calling this method"
            )


class AutoTokenRefresherRESTClient(RESTClientObject):
    def __init__(self, vayu_client: VayuClient, configuration: Configuration, *args, **kwargs):
        super().__init__(configuration, *args, **kwargs)
        self.vayu_client = vayu_client

    def request(self, method, url, headers=None, **kwargs):
        if "/login" not in url:
            self.vayu_client.refresh_token()
            if headers is None:
                headers = {}
            headers["Authorization"] = f"Bearer {self.vayu_client.access_token}"

        return super().request(method, url, headers=headers, **kwargs)


__all__ = ["VayuClient"]
