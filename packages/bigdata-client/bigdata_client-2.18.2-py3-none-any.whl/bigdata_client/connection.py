import uuid
from contextlib import suppress
from functools import wraps
from http import HTTPStatus
from json import JSONDecodeError, dumps
from typing import IO, Callable, Generator, Iterable, Optional, TypeVar, Union
from urllib.parse import urljoin

import aiohttp
import requests
from pydantic import BaseModel, ValidationError
from requests import Response
from websockets import ConnectionClosedError

from bigdata_client.api.chat import (
    ChatAskRequest,
    ChatResponse,
    ChatWSAuditTraceResponse,
    ChatWSCompleteEnrichedResponse,
    ChatWSCompleteResponse,
    ChatWSNextResponse,
    ChatWSSourcesResponse,
    CreateNewChat,
    GetChatListResponse,
)
from bigdata_client.api.knowledge_graph import (
    AutosuggestRequests,
    AutosuggestResponse,
    ByIdsRequest,
    ByIdsResponse,
    KnowledgeGraphTypes,
    get_discriminator_knowledge_graph_value,
    parse_autosuggest_response,
    parse_by_ids_response,
)
from bigdata_client.api.search import (
    DeleteSavedSearchResponse,
    DiscoveryPanelRequest,
    DiscoveryPanelResponse,
    ListSavedSearchesResponse,
    QueryChunksRequest,
    QueryChunksResponse,
    SavedSearchResponse,
    SaveSearchRequest,
    ShareSavedSearchRequest,
    UpdateSearchRequest,
)
from bigdata_client.api.subscription import (
    MyBigdataQuotaResponse,
    MyUploadQuotaResponse,
)
from bigdata_client.api.uploads import (
    DeleteFileResponse,
    FileResponse,
    FileStatus,
    GetDownloadPresignedUrlResponse,
    GetFileIndexStatusResponse,
    GetFileStatusResponse,
    ListFilesResponse,
    PostFileRequest,
    PostFileResponse,
)
from bigdata_client.api.watchlist import (
    CreateWatchlistRequest,
    CreateWatchlistResponse,
    DeleteSingleWatchlistResponse,
    GetSingleWatchlistResponse,
    GetWatchlistsResponse,
    ShareWatchlistResponse,
    UpdateSingleWatchlistResponse,
    UpdateWatchlistRequest,
)
from bigdata_client.auth import (
    AsyncRequestContext,
    AsyncResponseContext,
    BaseAuth,
    Proxy,
    WSAuth,
)
from bigdata_client.connection_management import RequestsPerMinuteController
from bigdata_client.constants import (
    MAX_REQUESTS_PER_MINUTE,
    REFRESH_FREQUENCY_RATE_LIMIT,
    TIME_BEFORE_RETRY_RATE_LIMITER,
    BackendErrorCodes,
)
from bigdata_client.daterange import AbsoluteDateRange
from bigdata_client.exceptions import (
    BigdataClientChatError,
    BigdataClientChatNotFound,
    BigdataClientRateLimitError,
    BigdataClientSimilarityPayloadTooLarge,
    RequestMaxLimitExceeds,
)
from bigdata_client.models.entities import Company
from bigdata_client.models.search import SearchChain
from bigdata_client.models.watchlists import Watchlist
from bigdata_client.services.knowledge_graph import FilterAnalyticCategory

CONCURRENT_AUTOSUGGEST_REQUESTS_LIMIT = 10
CHUNK_SIZE = 32 * 1024
REQUEST_BODY_LIMIT = 64 * 1024
SECONDS_WAITING_CHAT_RESPONSE = 60


class AsyncRequestPartialContext(BaseModel):
    """
    Context used to pass information to connection module for making async requests.
    Async requests are made in parallel, so each request is associated with an id to
    retrieve it from a list of responses.
    """

    id: str
    endpoint: str
    params: dict


json_types = Union[dict, list[dict]]

T = TypeVar("T")


