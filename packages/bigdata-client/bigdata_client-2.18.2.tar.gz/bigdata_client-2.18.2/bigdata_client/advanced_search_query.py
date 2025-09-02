from dataclasses import dataclass
from typing import Optional, Union

from bigdata_client.api.search import (
    DiscoveryPanelRequest,
    QueryChunksRequest,
    SavedSearchQueryResponse,
    SaveSearchQueryRequest,
)
from bigdata_client.daterange import AbsoluteDateRange, RollingDateRange
from bigdata_client.models.advanced_search_query import (
    QueryComponent,
    _expression_to_query_component,
)
from bigdata_client.models.search import (
    DocumentType,
    Expression,
    ExpressionTypes,
    SearchPaginationByCursor,
    SearchPaginationByOffset,
    SortBy,
)
from bigdata_client.settings import settings


@dataclass
class AdvancedSearchQuery:
    """
    A class to hold the query with the date range and sort by
    """

    query: QueryComponent
    date_range: Optional[Union[AbsoluteDateRange, RollingDateRange]] = None
    sortby: SortBy = SortBy.RELEVANCE
    scope: DocumentType = DocumentType.ALL
    rerank_threshold: Optional[float] = None

    def make_copy(self) -> "AdvancedSearchQuery":
        return AdvancedSearchQuery(
            date_range=self.date_range,
            query=self.query.make_copy(),
            sortby=self.sortby,
            scope=self.scope,
            rerank_threshold=self.rerank_threshold,
        )

    def to_query_chunks_api_request(
        self, pagination: Union[SearchPaginationByCursor, SearchPaginationByOffset]
    ) -> QueryChunksRequest:
        """
        Used when composing the request to perform a search using the
        /query-chunks endpoint.
        The difference between this method and to_save_search_request is that
        this one includes the date range in the expression and not outside
        """
        # Add time range
        query = self.query
        if self.date_range is not None:
            query = self.query & self.date_range
        expression = query.to_expression()
        return QueryChunksRequest(
            sort=self.sortby,
            scope=self.scope,
            ranking=settings.LLM.RANKING,
            pagination=pagination,
            hybrid=settings.LLM.USE_HYBRID,
            expression=expression,
            rerank_threshold=self.rerank_threshold,
        )

    def to_discovery_panel_api_request(self) -> DiscoveryPanelRequest:
        """
        Used when composing the request to get comentions.
        """
        # Add time range
        query = self.query
        if self.date_range is not None:
            query = self.query & self.date_range
        expression = query.to_expression()
        return DiscoveryPanelRequest(
            sort=self.sortby,
            scope=self.scope,
            ranking=settings.LLM.RANKING,
            hybrid=settings.LLM.USE_HYBRID,
            expression=expression,
        )

    def to_save_search_request(self) -> SaveSearchQueryRequest:
        """
        Used when composing the request to create a search.
        The difference between this method and to_query_chunks_api_request is that
        this one does not include the date range in the expression but outside
        """
        # Without date range
        expression = self.query.to_expression()
        date_expression = (
            [self.date_range.to_expression()] if self.date_range is not None else None
        )
        return SaveSearchQueryRequest(
            sort=self.sortby,
            scope=self.scope,
            ranking=settings.LLM.RANKING,
            hybrid=settings.LLM.USE_HYBRID,
            expression=expression,
            date=date_expression,
            rerank_threshold=self.rerank_threshold,
        )

    @classmethod
    def from_saved_search_response(
        cls, search_query: SavedSearchQueryResponse
    ) -> "AdvancedSearchQuery":
        """
        Deserializes a request/response object into a AdvancedSearchQuery object,
        if possible
        """
        date_range = None
        if search_query.date:
            if len(search_query.date) != 1:
                raise ValueError(
                    "Unexpected error. The date expression should have 1 value"
                )
            expression = search_query.date[0]
            date_range_raw = cls._get_field_from_expression(
                expression, ExpressionTypes.DATE
            )
            if date_range_raw is not None:
                date_range = cls._date_expression_to_date_range(date_range_raw)

        query = _expression_to_query_component(search_query.expression)

        return cls(
            query=query,
            date_range=date_range,
            sortby=search_query.sort,
            rerank_threshold=search_query.rerank_threshold,
        )

    @classmethod
    def _get_field_from_expression(
        cls, expression: Union[Expression, str], expression_type: ExpressionTypes
    ) -> Optional[Union[list, str]]:
        """Gets a field at the top level of an expression"""
        # It should always be an expression
        if isinstance(expression, Expression) and expression.type == expression_type:
            return expression.value

    @staticmethod
    def _date_expression_to_date_range(
        expression: Union[str, Expression, list[Union[str, Expression]]],
    ) -> Optional[Union[AbsoluteDateRange, RollingDateRange]]:
        if isinstance(expression, list):
            if len(expression) != 2:
                raise ValueError(
                    "Unexpected error. The date expression should have 2 values,"
                    f" but it has {len(expression)}"
                )
            return AbsoluteDateRange(expression[0], expression[1])
        else:
            return RollingDateRange(expression)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AdvancedSearchQuery):
            return False
        return (
            self.date_range == other.date_range
            and self.sortby == other.sortby
            and self.scope == other.scope
            and self.query.to_expression() == other.query.to_expression()
        )
