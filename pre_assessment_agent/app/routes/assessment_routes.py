# """
# API routes for pre-assessment agent
# """
#
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import Dict, Any
# import re
#
# from pre_assessment_agent.app.database import get_db
# from pre_assessment_agent.app.models.schema_models import (
#     AssessmentRequest,
#     AssessmentResponse,
#     ChatMessage
# )
# from pre_assessment_agent.app.services.ai_service import AIService
# from pre_assessment_agent.app.services.patient_service import PatientService
# from pre_assessment_agent.app.services.assessment_service import AssessmentService
#
# router = APIRouter(prefix="/api/assessment", tags=["Assessment"])
#
# # Initialize AI service
# ai_service = AIService()
#
#
# def is_valid_mobile_number(text: str) -> bool:
#     """Check if text contains a valid mobile number"""
#     # Indian mobile number pattern (10 digits, optionally starting with +91 or 91)
#     pattern = r'(\+91|91)?[6-9]\d{9}'
#     return bool(re.search(pattern, text))
#
#
# def extract_mobile_number(text: str) -> str:
#     """Extract mobile number from text"""
#     # Remove all non-digit characters except +
#     cleaned = re.sub(r'[^\d+]', '', text)
#
#     # Remove country code if present
#     if cleaned.startswith('+91'):
#         cleaned = cleaned[3:]
#     elif cleaned.startswith('91') and len(cleaned) == 12:
#         cleaned = cleaned[2:]
#
#     return cleaned
#
#
# @router.post("/chat", response_model=AssessmentResponse)
# async def chat_assessment(
#         request: AssessmentRequest,
#         db: Session = Depends(get_db)
# ):
#     """
#     Main endpoint for chat-based pre-assessment
#
#     Args:
#         request: Assessment request with message and conversation history
#         db: Database session
#
#     Returns:
#         AI response and updated session data
#     """
#     try:
#         session_data = request.session_data or {}
#         conversation_history = request.conversation_history or []
#         user_message = request.message
#
#         # Add user message to conversation history
#         conversation_history.append({
#             "role": "user",
#             "content": user_message
#         })
#
#         # STAGE 1: Mobile number verification
#         if not session_data.get("patient_verified"):
#             # Check if user provided mobile number
#             if is_valid_mobile_number(user_message):
#                 mobile_number = extract_mobile_number(user_message)
#
#                 # Verify patient in database
#                 patient, appointment = PatientService.verify_patient_and_get_details(
#                     db, mobile_number
#                 )
#
#                 if patient:
#                     # Patient found - update session
#                     session_data["patient_verified"] = True
#                     session_data["patient_id"] = patient.id
#                     session_data["patient_name"] = patient.patient_name
#                     session_data["mobile_number"] = mobile_number
#
#                     if appointment:
#                         session_data["appointment_id"] = appointment.id
#                         session_data["appointment_number"] = appointment.appointment_number
#                         session_data["appointment_date"] = appointment.appointment_date.strftime(
#                             "%B %d, %Y at %I:%M %p") if appointment.appointment_date else None
#
#                     session_data["current_stage"] = "greeting"
#
#                 else:
#                     # Patient not found
#                     response_text = "I'm sorry, I couldn't find a patient registered with that mobile number. Could you please verify the number and try again?"
#                     conversation_history.append({
#                         "role": "assistant",
#                         "content": response_text
#                     })
#
#                     return AssessmentResponse(
#                         response=response_text,
#                         session_data=session_data,
#                         is_complete=False
#                     )
#
#         # Generate AI response
#         messages = [{"role": msg["role"], "content": msg["content"]}
#                     for msg in
#                     conversation_history[:-1]]  # Exclude the last user message as it will be added by AI service
#
#         ai_response = await ai_service.generate_response(messages, session_data)
#
#         # Add AI response to conversation history
#         conversation_history.append({
#             "role": "assistant",
#             "content": ai_response
#         })
#
#         # Update session stage based on conversation
#         session_data = ai_service.update_session_stage(
#             session_data, user_message, ai_response
#         )
#
#         # Update conversation history in session
#         session_data["conversation_history"] = conversation_history
#
#         # Check if assessment is complete
#         is_complete = session_data.get("assessment_complete", False)
#         assessment_id = None
#
#         # If complete, extract and save assessment data
#         if is_complete and not session_data.get("assessment_saved"):
#             # Extract structured data from conversation
#             assessment_data = await ai_service.extract_assessment_data(
#                 conversation_history
#             )
#
#             # Save to database
#             assessment = AssessmentService.create_assessment(
#                 db=db,
#                 patient_id=session_data["patient_id"],
#                 appointment_id=session_data.get("appointment_id"),
#                 document=assessment_data
#             )
#
#             assessment_id = assessment.id
#             session_data["assessment_saved"] = True
#             session_data["assessment_id"] = assessment_id
#
#         return AssessmentResponse(
#             response=ai_response,
#             session_data=session_data,
#             is_complete=is_complete,
#             assessment_id=assessment_id
#         )
#
#     except Exception as e:
#         print(f"Error in chat_assessment: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {str(e)}"
#         )
#
#
# @router.get("/assessment/{assessment_id}")
# async def get_assessment(
#         assessment_id: int,
#         db: Session = Depends(get_db)
# ):
#     """
#     Get assessment by ID
#
#     Args:
#         assessment_id: Assessment ID
#         db: Database session
#
#     Returns:
#         Assessment data
#     """
#     assessment = AssessmentService.get_assessment_by_id(db, assessment_id)
#
#     if not assessment:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Assessment not found"
#         )
#
#     return {
#         "id": assessment.id,
#         "patient_id": assessment.patient_id,
#         "appointment_id": assessment.appointment_id,
#         "document": assessment.document,
#         "created_at": assessment.created_at
#     }
#
#
# @router.get("/patient/{patient_id}/assessments")
# async def get_patient_assessments(
#         patient_id: int,
#         db: Session = Depends(get_db)
# ):
#     """
#     Get all assessments for a patient
#
#     Args:
#         patient_id: Patient ID
#         db: Database session
#
#     Returns:
#         List of assessments
#     """
#     assessments = AssessmentService.get_assessments_by_patient(db, patient_id)
#
#     return {
#         "patient_id": patient_id,
#         "assessments": [
#             {
#                 "id": a.id,
#                 "appointment_id": a.appointment_id,
#                 "document": a.document,
#                 "created_at": a.created_at
#             }
#             for a in assessments
#         ]
#     }
#
#
# @router.post("/reset-session")
# async def reset_session():
#     """
#     Reset session data (for testing or starting new conversation)
#
#     Returns:
#         Empty session data
#     """
#     return {
#         "session_data": {},
#         "message": "Session reset successfully"
#     }


