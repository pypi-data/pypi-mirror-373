from typing import Literal, Optional

from pydantic import ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

from bigdata_client.models.advanced_search_query import Topic as TopicQuery
from bigdata_client.models.entities import QueryComponentMixin


class Topic(QueryComponentMixin):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
    id: str
    name: str
    volume: Optional[int] = None
    description: Optional[str] = Field(validation_alias="description", default=None)
    # Disabled, but enabled for watchlists?
    topic: Optional[str]
    topic_group: Optional[str]
    entity_type: Literal["TOPC"] = Field(default="TOPC")

    # Disabled fields.
    # topic_type: str = Field(validation_alias="group3")
    # topic_subtype: str = Field(validation_alias="group4")
    # topic_role: str = Field(validation_alias="group5")

    @model_validator(mode="before")
    @classmethod
    def apply_second_alias_generator(cls, values):
        """
        Applied before validating to replace some alias in the input @values so
        we can make the model in 3 ways: snake_case/camel_case/alias. This is required because not
        all endpoints are resolving the groupN into the correct field name.
        """
        values = values.copy()  # keep original input unmutated for Unions
        autosuggest_validation_alias_map = {
            "key": "id",
            "group1": "topic",
            "group2": "topicGroup",
        }
        for key in autosuggest_validation_alias_map:
            if key in values:
                values[autosuggest_validation_alias_map[key]] = values.pop(key)
        return values

    @property
    def _query_proxy(self):
        return TopicQuery(self.id)
