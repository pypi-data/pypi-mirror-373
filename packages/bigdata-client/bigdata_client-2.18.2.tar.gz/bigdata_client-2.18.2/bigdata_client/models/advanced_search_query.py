from abc import ABC, ABCMeta, abstractmethod
from typing import Optional, Protocol, Union, runtime_checkable

from bigdata_client.enum_utils import StrEnum
from bigdata_client.models.search import (
    Expression,
    ExpressionOperation,
    ExpressionTypes,
    FiscalQuarterValidator,
    FiscalYearValidator,
    SentimentRangeValidator,
)

DOUBLE_QUOTES_HTML_LITERAL = "&quot"


# Decorated with runtime_checkable to allow isinstance checks
@runtime_checkable
class QueryComponent(Protocol):
    """
    Protocol for any query component.
    Any class that implements this protocol should be able to be converted to
    an Expression object, and should be able to operate with other QueryComponents
    """

    def to_expression(self) -> Expression: ...

    def make_copy(self) -> "QueryComponent": ...

    def __and__(self, other: "QueryComponent") -> "QueryComponent": ...

    def __or__(self, other: "QueryComponent") -> "QueryComponent": ...

    def __invert__(self) -> "QueryComponent": ...

    def to_dict(self) -> dict: ...


class BaseQueryComponent(ABC):
    """
    An abstract component that implements the common basic logic of the query
    components, like the AND, OR, and NOT operators.
    """

    def __and__(self, other: QueryComponent) -> QueryComponent:
        """
        Joins two query components with an AND operator.

        Note: The return type is QueryComponent instead of And because cases like
        Entity("1") & Entity("2") should return
        Entity("1", "2", operation=ExpressionOperation.ALL)
        instead of
        And(Entity("1"), Entity("2"))
        """
        return And(self, other)

    def __or__(self, other: QueryComponent) -> QueryComponent:
        """
        Joins two query components with an OR operator.

        Note: The return type is QueryComponent instead of Or because cases like
        Entity in [1,2] | Entity in [3,4]` should return
        Entity in [1,2,3,4] instead of Or(Entity in [1,2], Entity in [3,4])
        """
        return Or(self, other)

    def __invert__(self) -> QueryComponent:
        """
        Negates the query component

        Note: The return type is QueryComponent instead of Not because cases like
        Not(Not(Entity("1"))) should return Entity("1")
        instead of Not(Not(Entity("1")))
        """
        return Not(self)

    def to_dict(self) -> dict:
        """Convert the query component to a dictionary"""
        return self.to_expression().model_dump(
            exclude_none=True, exclude_unset=True, mode="json"
        )

    @abstractmethod
    def to_expression(self) -> Expression:
        """Convert the query component to an Expression object"""

    @abstractmethod
    def make_copy(self) -> QueryComponent:
        """Make a deep copy of the query component"""


# -- Operators --


class And(BaseQueryComponent):
    def __init__(self, *args: QueryComponent):
        # Flatten by detecting Ands inside args
        flatten_args = []
        for arg in args:
            if isinstance(arg, And):
                flatten_args.extend(arg.items)
            else:
                flatten_args.append(arg)
        self.items = flatten_args

    def __and__(self, other: QueryComponent) -> QueryComponent:
        # Flatten A&(B&(C&D)) into &(A,B,C,D)
        if isinstance(other, And):
            items = [*self.items, *other.items]
        else:
            items = [*self.items, other]
        # We first want to group the items by their class to make use of the
        # all operation
        items_by_class = {}
        for item in items:
            items_by_class.setdefault(item.__class__, []).append(item)
        # Now we can merge the items that are of the same class
        items_sorted = []
        for item_list in items_by_class.values():
            for item in item_list:
                items_sorted.append(item)
        # If there were in order, don't do this again, just AND them
        if items_sorted == items:
            return And(*items_sorted)
        # Otherwise, try to start from scratch, with the sorted items
        return All(items_sorted)

    def to_expression(self) -> Expression:
        return Expression(
            type=ExpressionTypes.AND,
            value=[item.to_expression() for item in self.items],
        )

    def __repr__(self):
        items = [repr(item) for item in self.items]
        return f"And({', '.join(items)})"

    def make_copy(self) -> QueryComponent:
        """Make a deep copy of the query component"""
        items = [item.make_copy() for item in self.items]
        return And(*items)


