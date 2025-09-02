import enum
import os
import warnings
from typing import Optional, Union

from pydantic import BaseModel

from bigdata_client.auth import ApiKeyAuth, JWTAuth, Proxy
from bigdata_client.connection import BigdataConnection, UploadsConnection
from bigdata_client.jwt_utils import get_token_claim
from bigdata_client.services.chat_service import ChatService
from bigdata_client.services.content_search import ContentSearch
from bigdata_client.services.knowledge_graph import KnowledgeGraph
from bigdata_client.services.subscription import Subscription
from bigdata_client.services.uploads import Uploads
from bigdata_client.services.watchlists import Watchlists
from bigdata_client.settings import settings

JWT_CLAIM_ORGANIZATION_ID = "organization_id"


class Bigdata:
    """
    Represents a connection to RavenPack's Bigdata API.

    :ivar knowledge_graph: Proxy for the knowledge graph search functionality.
    :ivar search: Proxy object for the content search functionality.
    :ivar watchlists: Proxy object for the watchlist functionality.
    :ivar uploads: Proxy object for the internal content functionality.
    :ivar subscription: Proxy object for the subscription functionality.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        *,
        api_key: Optional[str] = None,
        bigdata_api_url: Optional[str] = None,
        bigdata_ws_url: Optional[str] = None,
        upload_api_url: Optional[str] = None,
        proxy: Optional[Proxy] = None,
        verify_ssl: Union[bool, str] = True
    ):
        if os.environ.get("BIGDATA_USER"):
            warnings.warn(
                "BIGDATA_USER is deprecated, use BIGDATA_USERNAME instead",
                DeprecationWarning,
                stacklevel=2,
            )

        auth_flow, auth_params = get_auth_flow(
            input_params=AuthParams(
                username=username, password=password, api_key=api_key
            ),
            env_params=AuthParams(
                username=os.environ.get("BIGDATA_USERNAME")
                or os.environ.get("BIGDATA_USER"),
                password=os.environ.get("BIGDATA_PASSWORD"),
                api_key=os.environ.get("BIGDATA_API_KEY"),
            ),
        )

        if are_proxies_in_env() and proxy:
            raise ValueError(
                "Setting both proxies in the environment and passing them as arguments is not allowed."
            )

        if auth_flow == AuthFlows.API_KEY:
            auth = ApiKeyAuth.from_api_key(
                api_key=auth_params.api_key,
                pool_maxsize=settings.MAX_PARALLEL_REQUESTS,
                proxy=proxy,
                verify=verify_ssl,
            )
            # The following is not yet supported with API keys: Upload api, sharing files with an org.
            self._upload_api = None
        else:
            auth = JWTAuth.from_username_and_password(
                auth_params.username,
                auth_params.password,
                clerk_frontend_url=str(settings.CLERK_FRONTEND_URL),
                clerk_instance_type=settings.CLERK_INSTANCE_TYPE,
                pool_maxsize=settings.MAX_PARALLEL_REQUESTS,
                proxy=proxy,
                verify=verify_ssl,
            )
            # The following is not yet supported with API keys: Upload api, sharing files with an org.
            organization_id = get_token_claim(
                token=auth._token_manager.get_session_token(),
                claim=JWT_CLAIM_ORGANIZATION_ID,
            )

            if upload_api_url is None:
                upload_api_url = str(settings.UPLOAD_API_URL)

            self._upload_api = UploadsConnection(
                auth, upload_api_url, organization_id=organization_id
            )
            self.uploads = Uploads(uploads_api=self._upload_api)

        if bigdata_api_url is None:
            bigdata_api_url = str(settings.BACKEND_API_URL)
        if bigdata_ws_url is None:
            bigdata_ws_url = str(settings.BACKEND_WS_API_URL)

        self._api = BigdataConnection(auth, bigdata_api_url, bigdata_ws_url)

        # Start the different services
        self.knowledge_graph = KnowledgeGraph(self._api)
        self.search = ContentSearch(self._api)
        self.watchlists = Watchlists(self._api)
        self.subscription = Subscription(
            api_connection=self._api, uploads_api_connection=self._upload_api
        )
        self.chat = ChatService(api_connection=self._api)


def are_proxies_in_env():
    proxys_keys = (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "WSS_PROXY",
        "http_proxy",
        "https_proxy",
        "wss_proxy",
    )
    return any(os.environ.get(key) for key in proxys_keys)


class AuthParams(BaseModel):
    api_key: Optional[str]
    username: Optional[str]
    password: Optional[str]


class AuthFlows(enum.Enum):
    API_KEY = enum.auto()
    USER_PWD = enum.auto()


def get_auth_flow(
    *, input_params: AuthParams, env_params: AuthParams
) -> tuple[AuthFlows, AuthParams]:
    username = input_params.username or env_params.username
    password = input_params.password or env_params.password
    api_key = input_params.api_key or env_params.api_key

    if not (username and password) and not api_key:
        raise ValueError("Username and password or API key must be provided")

    if input_params.api_key:
        flow = AuthFlows.API_KEY
    elif input_params.username:
        flow = AuthFlows.USER_PWD
    elif env_params.api_key:
        flow = AuthFlows.API_KEY
    else:  # if env_params.username
        flow = AuthFlows.USER_PWD

    return flow, AuthParams(username=username, password=password, api_key=api_key)
