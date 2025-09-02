import warnings
from typing import Optional, overload

from typing_extensions import Union, deprecated

from bigdata_client.api.knowledge_graph import (
    AutosuggestedSavedSearch,
    AutosuggestRequests,
    AutosuggestResponse,
    ByIdsRequest,
    EntityTypes,
    KnowledgeGraphTypes,
)
from bigdata_client.connection_protocol import BigdataConnectionProtocol
from bigdata_client.constants import DEPRECATED_WARNING_AUTOSUGGEST
from bigdata_client.enum_utils import StrEnum
from bigdata_client.models.entities import (
    Company,
    CompanyType,
    Concept,
    Etf,
    MacroEntity,
    Organization,
    Person,
    Place,
    Product,
)
from bigdata_client.models.languages import Language
from bigdata_client.models.sources import (
    Source,
    SourceCountry,
    SourceRank,
    SourceRetentionPeriod,
)
from bigdata_client.models.topics import Topic
from bigdata_client.query_type import QueryType


class FilterAnalyticCategory(StrEnum):
    """Categories used for filtering Knowledge Graph results"""

    COMPANIES = "Companies"
    CONCEPTS = "Concepts"
    ORGANIZATIONS = "Organizations"
    PEOPLE = "People"
    PLACES = "Places"
    PRODUCTS = "Products"
    TOPICS = "Topics"
    SOURCES = "Sources"
    ETF = "ETFs"

    def to_expected_model(self):
        # Old async autosuggest doesn't support filtering
        # so it is done by removing every result except the expected model
        return {
            FilterAnalyticCategory.COMPANIES: Company,
            FilterAnalyticCategory.CONCEPTS: Concept,
            FilterAnalyticCategory.ORGANIZATIONS: Organization,
            FilterAnalyticCategory.PEOPLE: Person,
            FilterAnalyticCategory.PLACES: Place,
            FilterAnalyticCategory.PRODUCTS: Product,
            FilterAnalyticCategory.TOPICS: Topic,
            FilterAnalyticCategory.SOURCES: Source,
            FilterAnalyticCategory.ETF: Etf,
        }.get(self)


