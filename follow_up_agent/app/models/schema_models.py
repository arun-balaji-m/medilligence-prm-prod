# from pydantic import BaseModel
# from typing import Optional, Dict, Any
# from datetime import datetime
#
#
# class ChatRequest(BaseModel):
#     message: str
#     session_id: Optional[str] = None
#
#
# class ChatResponse(BaseModel):
#     response: str
#     session_id: str
#
#
# class FollowUpAdherenceDocument(BaseModel):
#     medication_received: str = ""
#     medication_adherence: str = ""
#     medication_timing: str = ""
#     side_effects_check: str = ""
#     recovery_assessment: str = ""
#     lifestyle_coaching: str = ""
#     early_followup_recommended: str = ""
#
#
# class PatientInfo(BaseModel):
#     id: int
#     patient_name: str
#     mobile_number: str
#
#
# class ConsultationInfo(BaseModel):
#     id: int
#     consultation_number: str
#     consultation_date: datetime
#     medication_id: Optional[int]
#     medication_document: Optional[Dict[str, Any]]

# #second version
# from pydantic import BaseModel
# from typing import Optional, Dict, Any
# from datetime import datetime
#
#
# class ChatRequest(BaseModel):
#     message: str
#     session_id: Optional[str] = None
#
#
# class ChatResponse(BaseModel):
#     response: str
#     session_id: str
#
#
# class FollowUpAdherenceDocument(BaseModel):
#     medication_received: str = ""
#     medication_adherence: str = ""
#     medication_timing: str = ""
#     side_effects_check: str = ""
#     recovery_assessment: str = ""
#     lifestyle_coaching: str = ""
#     early_followup_recommended: str = ""
#
#
# class PatientInfo(BaseModel):
#     id: int
#     patient_name: str
#     mobile_number: str
#
#
# class ConsultationInfo(BaseModel):
#     id: int
#     consultation_number: str
#     consultation_date: datetime
#     medication_id: Optional[int]
#     medication_document: Optional[Dict[str, Any]]

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


class FollowUpAdherenceDocument(BaseModel):
    medication_received: str = ""
    medication_adherence: str = ""
    medication_timing: str = ""
    side_effects_check: str = ""
    recovery_assessment: str = ""
    lifestyle_coaching: str = ""
    early_followup_recommended: str = ""


class PatientInfo(BaseModel):
    id: int
    patient_name: str
    mobile_number: str


class ConsultationInfo(BaseModel):
    id: int
    consultation_number: str
    consultation_date: datetime
    medication_id: Optional[int]
    medication_document: Optional[Dict[str, Any]]
