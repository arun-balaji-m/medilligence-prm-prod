# from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
# from sqlalchemy.orm import Session
# from patient_referral_agent.app.database import get_db
# from patient_referral_agent.app.services.referral_service import ReferralService
# from patient_referral_agent.app.services.patient_service import PatientService
# from patient_referral_agent.app.models.schema_models import ChatMessage, ChatResponse, PatientResponse
# from patient_referral_agent.app.config import UPLOAD_DIR, MAX_FILE_SIZE
# import os
# import uuid
# import shutil
#
# router = APIRouter(prefix="/api/referral", tags=["Referral"])
#
# # In-memory service instances (use Redis in production)
# referral_services = {}
#
#
# def get_referral_service(session_id: str, db: Session) -> ReferralService:
#     if session_id not in referral_services:
#         referral_services[session_id] = ReferralService(db)
#     return referral_services[session_id]
#
#
# @router.post("/chat", response_model=ChatResponse)
# async def chat(
#         message: ChatMessage,
#         session_id: str = Form(...),
#         db: Session = Depends(get_db)
# ):
#     service = get_referral_service(session_id, db)
#     return service.handle_message(session_id, message.message, message.patient_id)
#
#
# @router.post("/upload", response_model=ChatResponse)
# async def upload_document(
#         file: UploadFile = File(...),
#         patient_id: int = Form(...),
#         session_id: str = Form(...),
#         db: Session = Depends(get_db)
# ):
#     # Validate file
#     if not file.filename.endswith('.pdf'):
#         raise HTTPException(400, "Only PDF files are allowed")
#
#     # Check file size
#     file.file.seek(0, 2)
#     file_size = file.file.tell()
#     if file_size > MAX_FILE_SIZE:
#         raise HTTPException(400, f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB")
#     file.file.seek(0)
#
#     # Save file
#     file_id = str(uuid.uuid4())
#     file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
#
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#
#     try:
#         service = get_referral_service(session_id, db)
#         result = service.process_document(file_path, patient_id)
#         return result
#     finally:
#         # Clean up
#         if os.path.exists(file_path):
#             os.remove(file_path)
#
#
# @router.get("/patient/{patient_id}", response_model=PatientResponse)
# async def get_patient(patient_id: int, db: Session = Depends(get_db)):
#     patient = PatientService.get_patient(db, patient_id)
#     if not patient:
#         raise HTTPException(404, "Patient not found")
#     return patient
#
#
# @router.get("/timeline/{patient_id}")
# async def get_timeline(patient_id: int, db: Session = Depends(get_db)):
#     referral = PatientService.get_referral(db, patient_id)
#     if not referral:
#         raise HTTPException(404, "No referral data found")
#     return referral.refferral_document
#
#
# @router.delete("/session/{session_id}")
# async def clear_session(session_id: str):
#     if session_id in referral_services:
#         del referral_services[session_id]
#     return {"message": "Session cleared"}


