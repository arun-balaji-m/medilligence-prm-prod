from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date


class ChatMessage(BaseModel):
    role: str
    content: str


class AssessmentRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = Field(default_factory=list)
    session_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AssessmentResponse(BaseModel):
    response: str
    session_data: Dict[str, Any]
    is_complete: bool
    assessment_id: Optional[int] = None


class VoiceAssessmentRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    conversation_history: Optional[List[ChatMessage]] = Field(default_factory=list)
    session_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


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


class AppointmentResponse(BaseModel):
    id: int
    appointment_number: Optional[str]
    appointment_date: Optional[datetime]
    patient_id: Optional[int]

    class Config:
        from_attributes = True


class PreAssessmentResponse(BaseModel):
    id: int
    document: Optional[Dict[str, Any]]
    patient_id: Optional[int]
    appointment_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentDocument(BaseModel):
    """Structure for the assessment JSON document"""
    chief_complaint: Optional[Dict[str, str]] = Field(default_factory=dict)
    history_present_illness: Optional[Dict[str, str]] = Field(default_factory=dict)
    past_medical_history: Optional[Dict[str, str]] = Field(default_factory=dict)
    procedure_history: Optional[Dict[str, str]] = Field(default_factory=dict)
    current_medication: Optional[Dict[str, str]] = Field(default_factory=dict)
    allergy: Optional[Dict[str, str]] = Field(default_factory=dict)
    comorbidities: Optional[Dict[str, str]] = Field(default_factory=dict)
    family_history: Optional[Dict[str, str]] = Field(default_factory=dict)
    social_history: Optional[Dict[str, str]] = Field(default_factory=dict)