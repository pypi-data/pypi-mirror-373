from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal


class Customer(BaseModel):
    model_config = ConfigDict(extra="allow")

    document: str = Field()
    name: str = Field()
    mail: str = Field()
    company_id: Optional[str] = Field(default=None)
    set_up_at: Optional[Decimal] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    trade_name: Optional[str] = Field(default=None)
    cluster_id: Optional[str] = Field(default=None)
    situation: Optional[str] = Field(default=None)