##second version
#
# from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
# from sqlalchemy.orm import Session
# from patient_referral_agent.app.database import get_db
# from patient_referral_agent.app.services.referral_service import ReferralService
# from patient_referral_agent.app.services.patient_service import PatientService
# from patient_referral_agent.app.models.schema_models import ChatMessage, ChatResponse, PatientResponse
# from patient_referral_agent.app.config import UPLOAD_DIR, MAX_FILE_SIZE
# import os
# import uuid
# import shutil
#
# router = APIRouter(prefix="/api/referral", tags=["Referral"])
#
# # In-memory service instances (use Redis in production)
# referral_services = {}
#
#
# def get_referral_service(session_id: str, db: Session) -> ReferralService:
#     if session_id not in referral_services:
#         referral_services[session_id] = ReferralService(db)
#     return referral_services[session_id]
#
#
# @router.get("/test")
# async def test_endpoint():
#     return {"status": "ok", "message": "Referral API is working"}
#
#
# @router.post("/chat", response_model=ChatResponse)
# async def chat(
#         message: str = Form(...),
#         session_id: str = Form(...),
#         patient_id: int = Form(None),
#         db: Session = Depends(get_db)
# ):
#     print(f"Received chat request - Message: {message}, Session: {session_id}, Patient: {patient_id}")
#     try:
#         service = get_referral_service(session_id, db)
#         result = service.handle_message(session_id, message, patient_id)
#         print(f"Returning response: {result}")
#         return result
#     except Exception as e:
#         print(f"Error in chat endpoint: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(500, f"Internal server error: {str(e)}")
#
#
# @router.post("/upload", response_model=ChatResponse)
# async def upload_document(
#         file: UploadFile = File(...),
#         patient_id: int = Form(...),
#         session_id: str = Form(...),
#         db: Session = Depends(get_db)
# ):
#     # Validate file
#     if not file.filename.endswith('.pdf'):
#         raise HTTPException(400, "Only PDF files are allowed")
#
#     # Check file size
#     file.file.seek(0, 2)
#     file_size = file.file.tell()
#     if file_size > MAX_FILE_SIZE:
#         raise HTTPException(400, f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB")
#     file.file.seek(0)
#
#     # Save file
#     file_id = str(uuid.uuid4())
#     file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
#
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#
#     try:
#         service = get_referral_service(session_id, db)
#         result = service.process_document(file_path, patient_id)
#         return result
#     finally:
#         # Clean up
#         if os.path.exists(file_path):
#             os.remove(file_path)
#
#
# @router.get("/patient/{patient_id}", response_model=PatientResponse)
# async def get_patient(patient_id: int, db: Session = Depends(get_db)):
#     patient = PatientService.get_patient(db, patient_id)
#     if not patient:
#         raise HTTPException(404, "Patient not found")
#     return patient
#
#
# @router.get("/timeline/{patient_id}")
# async def get_timeline(patient_id: int, db: Session = Depends(get_db)):
#     referral = PatientService.get_referral(db, patient_id)
#     if not referral:
#         raise HTTPException(404, "No referral data found")
#     return referral.refferral_document
#
#
# @router.delete("/session/{session_id}")
# async def clear_session(session_id: str):
#     if session_id in referral_services:
#         del referral_services[session_id]
#     return {"message": "Session cleared"}


##third version


from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from patient_referral_agent.app.database import get_db
from patient_referral_agent.app.services.referral_service import ReferralService
from patient_referral_agent.app.services.patient_service import PatientService
from patient_referral_agent.app.models.schema_models import ChatMessage, ChatResponse, PatientResponse
from patient_referral_agent.app.config import UPLOAD_DIR, MAX_FILE_SIZE
import os
import uuid
import shutil

router = APIRouter(prefix="/api/referral", tags=["Referral"])

# In-memory service instances (use Redis in production)
referral_services = {}


def get_referral_service(session_id: str, db: Session) -> ReferralService:
    if session_id not in referral_services:
        referral_services[session_id] = ReferralService(db)
    return referral_services[session_id]


@router.get("/test")
async def test_endpoint():
    return {"status": "ok", "message": "Referral API is working"}


@router.post("/chat", response_model=ChatResponse)
async def chat(
        message: str = Form(...),
        session_id: str = Form(...),
        patient_id: int = Form(None),
        db: Session = Depends(get_db)
):
    print(f"Received chat request - Message: {message}, Session: {session_id}, Patient: {patient_id}")
    try:
        service = get_referral_service(session_id, db)
        result = service.handle_message(session_id, message, patient_id)
        print(f"Returning response: {result}")
        return result
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Internal server error: {str(e)}")


@router.post("/upload", response_model=ChatResponse)
async def upload_document(
        file: UploadFile = File(...),
        patient_id: int = Form(...),
        session_id: str = Form(...),
        db: Session = Depends(get_db)
):
    file_path = None
    try:
        # Validate file
        if not file.filename.endswith('.pdf'):
            raise HTTPException(400, "Only PDF files are allowed")

        # Check file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(400, f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB")
        file.file.seek(0)

        # Save file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"File uploaded: {file_path} ({file_size} bytes)")

        service = get_referral_service(session_id, db)
        result = service.process_document(file_path, patient_id)
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in upload_document: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Error processing document: {str(e)}")
    finally:
        # Clean up
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up file: {file_path}")
            except Exception as e:
                print(f"Error cleaning up file: {e}")


@router.get("/patient/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = PatientService.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    return patient


@router.get("/timeline/{patient_id}")
async def get_timeline(patient_id: int, db: Session = Depends(get_db)):
    referral = PatientService.get_referral(db, patient_id)
    if not referral:
        raise HTTPException(404, "No referral data found")
    return referral.refferral_document


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in referral_services:
        del referral_services[session_id]
    return {"message": "Session cleared"}