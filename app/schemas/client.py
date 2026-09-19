from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    preferred_language: Optional[str] = None
    accessibility_mode: bool = False
    total_net_worth: Optional[float] = None
    monthly_income: Optional[float] = None


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)