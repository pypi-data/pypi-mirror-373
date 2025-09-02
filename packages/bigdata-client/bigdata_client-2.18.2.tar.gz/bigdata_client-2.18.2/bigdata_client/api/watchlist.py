from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic.alias_generators import to_camel

from bigdata_client.models.sharing import SharePermission


class DeleteSingleWatchlistResponse(BaseModel):
    id: str


class ShareWatchlistCompany(BaseModel):
    permission: SharePermission


class ShareUnshareWatchlistRequest(BaseModel):
    company: ShareWatchlistCompany
    users: list[str] = []


class ShareUnshareWatchlistResponse(BaseModel):
    company: ShareWatchlistCompany
    users: list[str] = []


class WatchlistApiResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    id: str = Field(validation_alias="key")
    name: str
    date_created: str
    last_updated: str
    shared: ShareUnshareWatchlistResponse
    # Optional since 'items' is not returned for lists of watchlist
    items: Optional[list[str]] = None


class GetSingleWatchlistResponse(WatchlistApiResponse): ...


class GetWatchlistsResponse(RootModel[list]):
    root: list[WatchlistApiResponse]


class CreateWatchlistRequest(BaseModel):
    name: str
    items: list[str]


class UpdateWatchlistRequest(BaseModel):
    name: Optional[str]
    items: Optional[list[str]]


class CreateWatchlistResponse(WatchlistApiResponse): ...


class UpdateSingleWatchlistResponse(WatchlistApiResponse): ...


class WatchlistSharingPermissions(BaseModel):
    editable: bool


class ShareWatchlistResponse(WatchlistApiResponse):
    permissions: WatchlistSharingPermissions