#commenting the assessment routes in 15-11-2025
# """
# API routes for pre-assessment agent
# """
#
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import Dict, Any
# import re
#
# from pre_assessment_agent.app.database import get_db
# from pre_assessment_agent.app.models.schema_models import (
#     AssessmentRequest,
#     AssessmentResponse,
#     ChatMessage
# )
# from pre_assessment_agent.app.services.ai_service import AIService
# from pre_assessment_agent.app.services.patient_service import PatientService
# from pre_assessment_agent.app.services.assessment_service import AssessmentService
#
# router = APIRouter(prefix="/api/assessment", tags=["Assessment"])
#
# # Initialize AI service
# ai_service = AIService()
#
#
# def is_valid_mobile_number(text: str) -> bool:
#     """Check if text contains a valid mobile number"""
#     # Indian mobile number pattern (10 digits, optionally starting with +91 or 91)
#     pattern = r'(\+91|91)?[6-9]\d{9}'
#     return bool(re.search(pattern, text))
#
#
# def extract_mobile_number(text: str) -> str:
#     """Extract mobile number from text"""
#     # Remove all non-digit characters except +
#     cleaned = re.sub(r'[^\d+]', '', text)
#
#     # Remove country code if present
#     if cleaned.startswith('+91'):
#         cleaned = cleaned[3:]
#     elif cleaned.startswith('91') and len(cleaned) == 12:
#         cleaned = cleaned[2:]
#
#     return cleaned
#
#
# @router.post("/chat", response_model=AssessmentResponse)
# async def chat_assessment(
#         request: AssessmentRequest,
#         db: Session = Depends(get_db)
# ):
#     """
#     Main endpoint for chat-based pre-assessment
#
#     Args:
#         request: Assessment request with message and conversation history
#         db: Database session
#
#     Returns:
#         AI response and updated session data
#     """
#     try:
#         session_data = request.session_data or {}
#         conversation_history = request.conversation_history or []
#         user_message = request.message
#
#         # Add user message to conversation history
#         conversation_history.append({
#             "role": "user",
#             "content": user_message
#         })
#
#         # STAGE 1: Mobile number verification
#         if not session_data.get("patient_verified"):
#             # Check if user provided mobile number
#             if is_valid_mobile_number(user_message):
#                 mobile_number = extract_mobile_number(user_message)
#
#                 # Verify patient in database
#                 patient, appointment = PatientService.verify_patient_and_get_details(
#                     db, mobile_number
#                 )
#
#                 if patient:
#                     # Patient found - update session
#                     session_data["patient_verified"] = True
#                     session_data["patient_id"] = patient.id
#                     session_data["patient_name"] = patient.patient_name
#                     session_data["mobile_number"] = mobile_number
#
#                     if appointment:
#                         session_data["appointment_id"] = appointment.id
#                         session_data["appointment_number"] = appointment.appointment_number
#                         session_data["appointment_date"] = appointment.appointment_date.strftime(
#                             "%B %d, %Y at %I:%M %p") if appointment.appointment_date else None
#
#                     session_data["current_stage"] = "greeting"
#
#                 else:
#                     # Patient not found
#                     response_text = "I'm sorry, I couldn't find a patient registered with that mobile number. Could you please verify the number and try again?"
#                     conversation_history.append({
#                         "role": "assistant",
#                         "content": response_text
#                     })
#
#                     return AssessmentResponse(
#                         response=response_text,
#                         session_data=session_data,
#                         is_complete=False
#                     )
#
#         # Generate AI response
#         messages = [{"role": msg["role"], "content": msg["content"]}
#                     for msg in
#                     conversation_history[:-1]]  # Exclude the last user message as it will be added by AI service
#
#         ai_response = await ai_service.generate_response(messages, session_data)
#
#         # Add AI response to conversation history
#         conversation_history.append({
#             "role": "assistant",
#             "content": ai_response
#         })
#
#         # Update session stage based on conversation
#         session_data = ai_service.update_session_stage(
#             session_data, user_message, ai_response
#         )
#
#         # Update conversation history in session
#         session_data["conversation_history"] = conversation_history
#
#         # Check if assessment is complete
#         is_complete = session_data.get("assessment_complete", False)
#         assessment_id = None
#
#         # If complete, extract and save assessment data
#         if is_complete and not session_data.get("assessment_saved"):
#             # Extract structured data from conversation
#             assessment_data = await ai_service.extract_assessment_data(
#                 conversation_history
#             )
#
#             # Save to database
#             assessment = AssessmentService.create_assessment(
#                 db=db,
#                 patient_id=session_data["patient_id"],
#                 appointment_id=session_data.get("appointment_id"),
#                 document=assessment_data
#             )
#
#             assessment_id = assessment.id
#             session_data["assessment_saved"] = True
#             session_data["assessment_id"] = assessment_id
#
#         return AssessmentResponse(
#             response=ai_response,
#             session_data=session_data,
#             is_complete=is_complete,
#             assessment_id=assessment_id
#         )
#
#     except Exception as e:
#         import traceback
#         error_details = traceback.format_exc()
#         print(f"Error in chat_assessment: {str(e)}")
#         print(f"Full traceback:\n{error_details}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {str(e)}"
#         )
#
#
# @router.get("/assessment/{assessment_id}")
# async def get_assessment(
#         assessment_id: int,
#         db: Session = Depends(get_db)
# ):
#     """
#     Get assessment by ID
#
#     Args:
#         assessment_id: Assessment ID
#         db: Database session
#
#     Returns:
#         Assessment data
#     """
#     assessment = AssessmentService.get_assessment_by_id(db, assessment_id)
#
#     if not assessment:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Assessment not found"
#         )
#
#     return {
#         "id": assessment.id,
#         "patient_id": assessment.patient_id,
#         "appointment_id": assessment.appointment_id,
#         "document": assessment.document,
#         "created_at": assessment.created_at
#     }
#
#
# @router.get("/patient/{patient_id}/assessments")
# async def get_patient_assessments(
#         patient_id: int,
#         db: Session = Depends(get_db)
# ):
#     """
#     Get all assessments for a patient
#
#     Args:
#         patient_id: Patient ID
#         db: Database session
#
#     Returns:
#         List of assessments
#     """
#     assessments = AssessmentService.get_assessments_by_patient(db, patient_id)
#
#     return {
#         "patient_id": patient_id,
#         "assessments": [
#             {
#                 "id": a.id,
#                 "appointment_id": a.appointment_id,
#                 "document": a.document,
#                 "created_at": a.created_at
#             }
#             for a in assessments
#         ]
#     }
#
#
# @router.post("/reset-session")
# async def reset_session():
#     """
#     Reset session data (for testing or starting new conversation)
#
#     Returns:
#         Empty session data
#     """
#     return {
#         "session_data": {},
#         "message": "Session reset successfully"
#     }


