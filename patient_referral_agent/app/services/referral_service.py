# from sqlalchemy.orm import Session
# from patient_referral_agent.app.services.ai_service import AIService
# from patient_referral_agent.app.services.patient_service import PatientService
# from patient_referral_agent.app.services.document_service import DocumentService
# from patient_referral_agent.app.models.schema_models import PatientCreate, ChatResponse
# import json
#
#
# class ReferralService:
#     def __init__(self, db: Session):
#         self.db = db
#         self.ai_service = AIService()
#         self.patient_service = PatientService()
#         self.doc_service = DocumentService()
#         self.session_state = {}
#
#     def handle_message(self, session_id: str, message: str, patient_id: int = None) -> ChatResponse:
#         """Main conversation handler"""
#
#         # Initialize session
#         if session_id not in self.session_state:
#             self.session_state[session_id] = {
#                 "stage": "registration",
#                 "patient_data": {},
#                 "patient_id": None
#             }
#
#         state = self.session_state[session_id]
#
#         # Patient registration stage
#         if state["stage"] == "registration":
#             return self._handle_registration(session_id, message)
#
#         # Medical history stage
#         elif state["stage"] == "history":
#             return self._handle_history(session_id, message, state["patient_id"])
#
#         # Update existing timeline
#         elif state["stage"] == "update":
#             return self._handle_update(session_id, message, state["patient_id"])
#
#     def _handle_registration(self, session_id: str, message: str) -> ChatResponse:
#         state = self.session_state[session_id]
#
#         result = self.ai_service.collect_patient_info(message, state["patient_data"])
#
#         state["patient_data"] = result.get("patient_data", {})
#
#         if result.get("complete"):
#             # Create patient
#             patient_data = PatientCreate(**state["patient_data"])
#             patient = self.patient_service.create_patient(self.db, patient_data)
#
#             state["patient_id"] = patient.id
#             state["stage"] = "history"
#
#             return ChatResponse(
#                 response=result[
#                              "response"] + "\n\nWould you like to share your medical history verbally or upload a document (PDF)?",
#                 requires_input=True,
#                 input_type="text_or_file",
#                 patient_id=patient.id
#             )
#
#         return ChatResponse(
#             response=result["response"],
#             requires_input=True,
#             input_type="text"
#         )
#
#     def _handle_history(self, session_id: str, message: str, patient_id: int) -> ChatResponse:
#         referral = self.patient_service.get_referral(self.db, patient_id)
#         existing_timeline = referral.refferral_document.get("timeline", []) if referral else []
#
#         result = self.ai_service.collect_medical_history(message, existing_timeline)
#
#         if result.get("events"):
#             # Create timeline from collected events
#             timeline_data = self.ai_service.create_timeline_from_data(json.dumps(result["events"]))
#
#             merged_timeline = self.ai_service.merge_timelines(
#                 existing_timeline,
#                 timeline_data.get("timeline", [])
#             )
#
#             document_data = {
#                 "timeline": merged_timeline,
#                 "summary": timeline_data.get("summary", "")
#             }
#
#             if referral:
#                 self.patient_service.update_referral(self.db, patient_id, document_data)
#             else:
#                 self.patient_service.create_referral(self.db, patient_id, document_data)
#
#             if not result.get("needs_more"):
#                 self.session_state[session_id]["stage"] = "complete"
#                 return ChatResponse(
#                     response="Thank you! I've created your medical timeline. You can view it below.",
#                     requires_input=False,
#                     patient_id=patient_id,
#                     timeline=merged_timeline
#                 )
#
#         return ChatResponse(
#             response=result["response"],
#             requires_input=True,
#             input_type="text",
#             patient_id=patient_id
#         )
#
#     def _handle_update(self, session_id: str, message: str, patient_id: int) -> ChatResponse:
#         return self._handle_history(session_id, message, patient_id)
#
#     def process_document(self, pdf_path: str, patient_id: int) -> ChatResponse:
#         """Process uploaded PDF document"""
#
#         # Extract text
#         raw_text = self.doc_service.pdf_to_text(pdf_path)
#
#         # Chunk if too large
#         chunks = self.doc_service.chunk_text(raw_text, max_chars=4000)
#
#         all_timelines = []
#
#         for chunk in chunks:
#             # Sanitize with Grok
#             sanitized = self.ai_service.sanitize_text_with_grok(chunk)
#
#             # Create timeline
#             timeline_data = self.ai_service.create_timeline_from_data(sanitized)
#             all_timelines.extend(timeline_data.get("timeline", []))
#
#         # Merge with existing
#         referral = self.patient_service.get_referral(self.db, patient_id)
#         existing_timeline = referral.refferral_document.get("timeline", []) if referral else []
#
#         merged_timeline = self.ai_service.merge_timelines(existing_timeline, all_timelines)
#
#         document_data = {
#             "timeline": merged_timeline,
#             "summary": f"Medical history extracted from uploaded document. Total events: {len(merged_timeline)}"
#         }
#
#         if referral:
#             self.patient_service.update_referral(self.db, patient_id, document_data)
#         else:
#             self.patient_service.create_referral(self.db, patient_id, document_data)
#
#         return ChatResponse(
#             response="Document processed successfully! Your medical timeline has been created.",
#             requires_input=False,
#             patient_id=patient_id,
#             timeline=merged_timeline
#         )

