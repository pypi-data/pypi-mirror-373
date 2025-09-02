from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from bigdata_client.models.advanced_search_query import Language as LanguageQuery
from bigdata_client.models.advanced_search_query import QueryComponent
from bigdata_client.models.search import Expression


class Language(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    query_type: Literal["language"] = Field(
        default="language", validation_alias="queryType"
    )

    # QueryComponent methods

    @property
    def _query_proxy(self):
        return LanguageQuery(self.id)

    def to_expression(self) -> Expression:
        return self._query_proxy.to_expression()

    def __or__(self, other: QueryComponent) -> QueryComponent:
        return self._query_proxy | other

    def __and__(self, other: QueryComponent) -> QueryComponent:
        return self._query_proxy & other

    def __invert__(self) -> QueryComponent:
        return ~self._query_proxy

    def make_copy(self) -> QueryComponent:
        return self._query_proxy.make_copy()
