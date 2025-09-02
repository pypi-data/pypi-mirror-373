from typing import Optional, Union

from bigdata_client.connection import BigdataConnection
from bigdata_client.daterange import AbsoluteDateRange, RollingDateRange
from bigdata_client.models.advanced_search_query import QueryComponent
from bigdata_client.models.search import DocumentType, SortBy
from bigdata_client.search import Search


class ContentSearch:
    def __init__(self, api_connection: BigdataConnection):
        self._api = api_connection

    def new(
        self,
        query: QueryComponent,
        date_range: Optional[Union[AbsoluteDateRange, RollingDateRange]] = None,
        sortby: SortBy = SortBy.RELEVANCE,
        scope: DocumentType = DocumentType.ALL,
        rerank_threshold: Optional[float] = None,
    ) -> Search:
        """
        Creates a new search object that allows you to perform a search on
        keywords, entities, etc.

        Example usage:

        >>> query = Entity("228D42") & Keyword("tesla")  # doctest: +SKIP
        >>> search = bigdata.search.new(
        ...    query,
        ...    date_range=RollingDateRange.LAST_WEEK,
        ...    sortby=SortBy.RELEVANCE,
        ...    scope=DocumentType.ALL
        ... )                               # doctest: +SKIP
        >>> search.save()                   # doctest: +SKIP
        >>> for document in search.limit_documents(100): # doctest: +SKIP
        >>>     print(document)                # doctest: +SKIP
        >>> print(search.get_summary())     # doctest: +SKIP
        >>> search.delete()                 # doctest: +SKIP
        """
        return Search.from_query(
            self._api,
            query,
            date_range=date_range,
            sortby=sortby,
            scope=scope,
            rerank_threshold=rerank_threshold,
        )

    def get(self, id_, /) -> Search:
        """Retrieve a saved search by its id."""
        response = self._api.get_search(id_)
        return Search.from_saved_search_response(self._api, response)

    def list(self) -> list[Search]:
        """Retrieve all saved searches for the current user."""
        list_response = self._api.list_searches()
        searches = []
        for search in list_response.results:
            try:
                response = self._api.get_search(search.id)
            except NotImplementedError:
                print(
                    f"Skipping search {search.id} because it has an unsupported expression type"
                )
                continue
            searches.append(Search.from_saved_search_response(self._api, response))
        return searches

    def delete(self, id_, /):
        """Delete a saved search by its id."""
        self._api.delete_search(id_)