class Or(BaseQueryComponent):
    def __init__(self, *args: QueryComponent):
        # Flatten by detecting Ors inside args
        flatten_args = []
        for arg in args:
            if isinstance(arg, Or):
                flatten_args.extend(arg.items)
            else:
                flatten_args.append(arg)
        self.items = flatten_args

    def __or__(self, other: QueryComponent) -> QueryComponent:
        # Flatten A|(B|(C|D)) into |(A,B,C,D)
        if isinstance(other, Or):
            items = [*self.items, *other.items]
        else:
            items = [*self.items, other]
        # We first want to group the items by their class to make use of the in operation
        items_by_class = {}
        for item in items:
            items_by_class.setdefault(item.__class__, []).append(item)
        # Now we can merge the items that are of the same class
        items_sorted = []
        for item_list in items_by_class.values():
            for item in item_list:
                items_sorted.append(item)
        # If there were in order, don't do this again, just OR them
        if items_sorted == items:
            return Or(*items_sorted)
        # Otherwise, try to start from scratch, with the sorted items
        return Any(items_sorted)

    def to_expression(self) -> Expression:
        return Expression(
            type=ExpressionTypes.OR,
            value=[item.to_expression() for item in self.items],
        )

    def __repr__(self):
        items = [repr(item) for item in self.items]
        return f"Or({', '.join(items)})"

    def make_copy(self) -> QueryComponent:
        """Make a deep copy of the query component"""
        items = [item.make_copy() for item in self.items]
        return Or(*items)


class Not(BaseQueryComponent):
    def __init__(self, item: QueryComponent):
        self.item = item

    def to_expression(self) -> Expression:
        return Expression(type=ExpressionTypes.NOT, value=self.item.to_expression())

    def __invert__(self) -> QueryComponent:
        return self.item

    def __repr__(self):
        return f"Not({repr(self.item)})"

    def make_copy(self) -> QueryComponent:
        """Make a deep copy of the query component"""
        return Not(self.item.make_copy())


# Any and All are used by the user and we want them to be in capital
def Any(items: list[QueryComponent]) -> QueryComponent:
    if not items:
        raise ValueError("At least one item is required in any_")
    component = items[0]
    for item in items[1:]:
        component = component | item
    return component


# Any and All are used by the user and we want them to be in capital
def All(items: list[QueryComponent]) -> QueryComponent:
    if not items:
        raise ValueError("At least one item is required in all_")
    component = items[0]
    for item in items[1:]:
        component = component & item
    return component


# -- Filters --


class ListQueryComponent(BaseQueryComponent, ABC):
    """
    An abstract component that implements most of the duplicated logic of
    Entity, Keyword, Topic, Language, Source, etc
    All of these classes hold a list of items and have an operator (IN or ALL),
    so __and__ and __or__ with other objects of the same type can return a single
    object with the items joined.
    """

    def __init__(
        self, *items: str, operation: ExpressionOperation = ExpressionOperation.IN
    ):
        self.items = items
        self.operation = operation

    @abstractmethod
    def get_expression_type(self) -> ExpressionTypes:
        """Should return the type, like _entity_ or _rp_topic_"""

    def to_expression(self) -> Expression:
        return Expression(
            type=self.get_expression_type(),
            operation=self.operation,
            value=list(self.items),
        )

    def __or__(self, other: QueryComponent) -> QueryComponent:
        """
        Or operator for Entity, Keyword, Topic, Language, Source, etc.

        Examples:

        Joining an entity with something else should return an OR
        >>> Entity("1") | Topic("t1")
        Or(Entity('1'), Topic('t1'))

        But joining multiple entities should use the "in" operator and return
        a single entity:
        >>> Entity("1") | Entity("2") | Entity("3")
        Entity('1', '2', '3')

        Even if the entities are not contiguous:
        >>> Entity("1") | Topic("t1") | Entity("2")
        Or(Entity('1', '2'), Topic('t1'))

        But not if the operations are different
        >>> Entity("1") | (Entity("2") & Entity("3"))
        Or(Entity('1'), Entity('2', '3', operation=ExpressionOperation.ALL))
        >>> (Entity("1") & Entity("2")) | Entity("3")
        Or(Entity('1', '2', operation=ExpressionOperation.ALL), Entity('3'))
        """
        cls = self.__class__
        default = Or(self, other)
        operation = ExpressionOperation.IN
        if not isinstance(other, cls):
            return default
        if len(other.items) > 1 and other.operation != operation:
            return default
        if len(self.items) > 1 and self.operation != operation:
            return default
        return cls(*self.items, *other.items, operation=operation)

    def __and__(self, other: QueryComponent) -> QueryComponent:
        """
        And operator for Entity, Keyword, Topic, Language, Source, etc.

        Examples:

        Joining an entity with something else should return an AND
        >>> Entity("1") & Topic("t1")
        And(Entity('1'), Topic('t1'))

        But joining multiple entities should use the "all" operator and return
        a single entity:
        >>> Entity("1") & Entity("2") & Entity("3")
        Entity('1', '2', '3', operation=ExpressionOperation.ALL)

        Even if the entities are not contiguous:
        >>> Entity("1") & Topic("t1") & Entity("2")
        And(Entity('1', '2', operation=ExpressionOperation.ALL), Topic('t1'))

        But not if the operations are different
        >>> Entity("1") & (Entity("2") | Entity("3"))
        And(Entity('1'), Entity('2', '3'))
        >>> (Entity("1") | Entity("2")) & Entity("3")
        And(Entity('1', '2'), Entity('3'))
        """
        cls = self.__class__
        default = And(self, other)
        operation = ExpressionOperation.ALL
        if not isinstance(other, cls):
            return default
        if len(other.items) > 1 and other.operation != operation:
            return default
        if len(self.items) > 1 and self.operation != operation:
            return default
        return cls(*self.items, *other.items, operation=operation)

    def __repr__(self):
        items = [repr(item) for item in self.items]
        operation = ""
        if self.operation == ExpressionOperation.ALL:
            operation = ", operation=ExpressionOperation.ALL"
        class_name = self.__class__.__name__
        return f"{class_name}({', '.join(items)}{operation})"

    def make_copy(self) -> QueryComponent:
        """Make a deep copy of the query component"""
        cls = self.__class__
        return cls(*self.items, operation=self.operation)