class BigdataConnection:
    """
    The connection to the API.

    Contains the Auth object with the JWT and abstracts all the calls to the API,
    receiving and returning objects to/from the caller, while rate-limiting the number
    of requests per minute.
    For internal use only.
    """

    def __init__(self, auth: BaseAuth, backend_url: str, websocket_url: str):
        self.http = RateLimitedHTTPWrapper(auth, backend_url)
        self.ws = WSWrapper(
            auth, websocket_url, proxies=auth.proxies, verify=auth.verify
        )

    # Autosuggest

    def autosuggest(
        self,
        item: Optional[str],
        limit: int,
        categories: Optional[list[FilterAnalyticCategory]],
        group1: Optional[list[str]],
        group2: Optional[list[str]],
        group3: Optional[list[str]],
        group4: Optional[list[str]],
        group5: Optional[list[str]],
    ) -> list[KnowledgeGraphTypes]:
        """Calls POST /autosuggest/search"""
        if item is None:
            item = ""
        json_response = self.http.post(
            "autosuggest/search",
            json={
                "query": item,
                "perPage": limit,
                "category": categories,
                "group1": group1,
                "group2": group2,
                "group3": group3,
                "group4": group4,
                "group5": group5,
            },
        )
        return [parse_autosuggest_response(item) for item in json_response["results"]]

    def autosuggest_async(
        self,
        items: AutosuggestRequests,
        limit: int,
    ) -> AutosuggestResponse:
        """Calls GET /autosuggest/search_basic using aiohttp"""

        # Split the requests in batches of size CONCURRENT_AUTOSUGGEST_REQUESTS_LIMIT to not overload the service
        all_requests_input = [
            AsyncRequestPartialContext(
                id=item,
                endpoint="autosuggest/search_basic",
                params={"query": item, "limit": limit},
            )
            for item in items.root
        ]

        items_search_responses = []
        for batch in self._get_batches(
            all_requests_input, CONCURRENT_AUTOSUGGEST_REQUESTS_LIMIT
        ):
            items_search_responses.extend(self.http.async_get(batch))

        # For Watchlist results, add the reference to WatchlistApiOperations
        for item in items_search_responses:
            for result in item.response["results"]:
                if (
                    get_discriminator_knowledge_graph_value(result)
                    == Watchlist.model_fields["query_type"].default
                ):
                    result["_api"] = self

        return AutosuggestResponse(
            root={
                item.id: [
                    parse_autosuggest_response(item)
                    for item in item.response["results"]
                ]
                for item in items_search_responses
            }
        )

    @staticmethod
    def _get_batches(items: list[T], batch_size: int) -> Generator[list[T], None, None]:
        for idx in range(0, len(items), batch_size):
            yield items[idx : idx + batch_size]

    def by_ids(self, request: ByIdsRequest) -> ByIdsResponse:
        json_request = request.model_dump(exclude_none=True, by_alias=True)
        json_response = self.http.post("cqs/by-ids", json=json_request)
        return ByIdsResponse(
            {item: parse_by_ids_response(obj) for item, obj in json_response.items()}
        )

    # Search
    def query_chunks(self, request: QueryChunksRequest) -> QueryChunksResponse:
        """Calls POST /cqs/query-chunks"""
        json_request = request.model_dump(exclude_none=True, by_alias=True)
        json_request["searchChain"] = SearchChain.CLUSTERING  # FIXME for watchlists

        # set default rerank_freshness_weight and search_chain if rerank_threshold is set
        if "rerankThreshold" in json_request:
            json_request["rerankFreshnessWeight"] = 0.0
            json_request["searchChain"] = SearchChain.CLUSTERING_RERANK

        json_response = self.http.post("cqs/query-chunks", json=json_request)
        return QueryChunksResponse(**json_response)

    def get_search(self, id: str) -> SavedSearchResponse:
        """Calls GET /user-data/queries/{id}"""
        json_response = self.http.get(f"user-data/queries/{id}")
        try:
            return SavedSearchResponse(**json_response)
        except ValidationError as e:
            raise NotImplementedError(
                "Query expression may have unsupported expression types"
            ) from e

    def list_searches(
        self, saved: bool = True, owned: bool = True
    ) -> ListSavedSearchesResponse:
        """Calls GET /user-data/queries"""
        params = {}
        if saved:
            params["save_status"] = "saved"
        if owned:
            params["owned"] = "true"
        json_response = self.http.get("user-data/queries", params=params)
        return ListSavedSearchesResponse(**json_response)

    def save_search(self, request: SaveSearchRequest) -> SavedSearchResponse:
        """Calls POST /user-data/queries"""
        json_request = request.model_dump(exclude_none=True, by_alias=True)
        response = self.http.post("user-data/queries", json=json_request)
        return SavedSearchResponse(**response)

    def update_search(
        self, request: UpdateSearchRequest, search_id: str
    ) -> SavedSearchResponse:
        """Calls PATCH /user-data/queries/{id}"""
        json_request = request.model_dump(exclude_none=True, by_alias=True)
        response = self.http.patch(f"user-data/queries/{search_id}", json=json_request)
        return SavedSearchResponse(**response)

    def delete_search(self, id: str) -> DeleteSavedSearchResponse:
        """Calls DELETE /user-data/queries/{id}"""
        response = self.http.delete(f"user-data/queries/{id}")
        return DeleteSavedSearchResponse(**response)

    def share_search(
        self, id_: str, request: ShareSavedSearchRequest
    ) -> SavedSearchResponse:
        """Calls POST /user-data/queries/{id}/share"""
        json_request = request.model_dump(exclude_none=True, by_alias=True)
        json_response = self.http.post(
            f"user-data/queries/{id_}/share", json=json_request
        )
        return SavedSearchResponse(**json_response)

    def query_discovery_panel(
        self, request: DiscoveryPanelRequest
    ) -> DiscoveryPanelResponse:
        """Calls POST /cqs/discovery-panel"""
        json_request = request.model_dump(exclude_none=True, by_alias=True)
        json_response = self.http.post("cqs/discovery-panel", json=json_request)
        return DiscoveryPanelResponse(**json_response)

    # Watchlist
    def create_watchlist(
        self, request: CreateWatchlistRequest
    ) -> CreateWatchlistResponse:
        """Calls POST /user-data/watchlists"""
        json_request = request.model_dump(exclude_none=True, by_alias=True)

        json_response = self.http.post("user-data/watchlists", json=json_request)

        return CreateWatchlistResponse.model_validate(json_response)

    def get_single_watchlist(self, id_: str) -> GetSingleWatchlistResponse:
        """Calls GET /user-data/watchlists/{id_}"""
        json_response = self.http.get(f"user-data/watchlists/{id_}")

        return GetSingleWatchlistResponse(**json_response)

    def get_all_watchlists(self, owned: bool) -> GetWatchlistsResponse:
        """Calls GET /user-data/watchlists"""
        url = "user-data/watchlists"
        if owned:
            url += "?owned=true"
        json_response = self.http.get(url)

        return GetWatchlistsResponse(root=json_response["results"])

    def delete_watchlist(self, id_: str) -> DeleteSingleWatchlistResponse:
        """Calls DELETE /user-data/watchlists/{id_}"""
        json_response = self.http.delete(f"user-data/watchlists/{id_}")

        return DeleteSingleWatchlistResponse(**json_response)

    def patch_watchlist(
        self, id_: str, request: UpdateWatchlistRequest
    ) -> UpdateSingleWatchlistResponse:
        """Calls PATCH /user-data/watchlists/{id_}"""
        json_request = request.model_dump(exclude_none=True, by_alias=True)
        json_response = self.http.patch(f"user-data/watchlists/{id_}", json_request)

        return UpdateSingleWatchlistResponse.model_validate(json_response)

    def share_unshare_watchlist(
        self, id_: str, request: UpdateWatchlistRequest
    ) -> ShareWatchlistResponse:
        """Calls POST /user-data/watchlists/{id_}/share"""
        json_request = request.model_dump(exclude_none=True, by_alias=True)
        json_response = self.http.post(
            f"user-data/watchlists/{id_}/share", json_request
        )

        return ShareWatchlistResponse.model_validate(json_response)

    def download_annotated_dict(self, id_: str) -> dict:
        """Calls GET /rpjson/{id_}"""
        json_response = self.http.get(f"rpjson/{id_}")
        if presigned_url := json_response.get("url"):
            response = requests.get(presigned_url)
            response.raise_for_status()
            return response.json()
        return json_response

    def get_my_quota(self) -> MyBigdataQuotaResponse:
        """Calls GET /user-data/quota"""
        json_response = self.http.get("user-data/quota")
        return MyBigdataQuotaResponse(**json_response)

    def get_companies_by_isin(self, isins: list[str]) -> list[Optional[Company]]:
        json_response = self.http.post("/cqs/companies/isin", json=isins)
        return self._format_company_from_cqs_response(isins, json_response)

    def get_companies_by_cusip(self, cusips: list[str]) -> list[Optional[Company]]:
        json_response = self.http.post("/cqs/companies/cusip", json=cusips)
        return self._format_company_from_cqs_response(cusips, json_response)

    def get_companies_by_sedol(self, sedols: list[str]) -> list[Optional[Company]]:
        json_response = self.http.post("/cqs/companies/sedol", json=sedols)
        return self._format_company_from_cqs_response(sedols, json_response)

    def get_companies_by_listing(self, listings: list[str]) -> list[Optional[Company]]:
        json_response = self.http.post("/cqs/companies/listing", json=listings)
        return self._format_company_from_cqs_response(listings, json_response)

    def send_tracking_event(self, trace_event: "TraceEvent"):  # noqa: F821
        return self.http.post(
            "/track-events", json=trace_event.model_dump(exclude_none=True)
        )

    def get_chat(self, id_: str) -> ChatResponse:
        json_response = self.http.get(f"/user-data/chats/{id_}")
        return ChatResponse(**json_response)

    def get_all_chats(self) -> GetChatListResponse:
        json_response = self.http.get("/user-data/chats")
        return GetChatListResponse(root=json_response)

    def delete_chat(self, id_: str):
        self.http.delete(f"/user-data/chats/{id_}")

    def create_chat(self, new_chat: CreateNewChat):
        json_response = self.http.post("/user-data/chats", json=new_chat.model_dump())
        return ChatResponse(**json_response)

    def ask_chat(
        self,
        id_: str,
        question: str,
        *,
        scope: Optional[str] = None,
        source_filter: Optional[list[str]] = None,
    ) -> Generator[
        Union[
            str,
            ChatWSCompleteEnrichedResponse,
            ChatWSAuditTraceResponse,
            ChatWSSourcesResponse,
        ],
        None,
        None,
    ]:
        request_id = str(uuid.uuid4())
        msg = ChatAskRequest(
            chat_id=id_,
            input_message=question,
            request_id=request_id,
            scope=scope,
            sources=source_filter,
        )
        with self.ws.get_ws_auth() as ws:
            ws.send(msg.model_dump(by_alias=True))
            next_contents = []

            while True:
                try:
                    response = ws.recv(timeout=SECONDS_WAITING_CHAT_RESPONSE)
                except TimeoutError:
                    raise BigdataClientChatError("Timeout waiting for chat response")
                except ConnectionClosedError as e:
                    raise BigdataClientChatError(e) from e

                response_type = response.get("type", "UNKNOWN")

                if response_type == "FAILED":
                    self._chat_error(response)

                elif response_type == "AUDIT_TRACE":
                    audit_trace = ChatWSAuditTraceResponse.model_validate(response)
                    yield audit_trace

                elif response_type == "NEXT":
                    next_data = ChatWSNextResponse.model_validate(response)
                    next_contents.append(next_data.content)
                    yield next_data.content

                elif response_type == "SOURCES":
                    sources_data = ChatWSSourcesResponse.model_validate(response)
                    yield sources_data

                elif response_type == "COMPLETE":
                    complete_message = ChatWSCompleteResponse.model_validate(response)
                    complete_enriched_message = ChatWSCompleteEnrichedResponse(
                        **complete_message.model_dump(),
                        aggregated_next_content="".join(next_contents),
                    )
                    yield complete_enriched_message
                    break

                else:
                    continue

    def _chat_error(self, response):
        message = response.get("message") or "Invalid response from chat"
        error_code = response.get("errorCode")
        if error_code == 404:
            raise BigdataClientChatNotFound(message)
        raise BigdataClientChatError(message)

    def _format_company_from_cqs_response(
        self, original_list: list[str], response: dict
    ) -> list[Optional[Company]]:
        return [
            (
                Company.model_validate(response[value])
                if response.get(value) is not None
                else None
            )
            for value in original_list
        ]