##second version
#
# from sqlalchemy.orm import Session
# from patient_referral_agent.app.services.ai_service import AIService
# from patient_referral_agent.app.services.patient_service import PatientService
# from patient_referral_agent.app.services.document_service import DocumentService
# from patient_referral_agent.app.models.schema_models import PatientCreate, ChatResponse
# import json
#
#
# class ReferralService:
#     def __init__(self, db: Session):
#         self.db = db
#         self.ai_service = AIService()
#         self.patient_service = PatientService()
#         self.doc_service = DocumentService()
#         self.session_state = {}
#
#     def handle_message(self, session_id: str, message: str, patient_id: int = None) -> ChatResponse:
#         """Main conversation handler"""
#
#         try:
#             # Initialize session
#             if session_id not in self.session_state:
#                 self.session_state[session_id] = {
#                     "stage": "registration",
#                     "patient_data": {},
#                     "patient_id": None
#                 }
#
#             state = self.session_state[session_id]
#
#             # Patient registration stage
#             if state["stage"] == "registration":
#                 return self._handle_registration(session_id, message)
#
#             # Medical history stage
#             elif state["stage"] == "history":
#                 return self._handle_history(session_id, message, state["patient_id"])
#
#             # Update existing timeline
#             elif state["stage"] == "update":
#                 return self._handle_update(session_id, message, state["patient_id"])
#
#         except Exception as e:
#             print(f"Error in handle_message: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             return ChatResponse(
#                 response=f"I encountered an error. Please try again. Error: {str(e)}",
#                 requires_input=True,
#                 input_type="text"
#             )
#
#     def _handle_registration(self, session_id: str, message: str) -> ChatResponse:
#         state = self.session_state[session_id]
#
#         result = self.ai_service.collect_patient_info(message, state["patient_data"])
#
#         state["patient_data"] = result.get("patient_data", {})
#
#         if result.get("complete"):
#             # Create patient
#             patient_data = PatientCreate(**state["patient_data"])
#             patient = self.patient_service.create_patient(self.db, patient_data)
#
#             state["patient_id"] = patient.id
#             state["stage"] = "history"
#
#             return ChatResponse(
#                 response=result[
#                              "response"] + "\n\nWould you like to share your medical history verbally or upload a document (PDF)?",
#                 requires_input=True,
#                 input_type="text_or_file",
#                 patient_id=patient.id
#             )
#
#         return ChatResponse(
#             response=result["response"],
#             requires_input=True,
#             input_type="text"
#         )
#
#     def _handle_history(self, session_id: str, message: str, patient_id: int) -> ChatResponse:
#         referral = self.patient_service.get_referral(self.db, patient_id)
#         existing_timeline = referral.refferral_document.get("timeline", []) if referral else []
#
#         result = self.ai_service.collect_medical_history(message, existing_timeline)
#
#         if result.get("events"):
#             # Create timeline from collected events
#             timeline_data = self.ai_service.create_timeline_from_data(json.dumps(result["events"]))
#
#             merged_timeline = self.ai_service.merge_timelines(
#                 existing_timeline,
#                 timeline_data.get("timeline", [])
#             )
#
#             document_data = {
#                 "timeline": merged_timeline,
#                 "summary": timeline_data.get("summary", "")
#             }
#
#             if referral:
#                 self.patient_service.update_referral(self.db, patient_id, document_data)
#             else:
#                 self.patient_service.create_referral(self.db, patient_id, document_data)
#
#             if not result.get("needs_more"):
#                 self.session_state[session_id]["stage"] = "complete"
#                 return ChatResponse(
#                     response="Thank you! I've created your medical timeline. You can view it below.",
#                     requires_input=False,
#                     patient_id=patient_id,
#                     timeline=merged_timeline
#                 )
#
#         return ChatResponse(
#             response=result["response"],
#             requires_input=True,
#             input_type="text",
#             patient_id=patient_id
#         )
#
#     def _handle_update(self, session_id: str, message: str, patient_id: int) -> ChatResponse:
#         return self._handle_history(session_id, message, patient_id)
#
#     def process_document(self, pdf_path: str, patient_id: int) -> ChatResponse:
#         """Process uploaded PDF document"""
#
#         # Extract text
#         raw_text = self.doc_service.pdf_to_text(pdf_path)
#
#         # Chunk if too large
#         chunks = self.doc_service.chunk_text(raw_text, max_chars=4000)
#
#         all_timelines = []
#
#         for chunk in chunks:
#             # Sanitize with Grok
#             sanitized = self.ai_service.sanitize_text_with_grok(chunk)
#
#             # Create timeline
#             timeline_data = self.ai_service.create_timeline_from_data(sanitized)
#             all_timelines.extend(timeline_data.get("timeline", []))
#
#         # Merge with existing
#         referral = self.patient_service.get_referral(self.db, patient_id)
#         existing_timeline = referral.refferral_document.get("timeline", []) if referral else []
#
#         merged_timeline = self.ai_service.merge_timelines(existing_timeline, all_timelines)
#
#         document_data = {
#             "timeline": merged_timeline,
#             "summary": f"Medical history extracted from uploaded document. Total events: {len(merged_timeline)}"
#         }
#
#         if referral:
#             self.patient_service.update_referral(self.db, patient_id, document_data)
#         else:
#             self.patient_service.create_referral(self.db, patient_id, document_data)
#
#         return ChatResponse(
#             response="Document processed successfully! Your medical timeline has been created.",
#             requires_input=False,
#             patient_id=patient_id,
#             timeline=merged_timeline
#         )