class Entity(ListQueryComponent):
    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.ENTITY


class Topic(ListQueryComponent):
    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.TOPIC


class Keyword(ListQueryComponent):
    def __init__(
        self, *items: str, operation: ExpressionOperation = ExpressionOperation.IN
    ):
        super().__init__(*items, operation=operation)

    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.KEYWORD

    def to_expression(self) -> Expression:
        items = [self._quote(item) for item in self.items]
        return Expression(
            type=self.get_expression_type(),
            operation=self.operation,
            value=list(items),
        )

    def _quote(self, item: str) -> str:
        if item[0] == '"' and item[-1] == '"':
            return (
                f"{DOUBLE_QUOTES_HTML_LITERAL}{item[1:-1]}{DOUBLE_QUOTES_HTML_LITERAL}"
            )
        if item.startswith(DOUBLE_QUOTES_HTML_LITERAL) and item.endswith(
            DOUBLE_QUOTES_HTML_LITERAL
        ):
            return item
        return f"{DOUBLE_QUOTES_HTML_LITERAL}{item}{DOUBLE_QUOTES_HTML_LITERAL}"


class Document(ListQueryComponent):
    def __init__(
        self, *items: str, operation: ExpressionOperation = ExpressionOperation.IN
    ):
        super().__init__(*items, operation=operation)

    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.DOCUMENT


class SentimentRange(BaseQueryComponent):

    def __init__(self, interval: tuple[float, float]):
        self.interval = SentimentRangeValidator(
            range_start=interval[0], range_end=interval[1]
        )

    def to_expression(self) -> Expression:
        return Expression(
            type=ExpressionTypes.SENTIMENT_RANGE,
            operation=ExpressionOperation.IN,
            value=[self.interval.range_start, self.interval.range_end],
        )

    def make_copy(self) -> QueryComponent:
        return SentimentRange(
            interval=(self.interval.range_start, self.interval.range_end)
        )


class Similarity(ListQueryComponent):
    def __init__(
        self, *items: str, operation: ExpressionOperation = ExpressionOperation.ALL
    ):
        if operation == ExpressionOperation.IN:
            raise ValueError("Similarity does not support `|` (OR) operator")
        super().__init__(*items, operation=operation)

    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.SIMILARITY

    def __repr__(self):
        items = [repr(item) for item in self.items]
        operation = ""
        # This can't happen, the operation is always ALL, so no need to show it
        # if self.operation == ExpressionOperation.IN:
        #     operation = ", operation=ExpressionOperation.IN"
        class_name = self.__class__.__name__
        return f"{class_name}({', '.join(items)}{operation})"


