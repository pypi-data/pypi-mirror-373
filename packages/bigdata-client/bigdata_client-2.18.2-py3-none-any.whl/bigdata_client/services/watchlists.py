from typing import List

from bigdata_client.api.watchlist import (
    CreateWatchlistRequest,
    ShareUnshareWatchlistRequest,
    ShareWatchlistCompany,
    UpdateWatchlistRequest,
)
from bigdata_client.connection_protocol import BigdataConnectionProtocol
from bigdata_client.models.sharing import SharePermission
from bigdata_client.models.watchlists import Watchlist


class Watchlists:
    """For finding, iterating and doing operations with watchlist objects"""

    def __init__(self, api_connection: BigdataConnectionProtocol):
        self._api = api_connection

    def get(self, id_: str, /) -> Watchlist:
        """Retrieve a watchlist by its id."""
        api_response = self._api.get_single_watchlist(id_)
        watchlist = Watchlist(
            id=api_response.id,
            name=api_response.name,
            date_created=api_response.date_created,
            last_updated=api_response.last_updated,
            items=api_response.items,
            # Keep track of the api_connection within the Watchlist instance
            _api=self._api,
            company_shared_permission=api_response.shared.company.permission,
        )

        return watchlist

    def list(self, owned: bool = False) -> list[Watchlist]:
        """Retrieve all watchlist objects for the current user."""
        api_response = self._api.get_all_watchlists(owned)
        all_watchlist = [
            Watchlist(
                id=base_watchlist.id,
                name=base_watchlist.name,
                date_created=base_watchlist.date_created,
                last_updated=base_watchlist.last_updated,
                company_shared_permission=base_watchlist.shared.company.permission,
                items=None,
                # Keep track of the api_connection within the Watchlist instance
                _api=self._api,
            )
            for base_watchlist in api_response.root
        ]

        return all_watchlist

    def create(self, name: str, items: List[str]) -> Watchlist:
        """Creates a new watchlist in the system."""
        api_response = self._api.create_watchlist(
            CreateWatchlistRequest(name=name, items=items)
        )
        return Watchlist(
            id=api_response.id,
            name=api_response.name,
            date_created=api_response.date_created,
            last_updated=api_response.last_updated,
            company_shared_permission=api_response.shared.company.permission,
            items=api_response.items,
            # Keep track of the api_connection within the Watchlist instance
            _api=self._api,
        )

    def delete(self, id_: str, /) -> str:
        """Delete a watchlist by its id."""
        api_response = self._api.delete_watchlist(id_)
        return api_response.id

    def update(self, id_: str, /, name=None, items=None) -> Watchlist:
        """Update a watchlist by its id."""
        api_response = self._api.patch_watchlist(
            id_, UpdateWatchlistRequest(name=name, items=items)
        )
        return Watchlist(
            id=api_response.id,
            name=api_response.name,
            date_created=api_response.date_created,
            last_updated=api_response.last_updated,
            items=api_response.items,
            company_shared_permission=api_response.shared.company.permission,
            # Keep track of the api_connection within the Watchlist instance
            _api=self._api,
        )

    def share_with_company(self, id_: str):
        """Share a watchlist with the whole company."""
        api_response = self._api.share_unshare_watchlist(
            id_,
            ShareUnshareWatchlistRequest(
                company=ShareWatchlistCompany(permission=SharePermission.READ)
            ),
        )
        return api_response.model_dump()

    def unshare_with_company(self, id_: str):
        """Stop sharing a watchlist with the company"""
        api_response = self._api.share_unshare_watchlist(
            id_,
            ShareUnshareWatchlistRequest(
                company=ShareWatchlistCompany(permission=SharePermission.UNDEFINED)
            ),
        )
        return api_response.model_dump()