##third version
#
# from sqlalchemy.orm import Session
# from patient_referral_agent.app.services.ai_service import AIService
# from patient_referral_agent.app.services.patient_service import PatientService
# from patient_referral_agent.app.services.document_service import DocumentService
# from patient_referral_agent.app.models.schema_models import PatientCreate, ChatResponse
# import json
#
#
# class ReferralService:
#     def __init__(self, db: Session):
#         self.db = db
#         self.ai_service = AIService()
#         self.patient_service = PatientService()
#         self.doc_service = DocumentService()
#         self.session_state = {}
#
#     def handle_message(self, session_id: str, message: str, patient_id: int = None) -> ChatResponse:
#         """Main conversation handler"""
#
#         try:
#             # Initialize session
#             if session_id not in self.session_state:
#                 self.session_state[session_id] = {
#                     "stage": "registration",
#                     "patient_data": {
#                         "patient_name": None,
#                         "dob": None,
#                         "gender": None,
#                         "mobile_number": None,
#                         "email": None
#                     },
#                     "patient_id": None
#                 }
#
#             state = self.session_state[session_id]
#
#             print(f"Session {session_id} - Stage: {state['stage']}, Message: {message}")
#
#             # Patient registration stage
#             if state["stage"] == "registration":
#                 return self._handle_registration(session_id, message)
#
#             # Medical history stage
#             elif state["stage"] == "history":
#                 return self._handle_history(session_id, message, state["patient_id"])
#
#             # Update existing timeline
#             elif state["stage"] == "update":
#                 return self._handle_update(session_id, message, state["patient_id"])
#
#         except Exception as e:
#             print(f"Error in handle_message: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             return ChatResponse(
#                 response=f"I encountered an error. Please try again. Error: {str(e)}",
#                 requires_input=True,
#                 input_type="text"
#             )
#
#     def _handle_registration(self, session_id: str, message: str) -> ChatResponse:
#         state = self.session_state[session_id]
#
#         # Initialize patient_data if not exists
#         if not state.get("patient_data"):
#             state["patient_data"] = {
#                 "patient_name": None,
#                 "dob": None,
#                 "gender": None,
#                 "mobile_number": None,
#                 "email": None
#             }
#
#         print(f"Current patient data before AI call: {state['patient_data']}")
#
#         result = self.ai_service.collect_patient_info(message, state["patient_data"])
#
#         # Update state with merged data
#         state["patient_data"] = result.get("patient_data", state["patient_data"])
#
#         print(f"Updated patient data: {state['patient_data']}")
#         print(f"Complete: {result.get('complete')}")
#
#         if result.get("complete"):
#             # Validate all required fields are present
#             required_fields = ["patient_name", "dob", "gender", "mobile_number"]
#             if all(state["patient_data"].get(field) for field in required_fields):
#                 try:
#                     # Create patient
#                     patient_data = PatientCreate(**state["patient_data"])
#                     patient = self.patient_service.create_patient(self.db, patient_data)
#
#                     state["patient_id"] = patient.id
#                     state["stage"] = "history"
#
#                     print(f"Patient created with ID: {patient.id}")
#
#                     return ChatResponse(
#                         response=f"Great! I've registered you successfully. Now, would you like to share your medical history verbally or upload a document (PDF)?",
#                         requires_input=True,
#                         input_type="text_or_file",
#                         patient_id=patient.id
#                     )
#                 except Exception as e:
#                     print(f"Error creating patient: {str(e)}")
#                     return ChatResponse(
#                         response=f"There was an error creating your profile. Please try again. Error: {str(e)}",
#                         requires_input=True,
#                         input_type="text"
#                     )
#             else:
#                 # Not all fields filled, continue asking
#                 print("Not all required fields filled, continuing registration")
#
#         return ChatResponse(
#             response=result["response"],
#             requires_input=True,
#             input_type="text"
#         )
#
#     def _handle_history(self, session_id: str, message: str, patient_id: int) -> ChatResponse:
#         referral = self.patient_service.get_referral(self.db, patient_id)
#         existing_timeline = referral.refferral_document.get("timeline", []) if referral else []
#
#         result = self.ai_service.collect_medical_history(message, existing_timeline)
#
#         if result.get("events"):
#             # Create timeline from collected events
#             timeline_data = self.ai_service.create_timeline_from_data(json.dumps(result["events"]))
#
#             merged_timeline = self.ai_service.merge_timelines(
#                 existing_timeline,
#                 timeline_data.get("timeline", [])
#             )
#
#             document_data = {
#                 "timeline": merged_timeline,
#                 "summary": timeline_data.get("summary", "")
#             }
#
#             if referral:
#                 self.patient_service.update_referral(self.db, patient_id, document_data)
#             else:
#                 self.patient_service.create_referral(self.db, patient_id, document_data)
#
#             if not result.get("needs_more"):
#                 self.session_state[session_id]["stage"] = "complete"
#                 return ChatResponse(
#                     response="Thank you! I've created your medical timeline. You can view it below.",
#                     requires_input=False,
#                     patient_id=patient_id,
#                     timeline=merged_timeline
#                 )
#
#         return ChatResponse(
#             response=result["response"],
#             requires_input=True,
#             input_type="text",
#             patient_id=patient_id
#         )
#
#     def _handle_update(self, session_id: str, message: str, patient_id: int) -> ChatResponse:
#         return self._handle_history(session_id, message, patient_id)
#
#     def process_document(self, pdf_path: str, patient_id: int) -> ChatResponse:
#         """Process uploaded PDF document"""
#
#         # Extract text
#         raw_text = self.doc_service.pdf_to_text(pdf_path)
#
#         # Chunk if too large
#         chunks = self.doc_service.chunk_text(raw_text, max_chars=4000)
#
#         all_timelines = []
#
#         for chunk in chunks:
#             # Sanitize with Grok
#             sanitized = self.ai_service.sanitize_text_with_grok(chunk)
#
#             # Create timeline
#             timeline_data = self.ai_service.create_timeline_from_data(sanitized)
#             all_timelines.extend(timeline_data.get("timeline", []))
#
#         # Merge with existing
#         referral = self.patient_service.get_referral(self.db, patient_id)
#         existing_timeline = referral.refferral_document.get("timeline", []) if referral else []
#
#         merged_timeline = self.ai_service.merge_timelines(existing_timeline, all_timelines)
#
#         document_data = {
#             "timeline": merged_timeline,
#             "summary": f"Medical history extracted from uploaded document. Total events: {len(merged_timeline)}"
#         }
#
#         if referral:
#             self.patient_service.update_referral(self.db, patient_id, document_data)
#         else:
#             self.patient_service.create_referral(self.db, patient_id, document_data)
#
#         return ChatResponse(
#             response="Document processed successfully! Your medical timeline has been created.",
#             requires_input=False,
#             patient_id=patient_id,
#             timeline=merged_timeline
#         )