class Language(ListQueryComponent):
    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.LANGUAGE

    # Predefined languages

    @classmethod
    @property
    def arabic(cls):
        return Language("AR")

    @classmethod
    @property
    def chinese_traditional(cls):
        return Language("ZHTW")

    @classmethod
    @property
    def chinese_simplified(cls):
        return Language("ZHCN")

    @classmethod
    @property
    def dutch(cls):
        return Language("NL")

    @classmethod
    @property
    def english(cls):
        return Language("EN")

    @classmethod
    @property
    def french(cls):
        return Language("FR")

    @classmethod
    @property
    def german(cls):
        return Language("DE")

    @classmethod
    @property
    def italian(cls):
        return Language("IT")

    @classmethod
    @property
    def japanese(cls):
        return Language("JA")

    @classmethod
    @property
    def korean(cls):
        return Language("KO")

    @classmethod
    @property
    def portuguese(cls):
        return Language("PT")

    @classmethod
    @property
    def russian(cls):
        return Language("RU")

    @classmethod
    @property
    def spanish(cls):
        return Language("ES")


class Source(ListQueryComponent):
    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.SOURCE


class MetaBaseQueryComponentAndStrEnum(type(BaseQueryComponent), type(StrEnum)):
    """Metaclass magic"""


class DocumentVersion(
    BaseQueryComponent, StrEnum, metaclass=MetaBaseQueryComponentAndStrEnum
):

    RAW = "RAW"
    """Document version raw"""

    CORRECTED = "CORRECTED"
    """Document version corrected"""

    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.DOCUMENT_VERSION

    def to_expression(self) -> Expression:
        return Expression(
            type=ExpressionTypes.DOCUMENT_VERSION,
            operation=ExpressionOperation.IN,
            value=[self.value],
        )

    def __repr__(self):
        return f"DocumentVersion({self.value})"

    def make_copy(self) -> QueryComponent:
        """Make a deep copy of the query component"""
        return DocumentVersion(self.value)


class SectionMetadata(
    BaseQueryComponent, StrEnum, metaclass=MetaBaseQueryComponentAndStrEnum
):
    MANAGEMENT_DISCUSSION = "Management Discussion Section"
    """Management Discussion Section"""
    QA = "qa"
    """QA"""
    QUESTION = "question"
    """question"""
    ANSWER = "answer"
    """answer"""

    def to_expression(self) -> Expression:
        return Expression(
            type=ExpressionTypes.SECTION_METADATA,
            operation=ExpressionOperation.IN,
            value=[self.value],
        )

    def __repr__(self):
        return f"SectionMetadata({self.value})"

    def make_copy(self) -> QueryComponent:
        """Make a deep copy of the query component"""
        return SectionMetadata(self.value)


class TranscriptTypes(
    BaseQueryComponent, StrEnum, metaclass=MetaBaseQueryComponentAndStrEnum
):
    ANALYST_INVESTOR_SHAREHOLDER_MEETING = "Analyst, Investor and Shareholder meeting"
    """Analyst, Investor and Shareholder meeting"""
    CONFERENCE_CALL = "General Conference Call"
    """General Conference Call"""
    GENERAL_PRESENTATION = "General Presentation"
    """General Presentation"""
    EARNINGS_CALL = "Earnings Call"
    """Earnings Call"""
    EARNINGS_RELEASE = "Earnings Release"
    """Earnings Release"""
    GUIDANCE_CALL = "Guidance Call"
    """Guidance Call"""
    SALES_REVENUE_CALL = "Sales and Revenue Call"
    """Sales and Revenue Call"""
    SALES_REVENUE_RELEASE = "Sales and Revenue Release"
    """Sales and Revenue Release"""
    SPECIAL_SITUATION_MA = "Special Situation, M&A and Other"
    """Special Situation, M&A and Other"""
    SHAREHOLDERS_MEETING = "Shareholders Meeting"
    """Shareholders Meeting"""
    MANAGEMENT_PLAN_ANNOUNCEMENT = "Management Plan Announcement"
    """Management Plan Announcement"""
    INVESTOR_CONFERENCE_CALL = "Investor Conference Call"
    """Investor Conference Call"""

    def to_expression(self) -> Expression:
        return Expression(
            type=ExpressionTypes.RP_DOCUMENT_SUBTYPE,
            operation=ExpressionOperation.IN,
            value=[self.value],
        )

    def __repr__(self):
        return f"TranscriptTypes('{self.value}')"

    def make_copy(self) -> QueryComponent:
        """Make a deep copy of the query component"""
        return TranscriptTypes(self.value)


