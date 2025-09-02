from typing import Optional

from pydantic import BaseModel


class QuotaConsumption(BaseModel):
    # 'None' means that no quota is defined
    total: Optional[int]
    used: int
    remaining: Optional[int]


class OrganizationQuota(BaseModel):
    query_unit: QuotaConsumption
    file_upload_pages: Optional[QuotaConsumption] = None
    pdf_upload_pages: Optional[QuotaConsumption] = None


class SubscriptionDetails(BaseModel):
    organization_quota: OrganizationQuota
