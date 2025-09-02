from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseApiResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class OrganizationQuotaResponse(BaseApiResponse):
    # 'None' means that no quota was defined
    contextual_units_max_read: Optional[int] = None


class OrganizationConsumedResponse(BaseApiResponse):
    contextual_units_read: int = 0


class MyBigdataQuotaResponse(BaseApiResponse):
    """Quota of logged-in user"""

    organization_quota: OrganizationQuotaResponse
    organization_consumed: OrganizationConsumedResponse


class UploadQuotaSubscriptionResponse(BaseModel):
    # 'None' means that no quota was defined
    max_pages_allowed: Optional[int] = None
    pages_used: int
    pages_remaining: Optional[int] = None
    max_units_allowed: Optional[int] = None
    units_used: int
    units_remaining: Optional[int] = None


class UploadQuotaResponse(BaseApiResponse):
    subscription: UploadQuotaSubscriptionResponse


class MyUploadQuotaResponse(BaseApiResponse):
    """Upload quota of logged-in user"""

    quota: UploadQuotaResponse
