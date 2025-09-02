from typing import Union

from pydantic import BaseModel

from bigdata_client.api.search import DiscoveryPanelResponse
from bigdata_client.models.entities import (
    Company,
    Concept,
    Facility,
    Landmark,
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


class Comentions(BaseModel):
    companies: list[Company]
    concepts: list[Concept]
    languages: list[Language]
    organizations: list[Union[Organization, OrganizationType]]
    places: list[Union[Place, Facility, Landmark]]
    products: list[Union[Product, ProductType]]
    sources: list[Source]
    topics: list[Topic]
    people: list[Person]

    @classmethod
    def from_response(cls, response: DiscoveryPanelResponse):
        return cls(
            companies=response.companies,
            concepts=response.concepts,
            languages=response.languages,
            organizations=response.organizations,
            places=response.places,
            products=response.products,
            sources=response.sources,
            topics=response.topics,
            people=response.people,
        )

    def to_dict(self):
        return {
            "companies": [company.model_dump() for company in self.companies],
            "concepts": [concept.model_dump() for concept in self.concepts],
            "languages": [language.model_dump() for language in self.languages],
            "organizations": [
                organization.model_dump() for organization in self.organizations
            ],
            "places": [place.model_dump() for place in self.places],
            "products": [product.model_dump() for product in self.products],
            "sources": [source.model_dump() for source in self.sources],
            "topics": [topic.model_dump() for topic in self.topics],
            "people": [person.model_dump() for person in self.people],
        }
