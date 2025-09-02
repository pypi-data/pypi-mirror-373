from functools import cache
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

from bigdata_client.enum_utils import StrEnum
from bigdata_client.models.advanced_search_query import QueryComponent
from bigdata_client.models.advanced_search_query import Source as SourceQuery
from bigdata_client.models.search import Expression


class SourceRetentionPeriod(StrEnum):
    """Retention periods used for filtering Knowledge Graph results"""

    TWO_WEEKS = "2W"
    TWO_YEARS = "2Y"
    FIVE_YEARS = "5Y"
    FULL_HISTORY = "99Y"


class SourceRank(StrEnum):
    """Source ranks used for filtering Knowledge Graph results"""

    RANK_1 = "1"
    """Fully accountable, reputable, and balanced"""
    RANK_2 = "2"
    """Official, reliable, and honest"""
    RANK_3 = "3"
    """Acknowledged, formal, and credible"""
    RANK_4 = "4"
    """Known and reasonable credibility"""
    RANK_5 = "5"
    """Satisfactory credibility"""


class Source(BaseModel):
    """A source of news and information for RavenPack"""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
    id: str
    name: str
    volume: Optional[int] = None
    description: Optional[str] = None
    entity_type: Literal["SRCE"] = Field(default="SRCE")
    publication_type: str
    language: Optional[str] = Field(default=None)
    country: Optional[str] = None
    source_rank: Optional[str] = Field(default=None)
    retention: Optional[SourceRetentionPeriod] = Field(default=None)
    provider_id: str
    url: Optional[str] = None
    favicon: Optional[str] = None

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
            "group1": "publicationType",
            "group2": "language",
            "group3": "country",
            "group4": "sourceRank",
            "group5": "retention",
            "metadata1": "providerId",
            "metadata2": "url",
            "metadata3": "favicon",
        }
        for key in autosuggest_validation_alias_map:
            if key in values:
                values[autosuggest_validation_alias_map[key]] = values.pop(key)
        return values

    def replace_country_by_iso3166(self):
        if self.country is not None:
            self.country = SourceCountry.get_reverse_mapping().get(
                self.country, self.country
            )

    # QueryComponent methods

    @property
    def _query_proxy(self):
        return SourceQuery(self.id)

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


