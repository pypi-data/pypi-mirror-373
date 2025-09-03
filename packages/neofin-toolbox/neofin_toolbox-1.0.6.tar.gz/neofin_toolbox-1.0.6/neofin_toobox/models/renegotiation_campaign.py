from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from decimal import Decimal


class RenegotiationCampaign(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(...)
    company_id: str = Field(...)
    start_date: Optional[str] = Field(default=None)
    end_date: Optional[str] = Field(default=None)
    initial_day_after_renegotiate: Decimal = Field(...)
    max_number_of_parcel: Decimal = Field(...)
    payment_methods: List[str] = Field(...)
    created_at: Decimal = Field(...)
    has_discount: bool = Field(...)
    created_by: str = Field(...)
    status: str = Field(...)
    customer_ids: List[str] = Field(...)
    available_payment_status: List[str] = Field(...)
    days_after_start: Decimal = Field(...)
    discount: Decimal = Field(...)
    updated_at: Decimal = Field(...)
    min_days_overdue: Optional[Decimal] = Field(default=None)
    updated_by: str = Field(...)
    amount: Decimal = Field(...)
    has_fines_and_fees: bool = Field(...)
    is_active: bool = Field(...)
    min_number_of_installments: Decimal = Field(...)
    title: str = Field(...)