# ##fourth version
#
# from sqlalchemy.orm import Session
# from patient_referral_agent.app.services.ai_service import AIService
# from patient_referral_agent.app.services.patient_service import PatientService
# from patient_referral_agent.app.services.document_service import DocumentService
# from patient_referral_agent.app.models.schema_models import PatientCreate, ChatResponse
# import json
#
#
# class ReferralService:
#     def __init__(self, db: Session):
#         self.db = db
#         self.ai_service = AIService()
#         self.patient_service = PatientService()
#         self.doc_service = DocumentService()
#         self.session_state = {}
#
#     def handle_message(self, session_id: str, message: str, patient_id: int = None) -> ChatResponse:
#         """Main conversation handler"""
#
#         try:
#             # Initialize session
#             if session_id not in self.session_state:
#                 self.session_state[session_id] = {
#                     "stage": "registration",
#                     "patient_data": {
#                         "patient_name": None,
#                         "dob": None,
#                         "gender": None,
#                         "mobile_number": None,
#                         "email": None
#                     },
#                     "asked_fields": [],
#                     "patient_id": None
#                 }
#
#             state = self.session_state[session_id]
#
#             print(f"Session {session_id} - Stage: {state['stage']}, Message: {message}")
#
#             # Patient registration stage
#             if state["stage"] == "registration":
#                 return self._handle_registration(session_id, message)
#
#             # Medical history stage
#             elif state["stage"] == "history":
#                 return self._handle_history(session_id, message, state["patient_id"])
#
#             # Update existing timeline
#             elif state["stage"] == "update":
#                 return self._handle_update(session_id, message, state["patient_id"])
#
#         except Exception as e:
#             print(f"Error in handle_message: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             return ChatResponse(
#                 response=f"I encountered an error. Please try again. Error: {str(e)}",
#                 requires_input=True,
#                 input_type="text"
#             )
#
#     def _handle_registration(self, session_id: str, message: str) -> ChatResponse:
#         state = self.session_state[session_id]
#
#         # Initialize patient_data and asked_fields if not exists
#         if not state.get("patient_data"):
#             state["patient_data"] = {
#                 "patient_name": None,
#                 "dob": None,
#                 "gender": None,
#                 "mobile_number": None,
#                 "email": None
#             }
#         if not state.get("asked_fields"):
#             state["asked_fields"] = []
#
#         print(f"Current patient data before AI call: {state['patient_data']}")
#         print(f"Already asked fields: {state['asked_fields']}")
#
#         result = self.ai_service.collect_patient_info(
#             message,
#             state["patient_data"],
#             state["asked_fields"]
#         )
#
#         # Update state with merged data
#         state["patient_data"] = result.get("patient_data", state["patient_data"])
#         state["asked_fields"] = result.get("asked_fields", state["asked_fields"])
#
#         print(f"Updated patient data: {state['patient_data']}")
#         print(f"Updated asked fields: {state['asked_fields']}")
#         print(f"Complete: {result.get('complete')}")
#
#         if result.get("complete"):
#             # Check if we have minimum required fields
#             required_fields = ["patient_name", "dob", "gender", "mobile_number"]
#             missing_required = [f for f in required_fields if not state["patient_data"].get(f)]
#
#             if not missing_required:
#                 try:
#                     # Prepare patient data - convert "none" to None for email
#                     patient_dict = state["patient_data"].copy()
#                     if patient_dict.get("email") == "none":
#                         patient_dict["email"] = None
#
#                     # Create patient
#                     patient_data = PatientCreate(**patient_dict)
#                     patient = self.patient_service.create_patient(self.db, patient_data)
#
#                     state["patient_id"] = patient.id
#                     state["stage"] = "history"
#
#                     print(f"Patient created with ID: {patient.id}")
#
#                     return ChatResponse(
#                         response="Great! I've registered you successfully. Now, would you like to share your medical history with me, or would you prefer to upload a document (PDF)?",
#                         requires_input=True,
#                         input_type="text_or_file",
#                         patient_id=patient.id
#                     )
#                 except Exception as e:
#                     print(f"Error creating patient: {str(e)}")
#                     import traceback
#                     traceback.print_exc()
#                     return ChatResponse(
#                         response=f"There was an error creating your profile. Please try again.",
#                         requires_input=True,
#                         input_type="text"
#                     )
#             else:
#                 # Still missing required fields
#                 print(f"Still missing required fields: {missing_required}")
#
#         return ChatResponse(
#             response=result["response"],
#             requires_input=True,
#             input_type="text"
#         )
#
#     def _handle_history(self, session_id: str, message: str, patient_id: int) -> ChatResponse:
#         referral = self.patient_service.get_referral(self.db, patient_id)
#         existing_timeline = referral.refferral_document.get("timeline", []) if referral else []
#
#         result = self.ai_service.collect_medical_history(message, existing_timeline)
#
#         if result.get("events"):
#             # Create timeline from collected events
#             timeline_data = self.ai_service.create_timeline_from_data(json.dumps(result["events"]))
#
#             merged_timeline = self.ai_service.merge_timelines(
#                 existing_timeline,
#                 timeline_data.get("timeline", [])
#             )
#
#             document_data = {
#                 "timeline": merged_timeline,
#                 "summary": timeline_data.get("summary", "")
#             }
#
#             if referral:
#                 self.patient_service.update_referral(self.db, patient_id, document_data)
#             else:
#                 self.patient_service.create_referral(self.db, patient_id, document_data)
#
#             if not result.get("needs_more"):
#                 self.session_state[session_id]["stage"] = "complete"
#                 return ChatResponse(
#                     response="Thank you! I've created your medical timeline. You can view it below.",
#                     requires_input=False,
#                     patient_id=patient_id,
#                     timeline=merged_timeline
#                 )
#
#         return ChatResponse(
#             response=result["response"],
#             requires_input=True,
#             input_type="text",
#             patient_id=patient_id
#         )
#
#     def _handle_update(self, session_id: str, message: str, patient_id: int) -> ChatResponse:
#         return self._handle_history(session_id, message, patient_id)
#
#     def process_document(self, pdf_path: str, patient_id: int) -> ChatResponse:
#         """Process uploaded PDF document"""
#
#         # Extract text
#         raw_text = self.doc_service.pdf_to_text(pdf_path)
#
#         # Chunk if too large
#         chunks = self.doc_service.chunk_text(raw_text, max_chars=4000)
#
#         all_timelines = []
#
#         for chunk in chunks:
#             # Sanitize with Grok
#             sanitized = self.ai_service.sanitize_text_with_grok(chunk)
#
#             # Create timeline
#             timeline_data = self.ai_service.create_timeline_from_data(sanitized)
#             all_timelines.extend(timeline_data.get("timeline", []))
#
#         # Merge with existing
#         referral = self.patient_service.get_referral(self.db, patient_id)
#         existing_timeline = referral.refferral_document.get("timeline", []) if referral else []
#
#         merged_timeline = self.ai_service.merge_timelines(existing_timeline, all_timelines)
#
#         document_data = {
#             "timeline": merged_timeline,
#             "summary": f"Medical history extracted from uploaded document. Total events: {len(merged_timeline)}"
#         }
#
#         if referral:
#             self.patient_service.update_referral(self.db, patient_id, document_data)
#         else:
#             self.patient_service.create_referral(self.db, patient_id, document_data)
#
#         return ChatResponse(
#             response="Document processed successfully! Your medical timeline has been created.",
#             requires_input=False,
#             patient_id=patient_id,
#             timeline=merged_timeline
#         )