class UploadsConnection:
    """
    The connection to the Uploads API.

    Contains the Auth object with the JWT and abstracts all the calls to the API,
    receiving and returning objects to/from the caller.
    For internal use only.
    """

    def __init__(self, auth: BaseAuth, api_url: str, organization_id: Optional[str]):
        self.http = HTTPWrapper(auth, api_url)
        # organization_id is set at this level so when an object performs an action that requires it (e.g: sharing)
        # it won't need to get & store its value, instead the sharing method already has it.
        self._organization_id = organization_id

    def list_files(
        self,
        date_range: Optional[AbsoluteDateRange],
        tags: Optional[list[str]],
        status: Optional[FileStatus],
        file_name: Optional[str],
        folder_id: Optional[str],
        page_size: int,
        shared: Optional[bool],
        offset: int,
    ) -> ListFilesResponse:
        start, end = None, None
        if date_range is not None:
            start, end = date_range.to_string_tuple()
        params = {
            "start_date": start,
            "end_date": end,
            "tags": tags,
            "status": status,
            "file_name": file_name,
            "folder_id": folder_id,
            "page_size": page_size,
            "shared": "true" if shared else None,  # FIXME API expects snake case 'true'
            "offset": offset,
        }

        params = {k: v for k, v in params.items() if v is not None}
        json_response = self.http.get("files", params=params)
        return ListFilesResponse(**json_response)

    def get_file(self, id: str) -> FileResponse:
        json_response = self.http.get(f"files/{id}/metadata")
        return FileResponse(**json_response)

    def post_file(self, request: PostFileRequest) -> PostFileResponse:
        json_request = request.model_dump(exclude_none=True, by_alias=True)
        json_response = self.http.post("files", json=json_request)
        return PostFileResponse(**json_response)

    def get_file_status(self, file_id: str) -> GetFileStatusResponse:
        json_response = self.http.get(f"files/{file_id}/status")
        return GetFileStatusResponse(**json_response)

    def get_file_index_status(self, file_id: str) -> GetFileIndexStatusResponse:
        json_response = self.http.get(f"files/{file_id}/index-status")
        return GetFileIndexStatusResponse(**json_response)

    def delete_file(self, file_id: str) -> DeleteFileResponse:
        response = self.http.delete(f"files/{file_id}")
        return DeleteFileResponse(**response)

    def get_download_presigned_url(
        self, file_id: str
    ) -> GetDownloadPresignedUrlResponse:
        json_response = self.http.get(f"files/{file_id}")
        return GetDownloadPresignedUrlResponse(**json_response)

    def download_analytics(self, file_id: str) -> Iterable[bytes]:
        return self.http.get_chunks(f"files/{file_id}/analytics", chunk_size=CHUNK_SIZE)

    def download_annotated(self, file_id: str) -> Iterable[bytes]:
        return self.http.get_chunks(f"files/{file_id}/annotated", chunk_size=CHUNK_SIZE)

    def download_text(self, file_id: str) -> Iterable[bytes]:
        return self.http.get_chunks(
            f"files/{file_id}/text-extraction", chunk_size=CHUNK_SIZE
        )

    def share_file_with_company(self, file_id: str) -> FileResponse:
        if not self._organization_id:
            raise NotImplementedError(
                "Sharing an item with the organization is not possible with the used auth method."
            )

        share_model = {"shared_with": [self._organization_id]}
        json_response = self.http.patch(f"files/{file_id}/metadata", json=share_model)
        return FileResponse(**json_response)

    def unshare_file_with_company(self, file_id: str) -> FileResponse:
        unshare_model = {"shared_with": []}
        json_response = self.http.patch(f"files/{file_id}/metadata", json=unshare_model)
        return FileResponse(**json_response)

    def get_my_quota(self) -> MyUploadQuotaResponse:
        """Calls GET /1.0/quota"""
        json_response = self.http.get("quota")
        return MyUploadQuotaResponse(**json_response)

    def update_file_tags(self, file_id: str, tags: list[str]) -> FileResponse:
        body = {"tags": tags}
        json_response = self.http.patch(f"files/{file_id}/metadata", json=body)
        return FileResponse(**json_response)

    def list_my_tags(self) -> list[str]:
        return self.http.get("files/tags")

    def list_tags_shared_with_me(self) -> list[str]:
        return self.http.get("files/tags?shared=true")


