from enum import Enum


class QueryType(str, Enum):
    # SAVED_SEARCH = "savedSearch"
    # WATCHLIST = "watchlist"
    ENTITY = "entity"
    TOPIC = "rp_topic"
    SOURCE = "source"
    LANGUAGE = "language"
    # KEYWORD = "keyword"  # TODO: check
