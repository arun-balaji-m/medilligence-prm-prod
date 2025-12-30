from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date


class PatientVerifyRequest(BaseModel):
    mobile_number: str = Field(..., description="Patient mobile number")


class PatientVerifyResponse(BaseModel):
    verified: bool
    patient_id: Optional[int] = None
    patient_name: Optional[str] = None
    message: str


class ChatQueryRequest(BaseModel):
    patient_id: int
    query: str = Field(..., max_length=1000)
    session_id: Optional[str] = None


class ChatQueryResponse(BaseModel):
    response: str
    chat_id: int
    session_id: str


class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    chat_id: Optional[int] = None
    explanation: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    id: int
    document_number: Optional[str]
    document: Optional[Dict[str, Any]]
    patient_id: int
    created_at: datetime


class PatientResponse(BaseModel):
    id: int
    patient_name: Optional[str]
    mobile_number: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True