class FilingTypes(
    BaseQueryComponent, StrEnum, metaclass=MetaBaseQueryComponentAndStrEnum
):
    SEC_10_K = "RNS-SEC-10-K"
    """Annual report filing regarding a company's financial performance"""
    SEC_10_Q = "RNS-SEC-10-Q"
    """Quarterly report filing regarding a company's financial performance"""
    SEC_8_K = "RNS-SEC-8-K"
    """Report filed whenever a significant corporate event takes place that triggers a disclosure"""
    SEC_20_F = "RNS-SEC-20-F"
    """Annual report filing for non-U.S. and non-Canadian companies that have securities trading in the U.S."""
    SEC_S_1 = "RNS-SEC-S-1"
    """Filing needed to register the securities of companies that wish to go public with the U.S."""
    SEC_S_3 = "RNS-SEC-S-3"
    """Filing utilized when a company wishes to raise capital"""
    SEC_6_K = "RNS-SEC-6-K"
    """Report of foreign private issuer pursuant to rules 13a-16 and 15d-16"""

    def to_expression(self) -> Expression:
        return Expression(
            type=ExpressionTypes.RP_DOCUMENT_SUBTYPE,
            operation=ExpressionOperation.IN,
            value=[self.value],
        )

    def __repr__(self):
        return f"FilingTypes('{self.value}')"

    def make_copy(self) -> QueryComponent:
        """Make a deep copy of the query component"""
        return FilingTypes(self.value)


class ReportingEntity(ListQueryComponent):
    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.REPORTING_ENTITIES


class FiscalYear(ListQueryComponent):
    def __init__(
        self, *items: int, operation: ExpressionOperation = ExpressionOperation.IN
    ):
        # Validate the items but keep them stored raw, this is so FiscalYear can operate with itself
        [FiscalYearValidator(value=i) for i in items]
        super().__init__(*items, operation=operation)

    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.REPORTING_PERIOD

    def to_expression(self) -> Expression:
        return Expression(
            type=self.get_expression_type(),
            operation=self.operation,
            value=[FiscalYearValidator(value=i).get_string() for i in self.items],
        )

    def __or__(self, other: QueryComponent) -> QueryComponent:
        """
        Implementation similar to ListQueryComponent but returning
        a ReportingPeriodAndWrapper when combining FiscalYear | FiscalQuarter
        """
        cls = self.__class__
        default = Or(self, other)
        operation = ExpressionOperation.IN
        if not isinstance(other, (cls, FiscalQuarter, ReportingPeriodWrapper)):
            return default
        if len(other.items) > 1 and other.operation != operation:
            return default
        if len(self.items) > 1 and self.operation != operation:
            return default
        if isinstance(other, FiscalQuarter):
            return ReportingPeriodWrapper(
                FiscalYearQuarterAggregate(fiscal_year=self, fiscal_quarter=other),
                operation=operation,
            )
        if isinstance(other, ReportingPeriodWrapper):
            return (
                ReportingPeriodWrapper(
                    FiscalYearQuarterAggregate(fiscal_year=self), operation=operation
                )
                | other
            )
        return cls(*self.items, *other.items, operation=operation)

    def __and__(self, other: QueryComponent) -> QueryComponent:
        """
        Implementation similar to ListQueryComponent but returning
        a ReportingPeriodAndWrapper when combining FiscalYear & FiscalQuarter
        """
        cls = self.__class__
        default = And(self, other)
        operation = ExpressionOperation.ALL
        if not isinstance(other, (cls, FiscalQuarter, ReportingPeriodWrapper)):
            return default
        if len(other.items) > 1 and other.operation != operation:
            return default
        if len(self.items) > 1 and self.operation != operation:
            return default
        if isinstance(other, FiscalQuarter):
            return ReportingPeriodWrapper(
                FiscalYearQuarterAggregate(fiscal_year=self, fiscal_quarter=other),
                operation=operation,
            )
        if isinstance(other, ReportingPeriodWrapper):
            return (
                ReportingPeriodWrapper(
                    FiscalYearQuarterAggregate(fiscal_year=self), operation=operation
                )
                & other
            )
        return cls(*self.items, *other.items, operation=operation)


