from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class EndUserUsageSummary:
    end_user_id: Optional[str]
    total_requests: int
    total_cost: float
    total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int
    current_month_requests: int
    current_month_cost: float
    current_month_tokens: int


@dataclass
class EndUserPlanInfo:
    id: int
    name: str
    monthly_token_limit: Optional[int]
    monthly_cost_limit: Optional[float]
    rate_limit_per_minute: Optional[int]
    rate_limit_per_hour: Optional[int]
    rate_limit_per_day: Optional[int]
    description: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str


@dataclass
class CreateEndUserPlanRequest:
    name: str
    monthly_token_limit: Optional[int] = None
    monthly_cost_limit: Optional[float] = None
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    rate_limit_per_day: Optional[int] = None
    description: Optional[str] = None


@dataclass
class UpdateEndUserPlanRequest:
    monthly_token_limit: Optional[int] = None
    monthly_cost_limit: Optional[float] = None
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    rate_limit_per_day: Optional[int] = None
    description: Optional[str] = None


@dataclass
class CreateEndUserPlanResponse:
    plan_id: int


@dataclass
class EndUserPlansListResponse:
    plans: List[EndUserPlanInfo]