##fifth version

from sqlalchemy.orm import Session
from patient_referral_agent.app.services.ai_service import AIService
from patient_referral_agent.app.services.patient_service import PatientService
from patient_referral_agent.app.services.document_service import DocumentService
from patient_referral_agent.app.models.schema_models import PatientCreate, ChatResponse
import json


class ReferralService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.patient_service = PatientService()
        self.doc_service = DocumentService()
        self.session_state = {}

    def handle_message(self, session_id: str, message: str, patient_id: int = None) -> ChatResponse:
        """Main conversation handler"""

        try:
            # Initialize session
            if session_id not in self.session_state:
                self.session_state[session_id] = {
                    "stage": "registration",
                    "patient_data": {
                        "patient_name": None,
                        "dob": None,
                        "gender": None,
                        "mobile_number": None,
                        "email": None
                    },
                    "asked_fields": [],
                    "patient_id": None
                }

            state = self.session_state[session_id]

            print(f"Session {session_id} - Stage: {state['stage']}, Message: {message}")

            # Patient registration stage
            if state["stage"] == "registration":
                return self._handle_registration(session_id, message)

            # Medical history stage
            elif state["stage"] == "history":
                return self._handle_history(session_id, message, state["patient_id"])

            # Update existing timeline
            elif state["stage"] == "update":
                return self._handle_update(session_id, message, state["patient_id"])

        except Exception as e:
            print(f"Error in handle_message: {str(e)}")
            import traceback
            traceback.print_exc()
            return ChatResponse(
                response=f"I encountered an error. Please try again. Error: {str(e)}",
                requires_input=True,
                input_type="text"
            )

    def _handle_registration(self, session_id: str, message: str) -> ChatResponse:
        state = self.session_state[session_id]

        # Initialize patient_data and asked_fields if not exists
        if not state.get("patient_data"):
            state["patient_data"] = {
                "patient_name": None,
                "dob": None,
                "gender": None,
                "mobile_number": None,
                "email": None
            }
        if not state.get("asked_fields"):
            state["asked_fields"] = []

        print(f"Current patient data before AI call: {state['patient_data']}")
        print(f"Already asked fields: {state['asked_fields']}")

        result = self.ai_service.collect_patient_info(
            message,
            state["patient_data"],
            state["asked_fields"]
        )

        # Update state with merged data
        state["patient_data"] = result.get("patient_data", state["patient_data"])
        state["asked_fields"] = result.get("asked_fields", state["asked_fields"])

        print(f"Updated patient data: {state['patient_data']}")
        print(f"Updated asked fields: {state['asked_fields']}")
        print(f"Complete: {result.get('complete')}")

        if result.get("complete"):
            # Check if we have minimum required fields
            required_fields = ["patient_name", "dob", "gender", "mobile_number"]
            missing_required = [f for f in required_fields if not state["patient_data"].get(f)]

            if not missing_required:
                try:
                    # Prepare patient data - convert "none" to None for email
                    patient_dict = state["patient_data"].copy()
                    if patient_dict.get("email") == "none":
                        patient_dict["email"] = None

                    # Create patient
                    patient_data = PatientCreate(**patient_dict)
                    patient = self.patient_service.create_patient(self.db, patient_data)

                    state["patient_id"] = patient.id
                    state["stage"] = "history"

                    print(f"Patient created with ID: {patient.id}")

                    return ChatResponse(
                        response="Great! I've registered you successfully. Now, would you like to share your medical history with me, or would you prefer to upload a document (PDF)?",
                        requires_input=True,
                        input_type="text_or_file",
                        patient_id=patient.id
                    )
                except Exception as e:
                    print(f"Error creating patient: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return ChatResponse(
                        response=f"There was an error creating your profile. Please try again.",
                        requires_input=True,
                        input_type="text"
                    )
            else:
                # Still missing required fields
                print(f"Still missing required fields: {missing_required}")

        return ChatResponse(
            response=result["response"],
            requires_input=True,
            input_type="text"
        )

    def _handle_history(self, session_id: str, message: str, patient_id: int) -> ChatResponse:
        referral = self.patient_service.get_referral(self.db, patient_id)
        existing_timeline = referral.refferral_document.get("timeline", []) if referral else []

        result = self.ai_service.collect_medical_history(message, existing_timeline)

        if result.get("events"):
            # Create timeline from collected events
            timeline_data = self.ai_service.create_timeline_from_data(json.dumps(result["events"]))

            merged_timeline = self.ai_service.merge_timelines(
                existing_timeline,
                timeline_data.get("timeline", [])
            )

            document_data = {
                "timeline": merged_timeline,
                "summary": timeline_data.get("summary", "")
            }

            if referral:
                self.patient_service.update_referral(self.db, patient_id, document_data)
            else:
                self.patient_service.create_referral(self.db, patient_id, document_data)

            if not result.get("needs_more"):
                self.session_state[session_id]["stage"] = "complete"
                return ChatResponse(
                    response="Thank you! I've created your medical timeline. You can view it below.",
                    requires_input=False,
                    patient_id=patient_id,
                    timeline=merged_timeline
                )

        return ChatResponse(
            response=result["response"],
            requires_input=True,
            input_type="text",
            patient_id=patient_id
        )

    def _handle_update(self, session_id: str, message: str, patient_id: int) -> ChatResponse:
        return self._handle_history(session_id, message, patient_id)

    def process_document(self, pdf_path: str, patient_id: int) -> ChatResponse:
        """Process uploaded PDF document"""

        try:
            print(f"Processing document: {pdf_path}")

            # Extract text
            raw_text = self.doc_service.pdf_to_text(pdf_path)

            if not raw_text or len(raw_text.strip()) < 50:
                return ChatResponse(
                    response="I couldn't extract enough text from the document. Please ensure the PDF contains readable text or try uploading a different document.",
                    requires_input=True,
                    input_type="text_or_file",
                    patient_id=patient_id
                )

            print(f"Extracted {len(raw_text)} characters from PDF")

            # Chunk if too large
            chunks = self.doc_service.chunk_text(raw_text, max_chars=4000)
            print(f"Split into {len(chunks)} chunks")

            all_timelines = []

            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i + 1}/{len(chunks)}")

                # Sanitize with Grok (or basic sanitization if Grok fails)
                sanitized = self.ai_service.sanitize_text_with_grok(chunk)
                print(f"Sanitized chunk {i + 1}")

                # Create timeline
                try:
                    timeline_data = self.ai_service.create_timeline_from_data(sanitized)
                    all_timelines.extend(timeline_data.get("timeline", []))
                    print(f"Created {len(timeline_data.get('timeline', []))} timeline events from chunk {i + 1}")
                except Exception as e:
                    print(f"Error creating timeline from chunk {i + 1}: {str(e)}")
                    continue

            if not all_timelines:
                return ChatResponse(
                    response="I processed the document but couldn't extract any medical timeline events. Would you like to tell me about your medical history verbally instead?",
                    requires_input=True,
                    input_type="text",
                    patient_id=patient_id
                )

            # Merge with existing
            referral = self.patient_service.get_referral(self.db, patient_id)
            existing_timeline = referral.refferral_document.get("timeline", []) if referral else []

            merged_timeline = self.ai_service.merge_timelines(existing_timeline, all_timelines)

            document_data = {
                "timeline": merged_timeline,
                "summary": f"Medical history extracted from uploaded document. Total events: {len(merged_timeline)}"
            }

            if referral:
                self.patient_service.update_referral(self.db, patient_id, document_data)
            else:
                self.patient_service.create_referral(self.db, patient_id, document_data)

            print(f"✓ Document processed successfully. Total timeline events: {len(merged_timeline)}")

            return ChatResponse(
                response=f"Document processed successfully! I've extracted {len(all_timelines)} medical events from your document and created your timeline.",
                requires_input=False,
                patient_id=patient_id,
                timeline=merged_timeline
            )

        except Exception as e:
            print(f"Error in process_document: {str(e)}")
            import traceback
            traceback.print_exc()

            return ChatResponse(
                response="There was an error processing your document. Would you like to tell me about your medical history verbally instead?",
                requires_input=True,
                input_type="text",
                patient_id=patient_id
            )