# Instead of `while True:`, for security reasons, we always limit the loops to something reasonably high.
from bigdata_client.enum_utils import StrEnum

MAX_SEARCH_PAGES = 1_000
SEARCH_PAGE_DEFAULT_SIZE = 300
PAGE_SIZE_BE_LIMIT = 1_000  # The Backend limit for the page size
MAX_RETRIES_RATE_LIMITER = (
    1_000  # Same as MAX_SEARCH_PAGES, but applied to the rate limiter
)
MAX_REQUESTS_PER_MINUTE = 300  # The maximum number of requests per minute
TIME_BEFORE_RETRY_RATE_LIMITER = 1  # Time in seconds before retrying the request
REFRESH_FREQUENCY_RATE_LIMIT = 10  # Time in seconds to pro-rate the rate limiter
DEPRECATED_WARNING_AUTOSUGGEST = "Accepting a list[str] of values is deprecated. Pass a single str as the value instead."


MIN_CHAT_QUESTION_LENGTH = 1
MAX_CHAT_QUESTION_LENGTH = 5000


# ERROR CODES
class BackendErrorCodes(StrEnum):
    QUERY_TOO_MANY_TOKENS = "QUERY-TOO_MANY_TOKENS"


THREAD_WAIT_TIMEOUT = 100
