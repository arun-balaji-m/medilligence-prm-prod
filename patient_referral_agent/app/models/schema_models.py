from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class PatientCreate(BaseModel):
    patient_name: str
    dob: date
    gender: str
    mobile_number: str
    email: Optional[str] = None

    @field_validator('dob', mode='before')
    @classmethod
    def parse_dob(cls, v):
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            # Try multiple date formats
            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f'Invalid date format: {v}')
        return v


class PatientResponse(BaseModel):
    id: int
    patient_mrn: Optional[str]
    patient_name: str
    dob: date
    gender: str
    mobile_number: str
    email: Optional[str]


class TimelineEvent(BaseModel):
    date: str
    title: str
    summary: str
    details: str
    category: str


class ReferralDocument(BaseModel):
    timeline: List[TimelineEvent]
    summary: str


class ChatMessage(BaseModel):
    message: str
    patient_id: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    requires_input: bool
    input_type: Optional[str] = None
    patient_id: Optional[int] = None
    timeline: Optional[List[Dict[str, Any]]] = None