"""
API routes for pre-assessment agent
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import re

from pre_assessment_agent.app.database import get_db
from pre_assessment_agent.app.models.schema_models import (
    AssessmentRequest,
    AssessmentResponse,
    ChatMessage
)
from pre_assessment_agent.app.services.ai_service import AIService
from pre_assessment_agent.app.services.patient_service import PatientService
from pre_assessment_agent.app.services.assessment_service import AssessmentService

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])

# Initialize AI service
ai_service = AIService()


def is_valid_mobile_number(text: str) -> bool:
    """Check if text contains a valid mobile number"""
    # Indian mobile number pattern (10 digits, optionally starting with +91 or 91)
    pattern = r'(\+91|91)?[6-9]\d{9}'
    return bool(re.search(pattern, text))


def extract_mobile_number(text: str) -> str:
    """Extract mobile number from text"""
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', text)

    # Remove country code if present
    if cleaned.startswith('+91'):
        cleaned = cleaned[3:]
    elif cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]

    return cleaned


@router.post("/chat", response_model=AssessmentResponse)
async def chat_assessment(
        request: AssessmentRequest,
        db: Session = Depends(get_db)
):
    """
    Main endpoint for chat-based pre-assessment

    Args:
        request: Assessment request with message and conversation history
        db: Database session

    Returns:
        AI response and updated session data
    """
    try:
        session_data = request.session_data or {}
        conversation_history = request.conversation_history or []
        user_message = request.message

        # Convert ChatMessage objects to dictionaries for processing
        conversation_history_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_history
        ]

        # Add user message to conversation history
        conversation_history_dicts.append({
            "role": "user",
            "content": user_message
        })

        # STAGE 1: Mobile number verification
        if not session_data.get("patient_verified"):
            # Check if user provided mobile number
            if is_valid_mobile_number(user_message):
                mobile_number = extract_mobile_number(user_message)

                # Verify patient in database
                patient, appointment = PatientService.verify_patient_and_get_details(
                    db, mobile_number
                )

                if patient:
                    # Patient found - update session
                    session_data["patient_verified"] = True
                    session_data["patient_id"] = patient.id
                    session_data["patient_name"] = patient.patient_name
                    session_data["mobile_number"] = mobile_number

                    if appointment:
                        session_data["appointment_id"] = appointment.id
                        session_data["appointment_number"] = appointment.appointment_number
                        session_data["appointment_date"] = appointment.appointment_date.strftime(
                            "%B %d, %Y at %I:%M %p") if appointment.appointment_date else None

                    session_data["current_stage"] = "greeting"

                else:
                    # Patient not found
                    response_text = "I'm sorry, I couldn't find a patient registered with that mobile number. Could you please verify the number and try again?"
                    conversation_history.append({
                        "role": "assistant",
                        "content": response_text
                    })

                    return AssessmentResponse(
                        response=response_text,
                        session_data=session_data,
                        is_complete=False
                    )

        # Generate AI response
        # Use all messages except we'll let the AI service handle it
        messages = conversation_history_dicts[:-1]  # Exclude the last user message

        ai_response = await ai_service.generate_response(messages, session_data)

        # Add AI response to conversation history
        conversation_history_dicts.append({
            "role": "assistant",
            "content": ai_response
        })

        # Update conversation history in session (store as dicts)
        session_data["conversation_history"] = conversation_history_dicts

        # Update session stage based on conversation
        session_data = ai_service.update_session_stage(
            session_data, user_message, ai_response
        )

        # Check if assessment is complete
        is_complete = session_data.get("assessment_complete", False)
        assessment_id = None

        # If complete, extract and save assessment data
        if is_complete and not session_data.get("assessment_saved"):
            # Extract structured data from conversation
            assessment_data = await ai_service.extract_assessment_data(
                conversation_history_dicts
            )

            # Save to database
            assessment = AssessmentService.create_assessment(
                db=db,
                patient_id=session_data["patient_id"],
                appointment_id=session_data.get("appointment_id"),
                document=assessment_data
            )

            assessment_id = assessment.id
            session_data["assessment_saved"] = True
            session_data["assessment_id"] = assessment_id

        return AssessmentResponse(
            response=ai_response,
            session_data=session_data,
            is_complete=is_complete,
            assessment_id=assessment_id
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in chat_assessment: {str(e)}")
        print(f"Full traceback:\n{error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/assessment/{assessment_id}")
async def get_assessment(
        assessment_id: int,
        db: Session = Depends(get_db)
):
    """
    Get assessment by ID

    Args:
        assessment_id: Assessment ID
        db: Database session

    Returns:
        Assessment data
    """
    assessment = AssessmentService.get_assessment_by_id(db, assessment_id)

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )

    return {
        "id": assessment.id,
        "patient_id": assessment.patient_id,
        "appointment_id": assessment.appointment_id,
        "document": assessment.document,
        "created_at": assessment.created_at
    }


@router.get("/patient/{patient_id}/assessments")
async def get_patient_assessments(
        patient_id: int,
        db: Session = Depends(get_db)
):
    """
    Get all assessments for a patient

    Args:
        patient_id: Patient ID
        db: Database session

    Returns:
        List of assessments
    """
    assessments = AssessmentService.get_assessments_by_patient(db, patient_id)

    return {
        "patient_id": patient_id,
        "assessments": [
            {
                "id": a.id,
                "appointment_id": a.appointment_id,
                "document": a.document,
                "created_at": a.created_at
            }
            for a in assessments
        ]
    }


@router.post("/reset-session")
async def reset_session():
    """
    Reset session data (for testing or starting new conversation)

    Returns:
        Empty session data
    """
    return {
        "session_data": {},
        "message": "Session reset successfully"
    }