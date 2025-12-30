from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class PatientResponse(BaseModel):
    id: int
    patient_mrn: Optional[str]
    patient_name: Optional[str]
    dob: Optional[date]
    gender: Optional[str]
    mobile_number: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True

class DoctorResponse(BaseModel):
    id: int
    doctor_login: Optional[str]
    doctor_name: Optional[str]
    specialization: Optional[str]

    class Config:
        from_attributes = True

class SlotResponse(BaseModel):
    id: int
    doctor_id: int
    doctor_name: Optional[str]
    start_time: datetime
    end_time: datetime
    status: str

    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    patient_id: int
    slot_id: int
    appointment_date: datetime

class AppointmentResponse(BaseModel):
    id: int
    appointment_number: Optional[str]
    appointment_date: Optional[datetime]
    slot_id: Optional[int]
    patient_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None