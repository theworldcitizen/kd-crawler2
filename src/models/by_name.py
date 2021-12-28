from typing import List, Optional

from pydantic import BaseModel


class Individual_details(BaseModel):
    lastname: str
    firstname: str
    title: str
    gender: str
    occupation: Optional[str]
    birth_date: str
    address: str


class Insolvency_case_details(BaseModel):
    fullname: str
    court: str
    type: str
    number: str
    arrangement_date: str
    status: str
    notification_date: Optional[str] = None


class Practitioner_contact(BaseModel):
    fullname: List[str]
    org_name: str
    address: str
    post_code: str
    phone: str


class Service_contact(BaseModel):
    insolvency_service_office: List[str]
    contact: str
    address: str
    post_code: str
    phone: str


class Data(BaseModel):
    platform_id = 'the_insolvency_service'
    personal_info: List[Individual_details]
    case_info: List[Insolvency_case_details]
    practitioner_contact: List[Practitioner_contact]
    service_contact: List[Service_contact]