class FiscalQuarter(ListQueryComponent):
    def __init__(
        self, *items: int, operation: ExpressionOperation = ExpressionOperation.IN
    ):
        # Validate the items but keep them stored raw, this is so FiscalQuarter can operate with itself
        [FiscalQuarterValidator(value=i).get_string() for i in items]
        super().__init__(*items, operation=operation)

    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.REPORTING_PERIOD

    def to_expression(self) -> Expression:
        return Expression(
            type=self.get_expression_type(),
            operation=self.operation,
            value=[FiscalQuarterValidator(value=i).get_string() for i in self.items],
        )

    def __or__(self, other: QueryComponent) -> QueryComponent:
        """
        Implementation similar to ListQueryComponent but returning
        a ReportingPeriodAndWrapper when combining FiscalYear | FiscalQuarter
        """
        cls = self.__class__
        default = Or(self, other)
        operation = ExpressionOperation.IN
        if not isinstance(other, (cls, FiscalYear, ReportingPeriodWrapper)):
            return default
        if len(other.items) > 1 and other.operation != operation:
            return default
        if len(self.items) > 1 and self.operation != operation:
            return default
        if isinstance(other, FiscalYear):
            return ReportingPeriodWrapper(
                FiscalYearQuarterAggregate(fiscal_quarter=self, fiscal_year=other),
                operation=operation,
            )
        if isinstance(other, ReportingPeriodWrapper):
            return (
                ReportingPeriodWrapper(
                    FiscalYearQuarterAggregate(fiscal_quarter=self), operation=operation
                )
                | other
            )
        return cls(*self.items, *other.items, operation=operation)

    def __and__(self, other: QueryComponent) -> QueryComponent:
        """
        Implementation similar to ListQueryComponent but returning
        a ReportingPeriodAndWrapper when combining FiscalYear & FiscalQuarter
        """
        cls = self.__class__
        default = And(self, other)
        operation = ExpressionOperation.ALL
        if not isinstance(other, (cls, FiscalYear, ReportingPeriodWrapper)):
            return default
        if len(other.items) > 1 and other.operation != operation:
            return default
        if len(self.items) > 1 and self.operation != operation:
            return default
        if isinstance(other, FiscalYear):
            return ReportingPeriodWrapper(
                FiscalYearQuarterAggregate(fiscal_quarter=self, fiscal_year=other),
                operation=operation,
            )
        if isinstance(other, ReportingPeriodWrapper):
            return (
                ReportingPeriodWrapper(
                    FiscalYearQuarterAggregate(fiscal_quarter=self), operation=operation
                )
                & other
            )

        return cls(*self.items, *other.items, operation=operation)


class FiscalYearQuarterAggregate:
    def __init__(
        self,
        fiscal_year: Optional[FiscalYear] = None,
        fiscal_quarter: Optional[FiscalQuarter] = None,
    ):
        self.fiscal_year = fiscal_year
        self.fiscal_quarter = fiscal_quarter

    @staticmethod
    def from_values(values: list[str]) -> "FiscalYearQuarterAggregate":
        fiscal_years = []
        fiscal_quarters = []
        for value in values:
            if value.endswith("FY"):
                fiscal_years.append(int(value[:-2]))
            elif value.startswith("FQ"):
                fiscal_quarters.append(int(value[2:]))
            else:
                raise ValueError(
                    f"Could not process {values} into FiscalYear and FiscalQuarter"
                )
        return FiscalYearQuarterAggregate(
            fiscal_year=FiscalYear(*fiscal_years),
            fiscal_quarter=FiscalQuarter(*fiscal_quarters),
        )

    def make_copy(self):
        return FiscalYearQuarterAggregate(
            fiscal_year=self.fiscal_year, fiscal_quarter=self.fiscal_quarter
        )


