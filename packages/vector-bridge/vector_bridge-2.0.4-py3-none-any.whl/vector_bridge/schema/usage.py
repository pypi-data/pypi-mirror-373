from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RequestDailyUsage(BaseModel):
    requests_number: int
    errors_number: int
    seconds_number: float


class RequestUsage(BaseModel):
    pk: str  # api key hash or organization_id or integration_id
    date: str
    usage_type: str
    request_usage: Dict[int, RequestDailyUsage] = Field(default_factory=dict)

    @property
    def total_requests(self):
        _sum = 0
        for usage in self.request_usage.values():
            _sum += usage.requests_number
            _sum += usage.errors_number
        return _sum


class PaginatedRequestUsages(BaseModel):
    request_usages: List[RequestUsage]
    limit: int
    last_evaluated_date: Optional[str]
    has_more: bool
