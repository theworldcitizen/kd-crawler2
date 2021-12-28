
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class Individual_insolvency_register(BaseModel):
    firstname: str
    lastname: str
    birth_date: Optional[datetime]
    org_name: str
    court: str
    number: str
    start_date: datetime
    type: str


class Result_by_organization(BaseModel):
    platform_id = 'the_insolvency_service'
    individual_insolvency_register: List[Individual_insolvency_register]
