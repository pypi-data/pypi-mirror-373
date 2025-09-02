from abc import abstractmethod
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from bigdata_client.enum_utils import StrEnum
from bigdata_client.models.advanced_search_query import Entity, QueryComponent
from bigdata_client.models.search import Expression


class QueryComponentMixin(BaseModel):
    """For making queries"""

    # QueryComponent methods

    @property
    @abstractmethod
    def _query_proxy(self):
        """Instance responsible for query operations"""

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


class CompanyType(StrEnum):
    PUBLIC = "Public"
    PRIVATE = "Private"


class Company(QueryComponentMixin):
    """
    Represents an entity in RavenPack's dataset.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: Literal["COMP"] = Field(default="COMP", validation_alias="entityType")
    company_type: Optional[str] = Field(validation_alias="group1", default=None)
    country: Optional[str] = Field(validation_alias="group2", default=None)
    sector: Optional[str] = Field(validation_alias="group3", default=None)
    industry_group: Optional[str] = Field(validation_alias="group4", default=None)
    industry: Optional[str] = Field(validation_alias="group5", default=None)
    ticker: Optional[str] = Field(validation_alias="metadata1", default=None)
    webpage: Optional[str] = Field(validation_alias="metadata5", default=None)
    isin_values: Optional[list[str]] = Field(validation_alias="metadata7", default=None)
    cusip_values: Optional[list[str]] = Field(
        validation_alias="metadata8", default=None
    )
    sedol_values: Optional[list[str]] = Field(
        validation_alias="metadata9", default=None
    )
    listing_values: Optional[list[str]] = Field(
        validation_alias="metadata10", default=None
    )

    @property
    def _query_proxy(self):
        return Entity(self.id)


class Etf(QueryComponentMixin):
    """
    Represents an entity in RavenPack's dataset.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    category: Literal["ETFs"] = Field(default="ETFs", validation_alias="category")
    entity_type: Literal["COMP"] = Field(default="COMP", validation_alias="entityType")
    company_type: Optional[str] = Field(validation_alias="group1", default=None)
    country: Optional[str] = Field(validation_alias="group2", default=None)
    sector: Optional[str] = Field(validation_alias="group3", default=None)
    industry_group: Optional[str] = Field(validation_alias="group4", default=None)
    industry: Optional[str] = Field(validation_alias="group5", default=None)
    ticker: Optional[str] = Field(validation_alias="metadata1", default=None)
    webpage: Optional[str] = Field(validation_alias="metadata5", default=None)
    isin_values: Optional[list[str]] = Field(validation_alias="metadata7", default=None)
    cusip_values: Optional[list[str]] = Field(
        validation_alias="metadata8", default=None
    )
    sedol_values: Optional[list[str]] = Field(
        validation_alias="metadata9", default=None
    )
    listing_values: Optional[list[str]] = Field(
        validation_alias="metadata10", default=None
    )

    @property
    def _query_proxy(self):
        return Entity(self.id)


class Product(QueryComponentMixin):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: Literal["PROD"] = Field(default="PROD", validation_alias="entityType")
    product_type: str = Field(validation_alias="group1")
    product_owner: Optional[str] = Field(validation_alias="group2", default=None)

    @property
    def _query_proxy(self):
        return Entity(self.id)


class ProductType(QueryComponentMixin):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: Literal["PRDT"] = Field(default="PRDT", validation_alias="entityType")

    @property
    def _query_proxy(self):
        return Entity(self.id)


class Organization(QueryComponentMixin):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: Literal["ORGA"] = Field(default="ORGA", validation_alias="entityType")
    organization_type: Optional[str] = Field(validation_alias="group1", default=None)
    country: Optional[str] = Field(validation_alias="group2", default=None)

    @property
    def _query_proxy(self):
        return Entity(self.id)


class OrganizationType(QueryComponentMixin):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: Literal["ORGT"] = Field(default="ORGT", validation_alias="entityType")

    @property
    def _query_proxy(self):
        return Entity(self.id)


class Person(QueryComponentMixin):
    """A person"""

    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: Literal["PEOP"] = Field(default="PEOP", validation_alias="entityType")
    # Disabled but enabled for watchlists?
    position: Optional[str] = Field(validation_alias="group1", default=None)
    employer: Optional[str] = Field(validation_alias="group2", default=None)
    nationality: Optional[str] = Field(validation_alias="group3", default=None)
    gender: Optional[str] = Field(validation_alias="group4", default=None)

    @property
    def _query_proxy(self):
        return Entity(self.id)


class Place(QueryComponentMixin):
    """A place. E.g. a country, city, etc."""

    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: Literal["PLCE"] = Field(default="PLCE", validation_alias="entityType")
    place_type: str = Field(validation_alias="group2")
    country: Optional[str] = Field(validation_alias="group4", default=None)
    region: Optional[str] = Field(validation_alias="group5", default=None)

    @property
    def _query_proxy(self):
        return Entity(self.id)


class Facility(QueryComponentMixin):
    """A facility. E.g. a factory, a mine, etc."""

    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: Literal["FCTY"] = Field(default="FCTY", validation_alias="entityType")
    country: Optional[str] = Field(validation_alias="group4", default=None)
    region: Optional[str] = Field(validation_alias="group5", default=None)

    @property
    def _query_proxy(self):
        return Entity(self.id)


class Landmark(QueryComponentMixin):
    """A landmark. E.g. a mountain, a lake, etc."""

    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: Literal["LAND"] = Field(default="LAND", validation_alias="entityType")
    landmark_type: str = Field(validation_alias="group2")
    country: Optional[str] = Field(validation_alias="group4", default=None)
    region: Optional[str] = Field(validation_alias="group5", default=None)

    @property
    def _query_proxy(self):
        return Entity(self.id)


class Concept(QueryComponentMixin):
    """Basically everything else"""

    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="key")
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: str = Field(
        validation_alias="entityType"
    )  # Should belong in EntityType
    entity_type_name: str = Field(validation_alias="group1")
    concept_level_2: Optional[str] = Field(validation_alias="group2", default=None)
    concept_level_3: Optional[str] = Field(validation_alias="group3", default=None)
    concept_level_4: Optional[str] = Field(validation_alias="group4", default=None)
    concept_level_5: Optional[str] = Field(validation_alias="group5", default=None)

    @property
    def _query_proxy(self):
        return Entity(self.id)


class MacroEntity(BaseModel):
    """Model to represent all of the entities with a field 'groups'. For now they are filtered out"""

    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="key")
    name: str
    description: Optional[str] = None
    query_type: str = Field(validation_alias="queryType")
    groups: list

    @property
    def _query_proxy(self):
        return Entity(self.id)