def upload_file(url: str, file_descriptor: IO):
    """Used to upload files to third-parties like S3"""
    response = requests.put(
        url,
        data=file_descriptor,
        headers={
            "x-amz-server-side-encryption": "AES256",
            "Content-Type": "application/octet-stream",
        },
    )
    response.raise_for_status()


def get_chunks_from_presigned_url(
    url: str, chunk_size: int = CHUNK_SIZE
) -> Iterable[bytes]:
    """Used to download files from third-parties like S3"""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    for chunk in response.iter_content(chunk_size=chunk_size):
        yield chunk


def enrich_http_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.HTTPError as error:
            backend_msg = "N/A"
            response = error.response
            with suppress(KeyError, AttributeError, JSONDecodeError):
                backend_msg = response.json()["message"]
            raise requests.HTTPError(
                f"{str(error)}\nBackend response: {backend_msg}",
                response=error.response,
                request=error.request,
            ) from error

    return wrapper


def default_update_headers(headers: dict) -> dict:
    return headers


class CustomHttpHeader:
    update_headers: Callable[[dict], dict] = default_update_headers

    @classmethod
    def register(cls, update_headers: Callable[[dict], dict]) -> None:
        if update_headers:
            cls.update_headers = update_headers

    @classmethod
    def resolve(cls, headers: dict) -> dict:
        return cls.update_headers(headers)