class SourceCountry(StrEnum):
    SS = "South Sudan"
    NE = "Niger"
    BF = "Burkina Faso"
    GD = "Grenada"
    ID = "Indonesia"
    NP = "Nepal"
    BQ = "Bonaire, Saint Eustatius and Saba"
    GI = "Gibraltar"
    KZ = "Kazakhstan"
    MH = "Marshall Islands"
    CV = "Cape Verde"
    HN = "Honduras"
    UY = "Uruguay"
    CN = "China"
    HT = "Haiti"
    PA = "Panama"
    GR = "Greece"
    RS = "Serbia"
    ML = "Mali"
    TZ = "Tanzania"
    GS = "South Georgia and the South Sandwich Islands"
    KN = "Saint Kitts and Nevis"
    AW = "Aruba"
    CF = "Central African Republic"
    AM = "Armenia"
    KR = "South Korea"
    NU = "Niue"
    VC = "Saint Vincent and the Grenadines"
    CD = "Democratic Republic of the Congo"
    TL = "East Timor"
    GM = "Gambia"
    SC = "Seychelles"
    PK = "Pakistan"
    JP = "Japan"
    MP = "Northern Mariana Islands"
    AU = "Australia"
    AQ = "Antarctica"
    GL = "Greenland"
    US = "United States"
    SK = "Slovakia"
    SN = "Senegal"
    MX = "Mexico"
    BG = "Bulgaria"
    PG = "Papua New Guinea"
    MY = "Malaysia"
    PN = "Pitcairn Islands"
    TO = "Tonga"
    SD = "Sudan"
    AR = "Argentina"
    TD = "Chad"
    BV = "Bouvet Island"
    TW = "Taiwan"
    BH = "Bahrain"
    CY = "Cyprus"
    CK = "Cook Islands"
    BN = "Brunei"
    AS = "American Samoa"
    VE = "Venezuela"
    LT = "Lithuania"
    PW = "Palau"
    PR = "Puerto Rico"
    PM = "Saint Pierre and Miquelon"
    HK = "Hong Kong SAR"
    IM = "Isle of Man"
    AL = "Albania"
    KI = "Kiribati"
    RW = "Rwanda"
    MC = "Monaco"
    SG = "Singapore"
    SL = "Sierra Leone"
    GU = "Guam"
    FK = "Falkland Islands"
    MV = "Maldives"
    GH = "Ghana"
    SO = "Somalia"
    GY = "Guyana"
    MQ = "Martinique"
    KY = "Cayman Islands"
    GE = "Georgia"
    CL = "Chile"
    VI = "U.S. Virgin Islands"
    CO = "Colombia"
    BM = "Bermuda"
    JE = "Jersey"
    DO = "Dominican Republic"
    PY = "Paraguay"
    MU = "Mauritius"
    SE = "Sweden"
    CI = "Ivory Coast"
    TH = "Thailand"
    MG = "Madagascar"
    BJ = "Benin"
    UA = "Ukraine"
    EH = "Western Sahara"
    RU = "Russia"
    TM = "Turkmenistan"
    EE = "Estonia"
    KH = "Cambodia"
    BD = "Bangladesh"
    YE = "Yemen"
    MR = "Mauritania"
    CZ = "Czechia"
    TJ = "Tajikistan"
    TN = "Tunisia"
    PH = "Philippines"
    MS = "Montserrat"
    FM = "Micronesia"
    NG = "Nigeria"
    MO = "Macau SAR"
    TV = "Tuvalu"
    BR = "Brazil"
    PF = "French Polynesia"
    ZA = "South Africa"
    MZ = "Mozambique"
    YT = "Mayotte"
    IR = "Iran"
    MK = "North Macedonia"
    LY = "Libya"
    CA = "Canada"
    RO = "Romania"
    NC = "New Caledonia"
    UM = "United States Minor Outlying Islands"
    IE = "Ireland"
    KM = "Comoros"
    HU = "Hungary"
    DE = "Germany"
    AZ = "Azerbaijan"
    IQ = "Iraq"
    LK = "Sri Lanka"
    FJ = "Fiji"
    BZ = "Belize"
    CX = "Christmas Island"
    AG = "Antigua and Barbuda"
    AO = "Angola"
    IO = "British Indian Ocean Territory"
    NF = "Norfolk Island"
    OM = "Oman"
    MT = "Malta"
    ES = "Spain"
    GF = "French Guiana"
    NI = "Nicaragua"
    KW = "Kuwait"
    LS = "Lesotho"
    FR = "France"
    NZ = "New Zealand"
    GW = "Guinea-Bissau"
    FO = "Faroe Islands"
    BL = "Saint Barthélemy"
    ZM = "Zambia"
    ET = "Ethiopia"
    SI = "Slovenia"
    AI = "Anguilla"
    KE = "Kenya"
    HR = "Croatia"
    LA = "Laos"
    VG = "British Virgin Islands"
    SA = "Saudi Arabia"
    AX = "Aland Islands"
    WS = "Samoa"
    AF = "Afghanistan"
    SR = "Suriname"
    PL = "Poland"
    TF = "French Southern Territories"
    CW = "Curaçao"
    BE = "Belgium"
    NO = "Norway"
    VN = "Vietnam"
    VA = "Vatican"
    BB = "Barbados"
    VU = "Vanuatu"
    RE = "Reunion"
    GQ = "Equatorial Guinea"
    DM = "Dominica"
    CH = "Switzerland"
    LR = "Liberia"
    ZW = "Zimbabwe"
    MA = "Morocco"
    FI = "Finland"
    AD = "Andorra"
    TC = "Turks and Caicos Islands"
    IN = "India"
    LU = "Luxembourg"
    CR = "Costa Rica"
    SV = "El Salvador"
    DK = "Denmark"
    CM = "Cameroon"
    BW = "Botswana"
    MW = "Malawi"
    DJ = "Djibouti"
    BO = "Bolivia"
    NA = "Namibia"
    DZ = "Algeria"
    IT = "Italy"
    SY = "Syria"
    BY = "Belarus"
    ER = "Eritrea"
    LB = "Lebanon"
    ME = "Montenegro"
    BS = "Bahamas"
    MF = "Saint Martin"
    NL = "The Netherlands"
    GT = "Guatemala"
    CC = "Cocos Islands"
    PT = "Portugal"
    HM = "Heard Island and McDonald Islands"
    AE = "United Arab Emirates"
    GG = "Guernsey"
    LC = "Saint Lucia"
    LV = "Latvia"
    UZ = "Uzbekistan"
    BI = "Burundi"
    BA = "Bosnia and Herzegovina"
    BT = "Bhutan"
    GA = "Gabon"
    SH = "Saint Helena"
    MD = "Moldova"
    JM = "Jamaica"
    SZ = "Eswatini"
    ST = "Sao Tome and Principe"
    PS = "Palestinian Territory"
    TT = "Trinidad and Tobago"
    JO = "Jordan"
    UG = "Uganda"
    MN = "Mongolia"
    AT = "Austria"
    KP = "North Korea"
    CG = "Republic of the Congo"
    GP = "Guadeloupe"
    QA = "Qatar"
    XK = "Kosovo"
    CU = "Cuba"
    TK = "Tokelau"
    SX = "Sint Maarten"
    KG = "Kyrgyzstan"
    GB = "United Kingdom"
    TG = "Togo"
    EG = "Egypt"
    LI = "Liechtenstein"
    SJ = "Svalbard and Jan Mayen"
    SB = "Solomon Islands"
    IL = "Israel"
    GN = "Guinea"
    WF = "Wallis and Futuna"
    PE = "Peru"
    NR = "Nauru"
    SM = "San Marino"
    MM = "Myanmar"
    TR = "Turkey"
    EC = "Ecuador"
    IS = "Iceland"

    @classmethod
    @cache
    def get_reverse_mapping(self) -> dict[str, str]:
        """Returns a reverse mapping of the enum values to their names."""
        return {member.value: member.name for member in SourceCountry}