class ReportingPeriodWrapper(ListQueryComponent):
    """
    This is an class that will be used when the user combines FiscalYear and FiscalQuarter so that when the expression
    is generated elements from FiscalYear and FiscalQuarter are combined into the same values array.
    E.g:
    >>> (FiscalYear(2099) & FiscalQuarter(2) & FiscalQuarter(3)).to_dict()
    {'type': 'reporting_period', 'value': ['FQ2', 'FQ3', '2099FY'], 'operation': 'all'}

    """

    def __init__(
        self,
        *items: FiscalYearQuarterAggregate,
        operation: ExpressionOperation = ExpressionOperation.IN,
    ):
        super().__init__(*items, operation=operation)

    def to_expression(self) -> Expression:
        fiscal_quarters, fiscal_years = self._get_items_as_string()
        return Expression(
            type=self.get_expression_type(),
            operation=self.operation,
            value=fiscal_quarters + fiscal_years,
        )

    def make_copy(self) -> QueryComponent:
        return ReportingPeriodWrapper(
            *[item.make_copy() for item in self.items],
            operation=self.operation,
        )

    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.REPORTING_PERIOD

    def _get_items_as_string(self) -> tuple[list[str], list[str]]:
        fiscal_years = []
        fiscal_quarters = []
        for aggregate in self.items:
            if aggregate.fiscal_year is not None:
                fiscal_years.extend(
                    FiscalYearValidator(value=year).get_string()
                    for year in aggregate.fiscal_year.items
                )
            if aggregate.fiscal_quarter is not None:
                fiscal_quarters.extend(
                    FiscalQuarterValidator(value=quarter).get_string()
                    for quarter in aggregate.fiscal_quarter.items
                )
        return fiscal_quarters, fiscal_years

    def __repr__(self):
        fiscal_quarters, fiscal_years = self._get_items_as_string()
        operator = " & " if self.operation == ExpressionOperation.ALL else " | "
        return f"FiscalYear({fiscal_years}) {operator} FiscalQuarter({fiscal_quarters})"

    def __or__(self, other: QueryComponent) -> QueryComponent:
        """
        Implementation similar to ListQueryComponent but returning
        a ReportingPeriodAndWrapper when combining FiscalYear | FiscalQuarter
        """
        cls = self.__class__
        default = Or(self, other)
        operation = ExpressionOperation.IN
        if not isinstance(other, (cls, FiscalYear, FiscalQuarter)):
            return default
        if len(other.items) > 1 and other.operation != operation:
            return default
        if len(self.items) > 1 and self.operation != operation:
            return default
        if isinstance(other, FiscalYear):
            return self | ReportingPeriodWrapper(
                FiscalYearQuarterAggregate(fiscal_year=other), operation=operation
            )
        if isinstance(other, FiscalQuarter):
            return self | ReportingPeriodWrapper(
                FiscalYearQuarterAggregate(fiscal_quarter=other), operation=operation
            )
        return cls(*self.items, *other.items, operation=operation)

    def __and__(self, other: QueryComponent) -> QueryComponent:
        """
        Implementation similar to ListQueryComponent but returning
        a ReportingPeriodAndWrapper when combining FiscalYear & FiscalQuarter
        """
        cls = self.__class__
        default = And(self, other)
        operation = ExpressionOperation.ALL
        if not isinstance(other, (cls, FiscalYear, FiscalQuarter)):
            return default
        if len(other.items) > 1 and other.operation != operation:
            return default
        if len(self.items) > 1 and self.operation != operation:
            return default
        if isinstance(other, FiscalYear):
            return self & ReportingPeriodWrapper(
                FiscalYearQuarterAggregate(fiscal_year=other), operation=operation
            )
        if isinstance(other, FiscalQuarter):
            return self & ReportingPeriodWrapper(
                FiscalYearQuarterAggregate(fiscal_quarter=other), operation=operation
            )

        return cls(*self.items, *other.items, operation=operation)


class AbsoluteDateRangeQuery(BaseQueryComponent):
    def __init__(self, start: str, end: str):
        self.start = start
        self.end = end

    def to_expression(self) -> Expression:
        return Expression(
            type=ExpressionTypes.DATE,
            value=[self.start, self.end],
        )

    def make_copy(self) -> QueryComponent:
        """Make a deep copy of the query component"""
        return AbsoluteDateRangeQuery(start=self.start, end=self.end)


class RollingDateRangeQuery(BaseQueryComponent):
    """Used by the real RollingDateRange. Do not use this class directly"""

    def __init__(self, value: str):
        self.value = value

    def to_expression(self) -> Expression:
        return Expression(
            type=ExpressionTypes.DATE,
            value=self.value,
        )

    def make_copy(self) -> QueryComponent:
        """Make a deep copy of the query component"""
        return RollingDateRangeQuery(value=self.value)


class ContentType(ListQueryComponent):
    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.CONTENT_TYPE

    @classmethod
    @property
    def pdf(cls):
        return ContentType("pdf")

    @classmethod
    @property
    def docx(cls):
        return ContentType("docx")

    @classmethod
    @property
    def pptx(cls):
        return ContentType("pptx")

    @classmethod
    @property
    def html(cls):
        return ContentType("html")

    @classmethod
    @property
    def txt(cls):
        return ContentType("txt")

    @classmethod
    @property
    def xlsx(cls):
        return ContentType("xlsx")

    @classmethod
    @property
    def csv(cls):
        return ContentType("csv")

    @classmethod
    @property
    def json(cls):
        return ContentType("json")

    @classmethod
    @property
    def xml(cls):
        return ContentType("xml")

    @classmethod
    @property
    def rtf(cls):
        return ContentType("rtf")

    @classmethod
    @property
    def md(cls):
        return ContentType("md")


