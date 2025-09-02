from contextlib import suppress
from typing import Annotated, Literal, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    RootModel,
    Tag,
    ValidationError,
    field_validator,
)

from bigdata_client.models.entities import (
    Company,
    Concept,
    Etf,
    Facility,
    Landmark,
    MacroEntity,
    Organization,
    OrganizationType,
    Person,
    Place,
    Product,
    ProductType,
)
from bigdata_client.models.languages import Language
from bigdata_client.models.sources import Source
from bigdata_client.models.topics import Topic
from bigdata_client.models.watchlists import Watchlist

MACRO_PREFIX = "macro_"
CATEGORY_ETF = "ETFs"


class AutosuggestedSavedSearch(BaseModel):
    """Class used only to parse the output from Autosuggest"""

    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(validation_alias="key", default=None)
    name: Optional[str] = Field(default=None)
    query_type: Literal["savedSearch"] = Field(
        default="savedSearch", validation_alias="queryType"
    )


DiscriminatedEntityTypes = Union[
    Annotated[Etf, Tag(Etf.model_fields["category"].default)],
    Annotated[Company, Tag(Company.model_fields["entity_type"].default)],
    Annotated[Facility, Tag(Facility.model_fields["entity_type"].default)],
    Annotated[Landmark, Tag(Landmark.model_fields["entity_type"].default)],
    Annotated[Organization, Tag(Organization.model_fields["entity_type"].default)],
    Annotated[
        OrganizationType,
        Tag(OrganizationType.model_fields["entity_type"].default),
    ],
    Annotated[Person, Tag(Person.model_fields["entity_type"].default)],
    Annotated[Place, Tag(Place.model_fields["entity_type"].default)],
    Annotated[Product, Tag(Product.model_fields["entity_type"].default)],
    Annotated[ProductType, Tag(ProductType.model_fields["entity_type"].default)],
]

DiscriminatedKnowledgeGraphTypes = Union[
    DiscriminatedEntityTypes,
    Annotated[Source, Tag(Source.model_fields["entity_type"].default)],
    Annotated[Topic, Tag(Topic.model_fields["entity_type"].default)],
    Annotated[Language, Tag(Language.model_fields["query_type"].default)],
    Annotated[
        AutosuggestedSavedSearch,
        Tag(AutosuggestedSavedSearch.model_fields["query_type"].default),
    ],
    Annotated[Watchlist, Tag(Watchlist.model_fields["query_type"].default)],
]

EntityTypes = Union[
    DiscriminatedEntityTypes,
    Concept,
]

KnowledgeGraphTypes = Union[
    MacroEntity,
    DiscriminatedKnowledgeGraphTypes,
    Concept,
]


def get_discriminator_knowledge_graph_value(
    v: Union[dict, DiscriminatedKnowledgeGraphTypes]
) -> Optional[str]:
    # We need to treat ETF differently from the rest of the entities
    # because ETF has `entity_type=COMP` which is same as for `Company`
    # but has `category=ETFs`, so we differentiate ETF from Company by `category`
    if category_is_etf(v):
        return CATEGORY_ETF
    if isinstance(v, dict):
        return v.get(
            "entityType", v.get("entity_type", v.get("queryType", v.get("query_type")))
        )
    return getattr(v, "entity_type", getattr(v, "query_type", None))


def category_is_etf(v: Union[dict, DiscriminatedKnowledgeGraphTypes]) -> bool:
    if isinstance(v, dict):
        return v.get("category") == CATEGORY_ETF
    return getattr(v, "category", None) == CATEGORY_ETF


class KnowledgeGraphAnnotated(RootModel[dict]):
    root: Annotated[
        DiscriminatedKnowledgeGraphTypes,
        Discriminator(get_discriminator_knowledge_graph_value),
    ]


def parse_autosuggest_response(domain_obj: dict) -> KnowledgeGraphTypes:
    with suppress(ValidationError):
        return KnowledgeGraphAnnotated.model_validate(domain_obj).root

    discriminator = get_discriminator_knowledge_graph_value(domain_obj)
    if discriminator and discriminator.startswith(MACRO_PREFIX):
        # Macro keys are not part of KnowledgeGraphAnnotated, and we don't want them there to be visible to the user
        with suppress(ValidationError):
            return MacroEntity.model_validate(domain_obj)

    return Concept.model_validate(domain_obj)


def parse_by_ids_response(
    domain_obj: dict,
) -> Union[DiscriminatedKnowledgeGraphTypes, Concept]:

    with suppress(ValidationError):
        return KnowledgeGraphAnnotated.model_validate(domain_obj).root

    return Concept.model_validate(domain_obj)


class ByIdsResponse(RootModel[dict]):
    root: dict[str, Union[DiscriminatedKnowledgeGraphTypes, Concept]]


class ByIdsRequestItem(BaseModel):
    key: str
    queryType: str


class ByIdsRequest(RootModel[list]):
    root: list[ByIdsRequestItem]


class AutosuggestResponse(RootModel[dict]):
    root: dict[str, list[KnowledgeGraphTypes]]


class AutosuggestRequests(RootModel[list]):
    root: list[str]

    @field_validator("root")
    @classmethod
    def no_duplicates(cls, values):
        if len(values) != len(set(values)):
            raise ValueError("Values must be unique")
        return values
