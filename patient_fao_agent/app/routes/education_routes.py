from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
from patient_fao_agent.app.database import get_db
from patient_fao_agent.app.models.schema_models import (
    PatientVerifyRequest, PatientVerifyResponse,
    ChatQueryRequest, ChatQueryResponse,
    DocumentUploadResponse, ChatHistoryResponse
)
from patient_fao_agent.app.services.patient_service import PatientService
from patient_fao_agent.app.services.education_service import EducationService
from patient_fao_agent.app.services.document_service import DocumentService

router = APIRouter()

@router.post("/verify-patient", response_model=PatientVerifyResponse)
async def verify_patient(
    request: PatientVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify patient by mobile number"""
    patient_service = PatientService(db)
    return await patient_service.verify_patient(request.mobile_number)

@router.post("/chat/query", response_model=ChatQueryResponse)
async def chat_query(
    request: ChatQueryRequest,
    db: Session = Depends(get_db)
):
    """Handle direct patient queries"""
    education_service = EducationService(db)
    return await education_service.handle_query(
        patient_id=request.patient_id,
        query=request.query,
        session_id=request.session_id
    )

@router.post("/chat/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
    patient_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process patient medical document"""
    document_service = DocumentService(db)
    return await document_service.process_document(patient_id, file)

@router.get("/chat/history/{patient_id}", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    patient_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get patient chat history"""
    education_service = EducationService(db)
    return await education_service.get_chat_history(patient_id, limit)

@router.delete("/chat/history/{chat_id}")
async def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db)
):
    """Delete a specific chat entry"""
    education_service = EducationService(db)
    return await education_service.delete_chat(chat_id)