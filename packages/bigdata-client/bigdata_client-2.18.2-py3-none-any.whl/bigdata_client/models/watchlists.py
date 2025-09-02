from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from pydantic.alias_generators import to_camel

from bigdata_client.api.watchlist import (
    ShareUnshareWatchlistRequest,
    ShareWatchlistCompany,
    UpdateWatchlistRequest,
)
from bigdata_client.connection_protocol import BigdataConnectionProtocol
from bigdata_client.models.sharing import SharePermission


class Watchlist(BaseModel):
    """Used to represent a watchlist"""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
    id: str = Field(validation_alias="key")
    name: str
    date_created: Optional[datetime] = None  # Not returned by autosuggest
    last_updated: Optional[datetime] = None  # Not returned by autosuggest
    query_type: Literal["watchlist"] = Field(
        default="watchlist", validation_alias="queryType"
    )
    company_shared_permission: SharePermission = SharePermission.UNDEFINED

    _items_initialized: bool = PrivateAttr(default=False)
    _items = PrivateAttr(default=[])

    # Keeps track of the connection to Bigdata
    _api: BigdataConnectionProtocol

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if "_api" not in kwargs:
            raise ValueError("Initialize _api first")
        self._api = kwargs["_api"]

        if "items" in kwargs and kwargs["items"] is not None:
            self._items = kwargs["items"]
            self._items_initialized = True

        if "shared" in kwargs:
            self.company_shared_permission = (
                SharePermission.READ
                if kwargs["shared"].company.permission == SharePermission.READ
                else None
            )

    @property
    def items(self) -> list[str]:
        if not self._items_initialized:
            self._items = self._api.get_single_watchlist(self.id).items or []
            self._items_initialized = True
        return self._items

    @items.setter
    def items(self, value: list[str]):
        self._items = value
        self._items_initialized = True

    def __eq__(self, other):
        # To avoid problems when comparing 2 objects with different privateAttr
        return self.model_dump() == other.model_dump()

    # Watchlist operations

    def save(self):
        """Save a watchlist"""
        self._api.patch_watchlist(
            self.id, UpdateWatchlistRequest(name=self.name, items=self.items)
        )

    def share_with_company(self):
        """Share this watchlist with every member of the company"""
        self._api.share_unshare_watchlist(
            self.id,
            ShareUnshareWatchlistRequest(
                company=ShareWatchlistCompany(permission=SharePermission.READ)
            ),
        )
        self.company_shared_permission = SharePermission.READ

    def unshare_with_company(self):
        """Stop sharing this watchlist with every member of the company"""
        self._api.share_unshare_watchlist(
            self.id,
            ShareUnshareWatchlistRequest(
                company=ShareWatchlistCompany(permission=SharePermission.UNDEFINED)
            ),
        )
        self.company_shared_permission = SharePermission.UNDEFINED

    def delete(self):
        """Delete the watchlist"""
        return self._api.delete_watchlist(self.id).id