class SentimentMetaclass(ABCMeta, type):
    """Only needed for blackmagic"""

    def __hash__(self):
        # Just blackmagic to make isinstance work
        return hash(self.__module__ + self.__name__)

    def __gt__(cls, value: Union[float, int]):
        return cls(value, operation=ExpressionOperation.GREATER_THAN)

    def __lt__(cls, value: Union[float, int]):
        return cls(value, operation=ExpressionOperation.LOWER_THAN)

    def __ge__(cls, value: Union[float, int]):
        _ = value
        raise ValueError("Sentiment only supports > and <, not >=")

    def __le__(cls, value: Union[float, int]):
        _ = value
        raise ValueError("Sentiment only supports > and <, not <=")

    def __eq__(cls, value: Union[float, int]):
        _ = value
        if isinstance(value, (float, int)):
            raise ValueError("Sentiment only supports > and <, not ==")
        else:
            # equal operator can be called by isinstance
            return super(cls).__eq__(value)

    def __ne__(cls, value: float):
        _ = value
        if isinstance(value, (float, int)):
            raise ValueError("Sentiment only supports > and <, not !=")
        else:
            # equal operator can be called by isinstance
            return super(cls).__eq__(value)


class FileTag(ListQueryComponent):
    def get_expression_type(self) -> ExpressionTypes:
        return ExpressionTypes.TAGS


def _expression_to_query_component(expression: Expression) -> QueryComponent:
    """
    Convert an Expression object to a QueryComponent object
    """
    if expression.type == ExpressionTypes.AND:
        return And(*[_expression_to_query_component(e) for e in expression.value])
    if expression.type == ExpressionTypes.OR:
        return Or(*[_expression_to_query_component(e) for e in expression.value])
    if expression.type == ExpressionTypes.NOT:
        return Not(_expression_to_query_component(expression.value))
    if expression.type == ExpressionTypes.ENTITY:
        return Entity(*expression.value, operation=expression.operation)
    if expression.type == ExpressionTypes.TOPIC:
        return Topic(*expression.value, operation=expression.operation)
    if expression.type == ExpressionTypes.KEYWORD:
        return Keyword(*expression.value, operation=expression.operation)
    if expression.type == ExpressionTypes.SIMILARITY:
        return Similarity(*expression.value, operation=expression.operation)
    if expression.type == ExpressionTypes.LANGUAGE:
        return Language(*expression.value, operation=expression.operation)
    if expression.type == ExpressionTypes.SOURCE:
        return Source(*expression.value, operation=expression.operation)
    if expression.type == ExpressionTypes.DATE:
        if isinstance(expression.value, list):
            return AbsoluteDateRangeQuery(*expression.value)
        return RollingDateRangeQuery(expression.value)
    if expression.type == ExpressionTypes.CONTENT_TYPE:
        return ContentType(*expression.value, operation=expression.operation)
    if expression.type == ExpressionTypes.REPORTING_PERIOD:
        return ReportingPeriodWrapper(
            FiscalYearQuarterAggregate.from_values(expression.value),
            operation=expression.operation,
        )
    if expression.type == ExpressionTypes.SECTION_METADATA:
        return SectionMetadata(expression.value[0])
    if expression.type == ExpressionTypes.RP_DOCUMENT_SUBTYPE:
        return _parse_document_type(expression.value[0])
    if expression.type == ExpressionTypes.REPORTING_ENTITIES:
        return ReportingEntity(*expression.value, operation=expression.operation)
    if expression.type == ExpressionTypes.DOCUMENT:
        return Document(*expression.value, operation=expression.operation)
    if expression.type == ExpressionTypes.SENTIMENT_RANGE:
        return SentimentRange(interval=(expression.value[0], expression.value[1]))
    if expression.type == ExpressionTypes.TAGS:
        return FileTag(*expression.value, operation=expression.operation)
    if expression.type == ExpressionTypes.DOCUMENT_VERSION:
        return DocumentVersion(expression.value[0])


def _parse_document_type(expression_type):
    if expression_type in list(map(str, TranscriptTypes)):
        return TranscriptTypes(expression_type)

    if expression_type in list(map(str, FilingTypes)):
        return FilingTypes(expression_type)

    raise ValueError(f"Unknown document type: {expression_type}")