class KnowledgeGraph:
    """For finding entities, sources and topics"""

    def __init__(self, api_connection: BigdataConnectionProtocol):
        self._api = api_connection

    def _autosuggest(
        self,
        value: Optional[str],
        limit: int,
        categories: Optional[list[FilterAnalyticCategory]] = None,
        group1: Optional[list[str]] = None,
        group2: Optional[list[str]] = None,
        group3: Optional[list[str]] = None,
        group4: Optional[list[str]] = None,
        group5: Optional[list[str]] = None,
    ) -> list[KnowledgeGraphTypes]:
        return self._api.autosuggest(
            value,
            limit=limit,
            categories=categories,
            group1=group1,
            group2=group2,
            group3=group3,
            group4=group4,
            group5=group5,
        )

    def _autosuggest_async(
        self,
        values: list[str],
        limit: int,
    ) -> AutosuggestResponse:
        return self._api.autosuggest_async(
            AutosuggestRequests(root=values), limit=limit
        )

    @overload
    @deprecated(DEPRECATED_WARNING_AUTOSUGGEST)
    def autosuggest(
        self, values: list[str], /, limit: int = 20
    ) -> dict[str, list[KnowledgeGraphTypes]]: ...

    @overload
    def autosuggest(
        self, value: str, /, limit: int = 20
    ) -> list[KnowledgeGraphTypes]: ...

    def autosuggest(
        self, values: Union[list[str], str], limit=20
    ) -> Union[dict[str, list[KnowledgeGraphTypes]], list[KnowledgeGraphTypes]]:
        """
        Searches for entities, sources, topics, searches and watchlists

        -------------------
        Overloaded method
        -------------------
        * Implementation 1

            Args:
                values: Searched item (str)

                limit: Upper limit for each result

            Returns:
                List of results.

        * Implementation 2: DEPRECATED

            Args:
                values: Searched items (list[str])

                limit: Upper limit for each result

            Returns:
                Dict with the searched terms as keys each with a list of results.
        """
        if isinstance(values, list):
            # Decorator not displaying the msg
            warnings.warn(
                DEPRECATED_WARNING_AUTOSUGGEST, DeprecationWarning, stacklevel=2
            )

            api_response = self._autosuggest_async(values, limit)
            # Exclude macros and saved searches from response
            only_supported_entities = self._exclude_models(
                api_response, models=(MacroEntity, AutosuggestedSavedSearch)
            )
            return dict(only_supported_entities.root.items())

        if isinstance(values, str):
            api_response = self._autosuggest(value=values, limit=limit)
            # Exclude macros and saved searches from response
            only_supported_entities = self._exclude_models(
                api_response, models=(MacroEntity, AutosuggestedSavedSearch)
            )
            return only_supported_entities

        raise TypeError(f"Expected list or str for @values, found {type(values)}")

    @overload
    @deprecated(DEPRECATED_WARNING_AUTOSUGGEST)
    def find_concepts(
        self, values: list[str], /, limit=20
    ) -> dict[str, list[Concept]]: ...

    @overload
    def find_concepts(self, values: str, /, limit=20) -> list[Concept]: ...

    def find_concepts(
        self, values: Union[list[str], str], /, limit=20
    ) -> Union[dict[str, list[Concept]], list[Concept]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a concept.

        -------------------
        Overloaded method
        -------------------
        * Implementation 1

            Args:
                values: Searched item (str)

                limit: Upper limit for each result before applying the filter

            Returns:
                List of results.

        * Implementation 2: DEPRECATED

            Args:
                values: Searched items (list[str])

                limit: Upper limit for each result before applying the filter

            Returns:
                Dict with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_category=FilterAnalyticCategory.CONCEPTS, values=values, limit=limit
        )

    def get_companies_by_isin(self, isins: list[str]) -> list[Optional[Company]]:
        """Retrieve a list of companies by their ISIN

        Args:
            isins (list[str]): ISIN list

        Returns:
            list[Optional[Company]]: List of companies in the same order as original @isin list, or None if was not found
        """
        return self._api.get_companies_by_isin(isins)

    def get_companies_by_cusip(self, cusips: list[str]) -> list[Optional[Company]]:
        """Retrieve a list of companies by their CUSIP

        Args:
            cusips (list[str]): CUSIP list

        Returns:
            list[Optional[Company]]: List of companies in the same order as original @cusip list, or None if was not found
        """
        return self._api.get_companies_by_cusip(cusips)

    def get_companies_by_sedol(self, sedols: list[str]) -> list[Optional[Company]]:
        """Retrieve a list of companies by their SEDOL

        Args:
            sedols (list[str]): SEDOL list

        Returns:
            list[Optional[Company]]: List of companies in the same order as original @sedol list, or None if was not found
        """
        return self._api.get_companies_by_sedol(sedols)

    def get_companies_by_listing(self, listings: list[str]) -> list[Optional[Company]]:
        """Retrieve a list of companies by their listing

        Args:
            listings (list[str]): listing list

        Returns:
            list[Optional[Company]]: List of companies in the same order as original @listing list, or None if was not found
        """
        return self._api.get_companies_by_listing(listings)

    def find_etfs(self, value: str, /, limit=20):
        """
        Searches for value in the Knowledge Graph and filters out anything that is not a ETF.

            Args:
                value: Searched item (str)

                limit: Upper limit for each result before applying the filter

            Returns:
                List of results.
        """
        return self._autosuggest_and_filter(
            allowed_category=FilterAnalyticCategory.ETF,
            values=value,
            limit=limit,
        )

    @overload
    @deprecated(DEPRECATED_WARNING_AUTOSUGGEST)
    def find_companies(
        self, values: list[str], /, limit: int = 20
    ) -> dict[str, list[Company]]: ...

    @overload
    def find_companies(
        self,
        values: Optional[str] = None,
        /,
        type: Optional[Union[CompanyType, list[CompanyType]]] = None,
        country: Optional[Union[str, list[str]]] = None,
        limit: int = 20,
    ) -> list[Company]: ...

    def find_companies(
        self,
        values: Optional[Union[list[str], str]] = None,
        /,
        type: Optional[Union[CompanyType, list[CompanyType]]] = None,
        country: Optional[Union[str, list[str]]] = None,
        limit: int = 20,
    ) -> Union[dict[str, list[Company]], list[Company]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a company.

        -------------------
        Overloaded method
        -------------------
        * Implementation 1

            Args:
                values: Searched item (str)
                type: Company type (Public, Private)
                country: Country (US, ES, ...)
                limit: Upper limit for each result before applying the filter

            Returns:
                List of results.

        * Implementation 2: DEPRECATED

            Args:
                values: Searched items (list[str])

                limit: Upper limit for each result before applying the filter

            Returns:
                Dict with the searched terms as keys each with a list of results.
        """
        if values is None and type is None and country is None:
            raise ValueError(
                "At least one of the parameters 'values', 'type' or 'country' must be provided."
            )
        types = [type] if isinstance(type, CompanyType) else type
        countries = [country] if isinstance(country, str) else country

        try:
            if countries:
                countries = [
                    SourceCountry[country.upper()].value for country in countries
                ]
        except KeyError:
            raise ValueError(
                f"Invalid or not supported Country value: '{countries}'. Please use an ISO-3166-1 alpha-2 code."
            )

        response = self._autosuggest_and_filter(
            allowed_category=FilterAnalyticCategory.COMPANIES,
            values=values,
            limit=limit,
            group1=types,
            group2=countries,
        )
        # Reverse mapping country names only if new response format is used
        if isinstance(response, list):
            for company in response:
                company.country = SourceCountry.get_reverse_mapping().get(
                    company.country
                )
        return response

    @overload
    @deprecated(DEPRECATED_WARNING_AUTOSUGGEST)
    def find_people(self, values: list[str], /, limit=20): ...

    @overload
    def find_people(self, values: str, /, limit=20) -> list[Person]: ...

    def find_people(
        self, values: Union[list[str], str], /, limit=20
    ) -> Union[dict[str, list[Person]], list[Person]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a person.

        -------------------
        Overloaded method
        -------------------
        * Implementation 1

            Args:
                values: Searched item (str)

                limit: Upper limit for each result before applying the filter

            Returns:
                List of results.

        * Implementation 2: DEPRECATED

            Args:
                values: Searched items (list[str])

                limit: Upper limit for each result before applying the filter

            Returns:
                Dict with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_category=FilterAnalyticCategory.PEOPLE, values=values, limit=limit
        )

    @overload
    @deprecated(DEPRECATED_WARNING_AUTOSUGGEST)
    def find_places(self, values: list[str], /, limit=20) -> dict[str, list[Place]]: ...

    @overload
    def find_places(self, values: str, /, limit=20) -> list[Place]: ...

    def find_places(
        self, values: Union[list[str], str], /, limit=20
    ) -> Union[dict[str, list[Place]], list[Place]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a place.

        -------------------
        Overloaded method
        -------------------
        * Implementation 1

            Args:
                values: Searched item (str)

                limit: Upper limit for each result before applying the filter

            Returns:
                List of results.

        * Implementation 2: DEPRECATED

            Args:
                values: Searched items (list[str])

                limit: Upper limit for each result before applying the filter

            Returns:
                Dict with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_category=FilterAnalyticCategory.PLACES, values=values, limit=limit
        )

    @overload
    @deprecated(DEPRECATED_WARNING_AUTOSUGGEST)
    def find_organizations(
        self, values: list[str], /, limit=20
    ) -> dict[str, list[Organization]]: ...

    @overload
    def find_organizations(self, values: str, /, limit=20) -> list[Organization]: ...

    def find_organizations(
        self, values: Union[list[str], str], /, limit=20
    ) -> Union[dict[str, list[Organization]], list[Organization]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not an organization.

        -------------------
        Overloaded method
        -------------------
        * Implementation 1

            Args:
                values: Searched item (str)

                limit: Upper limit for each result before applying the filter

            Returns:
                List of results.

        * Implementation 2: DEPRECATED

            Args:
                values: Searched items (list[str])

                limit: Upper limit for each result before applying the filter

            Returns:
                Dict with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_category=FilterAnalyticCategory.ORGANIZATIONS,
            values=values,
            limit=limit,
        )

    @overload
    @deprecated(DEPRECATED_WARNING_AUTOSUGGEST)
    def find_products(
        self, values: list[str], /, limit=20
    ) -> dict[str, list[Product]]: ...

    @overload
    def find_products(self, values: str, /, limit=20) -> list[Product]: ...

    def find_products(
        self, values: Union[list[str], str], /, limit=20
    ) -> Union[dict[str, list[Product]], list[Product]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a product.

        -------------------
        Overloaded method
        -------------------
        * Implementation 1

            Args:
                values: Searched item (str)

                limit: Upper limit for each result before applying the filter

            Returns:
                List of results.

        * Implementation 2: DEPRECATED

            Args:
                values: Searched items (list[str])

                limit: Upper limit for each result before applying the filter

            Returns:
                Dict with the searched terms as keys each with a list of results.
        """
        return self._autosuggest_and_filter(
            allowed_category=FilterAnalyticCategory.PRODUCTS, values=values, limit=limit
        )

    @overload
    @deprecated(DEPRECATED_WARNING_AUTOSUGGEST)
    def find_sources(
        self, values: list[str], /, limit=20
    ) -> dict[str, list[Source]]: ...

    @overload
    def find_sources(
        self,
        values: Optional[str] = None,
        /,
        limit=20,
        country: Optional[Union[list[str], str]] = None,
        rank: Optional[Union[list[SourceRank], SourceRank]] = None,
        retention: Optional[
            Union[list[SourceRetentionPeriod], SourceRetentionPeriod]
        ] = None,
    ) -> list[Source]: ...

    def find_sources(
        self,
        values: Optional[Union[list[str], str]] = None,
        /,
        limit=20,
        country: Optional[Union[list[str], str]] = None,
        rank: Optional[Union[list[SourceRank], SourceRank]] = None,
        retention: Optional[
            Union[list[SourceRetentionPeriod], SourceRetentionPeriod]
        ] = None,
    ) -> Union[dict[str, list[Source]], list[Source]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a source.

        -------------------
        Overloaded method
        -------------------
        * Implementation 1

            Args:
                values: Searched item (str), leave as None to only apply the rest of the filters

                limit: Upper limit for each result before applying the filter

                country: Optional country ISO-3166-1 alpha-2 to filter sources by

                rank: Optional rank to filter sources by

                retention: Optional retention period to filter sources by
            Returns:
                List of results.

        * Implementation 2: DEPRECATED

            Args:
                values: Searched items (list[str])

                limit: Upper limit for each result before applying the filter

            Returns:
                Dict with the searched terms as keys each with a list of results.
        """
        if values is None:
            values = ""
        countries = [country] if isinstance(country, str) else country
        ranks = [rank] if isinstance(rank, SourceRank) else rank
        retentions = (
            [retention] if isinstance(retention, SourceRetentionPeriod) else retention
        )

        if countries:
            try:
                countries = [SourceCountry[country.upper()] for country in countries]
            except KeyError:
                raise ValueError(
                    f"Invalid or not supported Country value: '{country}'. Please use an ISO-3166-1 alpha-2 code."
                )

        results = self._autosuggest_and_filter(
            allowed_category=FilterAnalyticCategory.SOURCES,
            values=values,
            limit=limit,
            group3=countries,
            group4=ranks,
            group5=retentions,
        )

        if isinstance(results, dict):
            # Deprecated implementation
            return results
        elif isinstance(results, list):
            # Reverse mapping country names to ISO-3166-1 alpha-2
            for source in results:
                source.replace_country_by_iso3166()
            return results

    @overload
    @deprecated(DEPRECATED_WARNING_AUTOSUGGEST)
    def find_topics(self, values: list[str], /, limit=20) -> dict[str, list[Topic]]: ...

    @overload
    def find_topics(self, value: str, /, limit=20) -> list[Topic]: ...

    def find_topics(
        self, values: Union[list[str], str], /, limit=20
    ) -> Union[dict[str, list[Topic]], list[Topic]]:
        """
        Searches for values in the Knowledge Graph and filters out anything that is not a topic.

        -------------------
        Overloaded method
        -------------------
        * Implementation 1

            Args:
                values: Searched item (str)

                limit: Upper limit for each result before applying the filter

            Returns:
                List of results.

        * Implementation 2: DEPRECATED

            Args:
                values: Searched items (list[str])

                limit: Upper limit for each result before applying the filter

            Returns:
                Dict with the searched terms as keys each with a list of results.
        """

        return self._autosuggest_and_filter(
            allowed_category=FilterAnalyticCategory.TOPICS, values=values, limit=limit
        )

    def _autosuggest_and_filter(
        self,
        allowed_category: FilterAnalyticCategory,
        values: Optional[Union[list[str], str]],
        limit: int,
        group1: Optional[list[str]] = None,
        group2: Optional[list[str]] = None,
        group3: Optional[str] = None,
        group4: Optional[str] = None,
        group5: Optional[str] = None,
    ) -> Union[dict, list]:
        if isinstance(values, list):
            # Decorator not displaying the msg
            warnings.warn(
                DEPRECATED_WARNING_AUTOSUGGEST, DeprecationWarning, stacklevel=3
            )

            api_response = self._autosuggest_async(values, limit)

            results = self._include_only_models(
                api_response, models=(allowed_category.to_expected_model(),)
            )

            return dict(results.root.items())

        if isinstance(values, str) or values is None:
            return self._autosuggest(
                value=values,
                limit=limit,
                categories=[allowed_category],
                group1=group1,
                group2=group2,
                group3=group3,
                group4=group4,
                group5=group5,
            )

        raise TypeError(f"Expected list or str for @values, found {type(values)}")

    @staticmethod
    def _exclude_models(
        api_response: Union[AutosuggestResponse, list[KnowledgeGraphTypes]],
        models: tuple,
    ) -> Union[AutosuggestResponse, list[KnowledgeGraphTypes]]:
        """It will exclude the models from the response."""
        if isinstance(api_response, AutosuggestResponse):
            filtered_response = {}
            for key, key_results in api_response.root.items():
                filtered_response[key] = list(
                    filter(
                        lambda result: not isinstance(result, models),
                        key_results,
                    )
                )
            return AutosuggestResponse(root=filtered_response)

        if isinstance(api_response, list):
            return list(
                filter(
                    lambda result: not isinstance(result, models),
                    api_response,
                )
            )

        raise TypeError(
            f"Expected AutosuggestResponse or list for @api_response, found {type(api_response)}"
        )

    @staticmethod
    def _include_only_models(
        api_response: Union[AutosuggestResponse, list[KnowledgeGraphTypes]],
        models: tuple,
    ) -> Union[AutosuggestResponse, list[KnowledgeGraphTypes]]:
        """It will include the models specified only"""
        if isinstance(api_response, AutosuggestResponse):
            filtered_response = {}
            for key, key_results in api_response.root.items():
                filtered_response[key] = list(
                    filter(
                        lambda result: isinstance(result, models),
                        key_results,
                    )
                )
            return AutosuggestResponse(root=filtered_response)

        if isinstance(api_response, list):
            return list(
                filter(
                    lambda result: isinstance(result, models),
                    api_response,
                )
            )

        raise TypeError(
            f"Expected AutosuggestResponse or list for @api_response, found {type(api_response)}"
        )

    def get_entities(self, ids: list[str], /) -> list[Optional[EntityTypes]]:
        """Retrieve a list of entities by their ids."""
        return self._get_by_ids(ids, QueryType.ENTITY)

    def get_sources(self, ids: list[str], /) -> list[Optional[Source]]:
        """Retrieve a list of sources by its ids."""
        return self._get_by_ids(ids, QueryType.SOURCE)

    def get_topics(self, ids: list[str], /) -> list[Optional[Topic]]:
        """Retrieve a list of topics by its ids."""
        return self._get_by_ids(ids, QueryType.TOPIC)

    def get_languages(self, ids: list[str], /) -> list[Optional[Language]]:
        """Retrieve a list of languages by its ids."""
        return self._get_by_ids(ids, QueryType.LANGUAGE)

    def _get_by_ids(self, ids: list[str], query_type: QueryType) -> list:
        api_response = self._api.by_ids(
            ByIdsRequest.model_validate(
                [{"key": id_, "queryType": query_type} for id_ in ids]
            )
        )
        return [api_response.root.get(id_) for id_ in ids]