class HTTPWrapper:
    """
    A basic connection to perform authenticated HTTP GET, POST, PATCH, DELETE requests.
    """

    def __init__(self, auth: BaseAuth, api_url: str):
        self.auth = auth
        self.api_url = api_url

    @enrich_http_errors
    def get(self, endpoint: str, params: dict = None) -> Union[dict, list]:
        params = params or {}
        url = self._get_url(endpoint)
        response = self._make_auth_request("GET", url, params=params)
        return response.json()

    @enrich_http_errors
    def post(self, endpoint: str, json: json_types) -> json_types:
        self._validate_json_size(json)
        url = self._get_url(endpoint)
        response = self._make_auth_request("POST", url, json=json)

        return response.json()

    @enrich_http_errors
    def patch(self, endpoint: str, json: json_types) -> json_types:
        self._validate_json_size(json)
        url = self._get_url(endpoint)
        response = self._make_auth_request("PATCH", url, json=json)
        return response.json()

    @enrich_http_errors
    def put(self, endpoint: str, json: json_types) -> json_types:
        self._validate_json_size(json)
        url = self._get_url(endpoint)
        response = self._make_auth_request("PUT", url, json=json)
        return response.json()

    @enrich_http_errors
    def delete(self, endpoint: str) -> json_types:
        url = self._get_url(endpoint)
        response = self._make_auth_request("DELETE", url)
        return response.json()

    @enrich_http_errors
    def get_chunks(self, endpoint: str, chunk_size: int) -> Iterable[bytes]:
        """Does an HTTP GET but returns the response in chunks of bytes."""
        url = self._get_url(endpoint)
        response = self._make_auth_request("GET", url, stream=True)
        for chunk in response.iter_content(chunk_size=chunk_size):
            yield chunk

    def _make_auth_request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        stream: Optional[bool] = None,
        json: Optional[json_types] = None,
    ) -> Response:
        try:
            headers = {}
            custom_headers = CustomHttpHeader.resolve(headers)
            response = self.auth.request(
                method,
                url,
                params=params,
                stream=stream,
                json=json,
                headers=custom_headers,
            )
            response.raise_for_status()
            return response
        except requests.HTTPError as error:
            response = error.response
            backend_msg = "N/A"
            self.check_for_backend_codes(response)
            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                with suppress(KeyError, AttributeError, JSONDecodeError):
                    backend_msg = response.json()["message"]
                raise BigdataClientRateLimitError(backend_msg) from error
            else:
                raise

    @staticmethod
    def check_for_backend_codes(response: Response):
        with suppress(KeyError, AttributeError, JSONDecodeError):
            if response.json()["errorCode"] == BackendErrorCodes.QUERY_TOO_MANY_TOKENS:
                raise BigdataClientSimilarityPayloadTooLarge(response.json()["message"])

    # Async wrappers for HTTP methods
    def async_get(
        self, async_partial_contexts: list[AsyncRequestPartialContext]
    ) -> list[AsyncResponseContext]:
        all_requests_context = [
            AsyncRequestContext(
                id=partial_context.id,
                url=self._get_url(partial_context.endpoint),
                params=partial_context.params,
            )
            for partial_context in async_partial_contexts
        ]
        try:
            response = self.auth.async_requests("GET", all_requests_context)
        except aiohttp.client_exceptions.ClientResponseError as err:
            if err.status == HTTPStatus.TOO_MANY_REQUESTS:
                raise BigdataClientRateLimitError
            raise

        return response

    # Other helpers

    def _get_url(self, endpoint: str) -> str:
        return urljoin(str(self.api_url), str(endpoint))

    def _validate_json_size(self, json: json_types):
        json_payload = dumps(json)
        payload_size = len(json_payload.encode("utf-8"))
        if payload_size > REQUEST_BODY_LIMIT:
            raise RequestMaxLimitExceeds(payload_size, REQUEST_BODY_LIMIT)


class RateLimitedHTTPWrapper(HTTPWrapper):
    """Extension on HTTPWrapper that applies rate limiting to synchronous requests"""

    def __init__(self, auth: BaseAuth, api_url: str):
        super().__init__(auth, api_url)
        self.request_controller = RequestsPerMinuteController(
            max_requests_per_min=MAX_REQUESTS_PER_MINUTE,
            rate_limit_refresh_frequency=REFRESH_FREQUENCY_RATE_LIMIT,
            seconds_before_retry=TIME_BEFORE_RETRY_RATE_LIMITER,
        )

    @wraps(HTTPWrapper._make_auth_request)
    def _make_auth_request(self, *args, **kwargs):
        return self.request_controller(super()._make_auth_request, *args, **kwargs)


class WSWrapper:
    def __init__(
        self,
        auth: BaseAuth,
        api_url: str,
        proxies: Optional[dict],
        verify: Union[bool, str],
    ):
        self.auth = auth
        self.api_url = api_url
        self.proxies = proxies
        self.verify = verify

    def get_ws_auth(self) -> WSAuth:
        proxy = (
            Proxy(url=self.proxies["wss"], protocol="wss")
            if (self.proxies and self.proxies.get("wss"))
            else None
        )
        return self.auth.get_ws_auth(self.api_url, proxy=proxy, verify=self.verify)
