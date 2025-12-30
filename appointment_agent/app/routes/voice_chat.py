# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from sqlalchemy.orm import Session
# import asyncio
# import json
# import os
# import websockets
# import time
# from appointment_agent.app.database import get_db
# from appointment_agent.app.utils.voice_handler import VoiceHandler
# from appointment_agent.app.utils.ai_handler import process_chat_message, add_function_result
# from appointment_agent.app import crud
# from datetime import datetime
#
# router = APIRouter(prefix="/api/voice", tags=["voice"])
#
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
#
# # Welcome message for voice
# WELCOME_MESSAGE = "Hello! I'm your medical appointment assistant. I can help you book appointments, check available slots, or manage your existing appointments. How can I help you today?"
#
#
# def execute_function(function_name: str, function_args: dict, db: Session):
#     """Execute the requested function and return result"""
#     try:
#         if function_name == "getPatientDetails":
#             patient = crud.get_patient_by_mobile(db, function_args["mobile_number"])
#             if patient:
#                 return json.dumps({
#                     "success": True,
#                     "data": {
#                         "id": patient.id,
#                         "patient_name": patient.patient_name,
#                         "patient_mrn": patient.patient_mrn,
#                         "dob": str(patient.dob) if patient.dob else None,
#                         "gender": patient.gender,
#                         "mobile_number": patient.mobile_number,
#                         "email": patient.email
#                     }
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "Patient not found"})
#
#         elif function_name == "getDoctorDepartmentDetails":
#             doctors = crud.get_doctors_by_name_or_department(
#                 db,
#                 function_args.get("doctor_name"),
#                 function_args.get("specialization")
#             )
#             if doctors:
#                 return json.dumps({
#                     "success": True,
#                     "data": [
#                         {
#                             "id": doc.id,
#                             "doctor_name": doc.doctor_name,
#                             "specialization": doc.specialization
#                         }
#                         for doc in doctors
#                     ]
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "No doctors found"})
#
#         elif function_name == "getAvailableSlots":
#             date_str = function_args["appointment_date"]
#             date_obj = datetime.strptime(date_str, "%Y-%m-%d")
#
#             slots = crud.get_available_slots(
#                 db,
#                 function_args.get("doctor_id"),
#                 None,
#                 date_obj
#             )
#
#             if slots:
#                 return json.dumps({
#                     "success": True,
#                     "data": [
#                         {
#                             "id": slot.id,
#                             "doctor_id": slot.doctor_id,
#                             "doctor_name": slot.doctor.doctor_name if slot.doctor else None,
#                             "specialization": slot.doctor.specialization if slot.doctor else None,
#                             "start_time": slot.start_time.isoformat(),
#                             "end_time": slot.end_time.isoformat(),
#                             "status": slot.status
#                         }
#                         for slot in slots
#                     ]
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "No available slots found"})
#
#         elif function_name == "bookAnAppointment":
#             appointment_date = datetime.fromisoformat(function_args["appointment_date"])
#             appointment, error = crud.book_appointment(
#                 db,
#                 function_args["patient_id"],
#                 function_args["slot_id"],
#                 appointment_date
#             )
#
#             if error:
#                 return json.dumps({"success": False, "message": error})
#
#             return json.dumps({
#                 "success": True,
#                 "data": {
#                     "id": appointment.id,
#                     "appointment_number": appointment.appointment_number,
#                     "appointment_date": appointment.appointment_date.isoformat(),
#                     "slot_id": appointment.slot_id,
#                     "patient_id": appointment.patient_id
#                 }
#             })
#
#         elif function_name == "cancelAppointment":
#             success, error = crud.cancel_appointment(db, function_args["appointment_id"])
#
#             if error:
#                 return json.dumps({"success": False, "message": error})
#
#             return json.dumps({"success": True, "message": "Appointment cancelled successfully"})
#
#         else:
#             return json.dumps({"success": False, "message": f"Unknown function: {function_name}"})
#
#     except Exception as e:
#         return json.dumps({"success": False, "message": f"Error: {str(e)}"})
#
#
# async def process_transcript_with_ai(transcript: str, session_id: str, db: Session, websocket: WebSocket,
#                                      voice_handler: VoiceHandler):
#     """Process transcript with AI and handle function calls"""
#     try:
#         await websocket.send_json({
#             "type": "status",
#             "message": "Processing..."
#         })
#
#         # Process with AI
#         result = process_chat_message(transcript, session_id)
#
#         # Handle function calls in a loop
#         while result["type"] == "function_call":
#             function_name = result["function_name"]
#             function_args = result["function_args"]
#
#             print(f"Calling function: {function_name} with args: {function_args}")
#
#             # Execute the function
#             function_result = execute_function(function_name, function_args, db)
#
#             # Send result back to AI and get next response
#             result = add_function_result(session_id, function_name, function_result)
#
#         # Get final text response
#         ai_response = result["content"]
#
#         await websocket.send_json({
#             "type": "response",
#             "text": ai_response
#         })
#
#         # Generate speech
#         await websocket.send_json({
#             "type": "status",
#             "message": "Speaking..."
#         })
#
#         audio_bytes = await voice_handler.speak_with_elevenlabs(ai_response)
#
#         if audio_bytes:
#             await websocket.send_bytes(audio_bytes)
#             await websocket.send_json({
#                 "type": "audio_complete",
#                 "message": "Audio sent"
#             })
#
#         await websocket.send_json({
#             "type": "status",
#             "message": "Listening..."
#         })
#
#     except Exception as e:
#         print(f"Error processing transcript: {e}")
#         import traceback
#         traceback.print_exc()
#         await websocket.send_json({
#             "type": "error",
#             "message": str(e)
#         })
#
#
# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     """WebSocket endpoint for real-time voice interaction"""
#     await websocket.accept()
#     session_id = f"voice_session_{id(websocket)}"
#     voice_handler = VoiceHandler(session_id)
#
#     # Get database session
#     db = next(get_db())
#
#     deepgram_ws = None
#
#     try:
#         # Connect to Deepgram WebSocket
#         deepgram_url = "wss://api.deepgram.com/v1/listen?model=nova-2&interim_results=true&punctuate=true&vad_events=true"
#
#         deepgram_ws = await websockets.connect(
#             deepgram_url,
#             additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
#         )
#
#         print("Connected to Deepgram for voice")
#
#         # Send welcome message with voice
#         await websocket.send_json({"type": "status", "message": "Voice assistant ready"})
#
#         # Speak welcome message
#         await websocket.send_json({
#             "type": "response",
#             "text": WELCOME_MESSAGE
#         })
#
#         welcome_audio = await voice_handler.speak_with_elevenlabs(WELCOME_MESSAGE)
#         if welcome_audio:
#             await websocket.send_bytes(welcome_audio)
#             await websocket.send_json({
#                 "type": "audio_complete",
#                 "message": "Welcome audio sent"
#             })
#
#         await websocket.send_json({"type": "status", "message": "Listening..."})
#
#         # Handle messages concurrently
#         async def receive_from_client():
#             while True:
#                 try:
#                     message = await websocket.receive()
#
#                     if "bytes" in message:
#                         # Forward audio to Deepgram
#                         audio_size = len(message['bytes'])
#                         if audio_size > 0:
#                             await deepgram_ws.send(message["bytes"])
#                     elif "text" in message:
#                         data = json.loads(message["text"])
#                         if data.get("type") == "stop":
#                             break
#
#                 except WebSocketDisconnect:
#                     print("Client disconnected")
#                     break
#                 except Exception as e:
#                     print(f"Error receiving from client: {e}")
#                     break
#
#         async def receive_from_deepgram():
#             while True:
#                 try:
#                     response = await deepgram_ws.recv()
#                     data = json.loads(response)
#
#                     msg_type = data.get("type", "")
#
#                     if msg_type == "Results":
#                         channel = data.get("channel", {})
#                         alternatives = channel.get("alternatives", [])
#
#                         if alternatives:
#                             transcript = alternatives[0].get("transcript", "").strip()
#                             is_final = data.get("is_final", False)
#                             speech_final = data.get("speech_final", False)
#
#                             if transcript:
#                                 if is_final:
#                                     voice_handler.current_transcript += " " + transcript
#                                     voice_handler.current_transcript = voice_handler.current_transcript.strip()
#                                     voice_handler.last_speech_time = time.time()
#
#                                     await websocket.send_json({
#                                         "type": "interim_transcript",
#                                         "text": voice_handler.current_transcript
#                                     })
#
#                                 # Process when speech is final
#                                 if speech_final and voice_handler.current_transcript and not voice_handler.is_processing:
#                                     voice_handler.is_processing = True
#                                     final_transcript = voice_handler.current_transcript
#                                     voice_handler.current_transcript = ""
#
#                                     print(f"Processing voice transcript: '{final_transcript}'")
#
#                                     await websocket.send_json({
#                                         "type": "transcript",
#                                         "text": final_transcript
#                                     })
#
#                                     # Process with AI (handles function calls)
#                                     await process_transcript_with_ai(
#                                         final_transcript,
#                                         session_id,
#                                         db,
#                                         websocket,
#                                         voice_handler
#                                     )
#
#                                     voice_handler.is_processing = False
#
#                     elif msg_type == "SpeechStarted":
#                         await websocket.send_json({"type": "speech_started"})
#
#                     elif msg_type == "UtteranceEnd":
#                         if voice_handler.current_transcript and not voice_handler.is_processing:
#                             await asyncio.sleep(0.5)
#
#                             if voice_handler.current_transcript and not voice_handler.is_processing:
#                                 voice_handler.is_processing = True
#                                 final_transcript = voice_handler.current_transcript
#                                 voice_handler.current_transcript = ""
#
#                                 await websocket.send_json({
#                                     "type": "transcript",
#                                     "text": final_transcript
#                                 })
#
#                                 # Process with AI
#                                 await process_transcript_with_ai(
#                                     final_transcript,
#                                     session_id,
#                                     db,
#                                     websocket,
#                                     voice_handler
#                                 )
#
#                                 voice_handler.is_processing = False
#
#                 except websockets.exceptions.ConnectionClosed:
#                     print("Deepgram connection closed")
#                     break
#                 except Exception as e:
#                     print(f"Error receiving from Deepgram: {e}")
#                     import traceback
#                     traceback.print_exc()
#                     break
#
#         # Run both tasks concurrently
#         await asyncio.gather(
#             receive_from_client(),
#             receive_from_deepgram()
#         )
#
#     except Exception as e:
#         print(f"WebSocket error: {e}")
#         import traceback
#         traceback.print_exc()
#         await websocket.send_json({"type": "error", "message": str(e)})
#     finally:
#         if deepgram_ws:
#             await deepgram_ws.close()
#         db.close()

# ##second version
# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from sqlalchemy.orm import Session
# import asyncio
# import json
# import os
# import websockets
# import time
# from appointment_agent.app.database import get_db
# from appointment_agent.app.utils.voice_handler import VoiceHandler
# from appointment_agent.app.utils.ai_handler import process_chat_message, add_function_result
# from appointment_agent.app import crud
# from datetime import datetime
#
# router = APIRouter(prefix="/api/voice", tags=["voice"])
#
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
#
# # Welcome message for voice
# WELCOME_MESSAGE = "Hello! I'm your medical appointment assistant. I can help you book appointments, check available slots, or manage your existing appointments. How can I help you today?"
#
#
# @router.get("/test-keys")
# async def test_api_keys():
#     """Test if API keys are configured"""
#     return {
#         "deepgram": "configured" if DEEPGRAM_API_KEY else "missing",
#         "deepgram_length": len(DEEPGRAM_API_KEY) if DEEPGRAM_API_KEY else 0,
#         "elevenlabs": "configured" if os.getenv("ELEVENLABS_API_KEY") else "missing"
#     }
#
#
# def execute_function(function_name: str, function_args: dict, db: Session):
#     """Execute the requested function and return result"""
#     try:
#         if function_name == "getPatientDetails":
#             patient = crud.get_patient_by_mobile(db, function_args["mobile_number"])
#             if patient:
#                 return json.dumps({
#                     "success": True,
#                     "data": {
#                         "id": patient.id,
#                         "patient_name": patient.patient_name,
#                         "patient_mrn": patient.patient_mrn,
#                         "dob": str(patient.dob) if patient.dob else None,
#                         "gender": patient.gender,
#                         "mobile_number": patient.mobile_number,
#                         "email": patient.email
#                     }
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "Patient not found"})
#
#         elif function_name == "getDoctorDepartmentDetails":
#             doctors = crud.get_doctors_by_name_or_department(
#                 db,
#                 function_args.get("doctor_name"),
#                 function_args.get("specialization")
#             )
#             if doctors:
#                 return json.dumps({
#                     "success": True,
#                     "data": [
#                         {
#                             "id": doc.id,
#                             "doctor_name": doc.doctor_name,
#                             "specialization": doc.specialization
#                         }
#                         for doc in doctors
#                     ]
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "No doctors found"})
#
#         elif function_name == "getAvailableSlots":
#             date_str = function_args["appointment_date"]
#             date_obj = datetime.strptime(date_str, "%Y-%m-%d")
#
#             slots = crud.get_available_slots(
#                 db,
#                 function_args.get("doctor_id"),
#                 None,
#                 date_obj
#             )
#
#             if slots:
#                 return json.dumps({
#                     "success": True,
#                     "data": [
#                         {
#                             "id": slot.id,
#                             "doctor_id": slot.doctor_id,
#                             "doctor_name": slot.doctor.doctor_name if slot.doctor else None,
#                             "specialization": slot.doctor.specialization if slot.doctor else None,
#                             "start_time": slot.start_time.isoformat(),
#                             "end_time": slot.end_time.isoformat(),
#                             "status": slot.status
#                         }
#                         for slot in slots
#                     ]
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "No available slots found"})
#
#         elif function_name == "bookAnAppointment":
#             appointment_date = datetime.fromisoformat(function_args["appointment_date"])
#             appointment, error = crud.book_appointment(
#                 db,
#                 function_args["patient_id"],
#                 function_args["slot_id"],
#                 appointment_date
#             )
#
#             if error:
#                 return json.dumps({"success": False, "message": error})
#
#             return json.dumps({
#                 "success": True,
#                 "data": {
#                     "id": appointment.id,
#                     "appointment_number": appointment.appointment_number,
#                     "appointment_date": appointment.appointment_date.isoformat(),
#                     "slot_id": appointment.slot_id,
#                     "patient_id": appointment.patient_id
#                 }
#             })
#
#         elif function_name == "cancelAppointment":
#             success, error = crud.cancel_appointment(db, function_args["appointment_id"])
#
#             if error:
#                 return json.dumps({"success": False, "message": error})
#
#             return json.dumps({"success": True, "message": "Appointment cancelled successfully"})
#
#         else:
#             return json.dumps({"success": False, "message": f"Unknown function: {function_name}"})
#
#     except Exception as e:
#         return json.dumps({"success": False, "message": f"Error: {str(e)}"})
#
#
# async def process_transcript_with_ai(transcript: str, session_id: str, db: Session, websocket: WebSocket,
#                                      voice_handler: VoiceHandler):
#     """Process transcript with AI and handle function calls"""
#     try:
#         await websocket.send_json({
#             "type": "status",
#             "message": "Processing..."
#         })
#
#         # Process with AI
#         result = process_chat_message(transcript, session_id)
#
#         # Handle function calls in a loop
#         while result["type"] == "function_call":
#             function_name = result["function_name"]
#             function_args = result["function_args"]
#
#             print(f"Calling function: {function_name} with args: {function_args}")
#
#             # Execute the function
#             function_result = execute_function(function_name, function_args, db)
#
#             # Send result back to AI and get next response
#             result = add_function_result(session_id, function_name, function_result)
#
#         # Get final text response
#         ai_response = result["content"]
#
#         await websocket.send_json({
#             "type": "response",
#             "text": ai_response
#         })
#
#         # Generate speech
#         await websocket.send_json({
#             "type": "status",
#             "message": "Speaking..."
#         })
#
#         audio_bytes = await voice_handler.speak_with_elevenlabs(ai_response)
#
#         if audio_bytes:
#             await websocket.send_bytes(audio_bytes)
#             await websocket.send_json({
#                 "type": "audio_complete",
#                 "message": "Audio sent"
#             })
#
#         await websocket.send_json({
#             "type": "status",
#             "message": "Listening..."
#         })
#
#     except Exception as e:
#         print(f"Error processing transcript: {e}")
#         import traceback
#         traceback.print_exc()
#         await websocket.send_json({
#             "type": "error",
#             "message": str(e)
#         })
#
#
# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     """WebSocket endpoint for real-time voice interaction"""
#     await websocket.accept()
#     session_id = f"voice_session_{id(websocket)}"
#     voice_handler = VoiceHandler(session_id)
#
#     # Get database session
#     db = next(get_db())
#
#     deepgram_ws = None
#     keepalive_task = None
#
#     try:
#         # Connect to Deepgram WebSocket with better configuration
#         deepgram_url = (
#             "wss://api.deepgram.com/v1/listen?"
#             "model=nova-2"
#             "&encoding=linear16"
#             "&sample_rate=16000"
#             "&channels=1"
#             "&interim_results=true"
#             "&punctuate=true"
#             "&vad_events=true"
#             "&endpointing=300"
#         )
#
#         print(f"Connecting to Deepgram...")
#         deepgram_ws = await websockets.connect(
#             deepgram_url,
#             additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
#             ping_interval=5,
#             ping_timeout=10
#         )
#
#         print("Connected to Deepgram successfully")
#
#         # Send welcome message with voice
#         await websocket.send_json({"type": "status", "message": "Voice assistant ready"})
#
#         # Speak welcome message
#         await websocket.send_json({
#             "type": "response",
#             "text": WELCOME_MESSAGE
#         })
#
#         welcome_audio = await voice_handler.speak_with_elevenlabs(WELCOME_MESSAGE)
#         if welcome_audio:
#             await websocket.send_bytes(welcome_audio)
#             await websocket.send_json({
#                 "type": "audio_complete",
#                 "message": "Welcome audio sent"
#             })
#
#         await websocket.send_json({"type": "status", "message": "Listening..."})
#
#         # Keepalive task to prevent Deepgram timeout
#         async def send_keepalive():
#             try:
#                 while True:
#                     await asyncio.sleep(3)
#                     if deepgram_ws and not deepgram_ws.closed:
#                         # Send empty keepalive
#                         await deepgram_ws.send(json.dumps({"type": "KeepAlive"}))
#             except Exception as e:
#                 print(f"Keepalive error: {e}")
#
#         keepalive_task = asyncio.create_task(send_keepalive())
#
#         # Handle messages concurrently
#         async def receive_from_client():
#             while True:
#                 try:
#                     message = await websocket.receive()
#
#                     if "bytes" in message:
#                         # Forward audio to Deepgram
#                         audio_size = len(message['bytes'])
#                         if audio_size > 0 and deepgram_ws and not deepgram_ws.closed:
#                             try:
#                                 await deepgram_ws.send(message["bytes"])
#                             except Exception as e:
#                                 print(f"Error sending to Deepgram: {e}")
#                                 break
#                     elif "text" in message:
#                         data = json.loads(message["text"])
#                         if data.get("type") == "stop":
#                             break
#
#                 except WebSocketDisconnect:
#                     print("Client disconnected")
#                     break
#                 except Exception as e:
#                     print(f"Error receiving from client: {e}")
#                     break
#
#         async def receive_from_deepgram():
#             while True:
#                 try:
#                     response = await asyncio.wait_for(deepgram_ws.recv(), timeout=10.0)
#                     data = json.loads(response)
#
#                     msg_type = data.get("type", "")
#
#                     if msg_type == "Results":
#                         channel = data.get("channel", {})
#                         alternatives = channel.get("alternatives", [])
#
#                         if alternatives:
#                             transcript = alternatives[0].get("transcript", "").strip()
#                             is_final = data.get("is_final", False)
#                             speech_final = data.get("speech_final", False)
#
#                             if transcript:
#                                 if is_final:
#                                     voice_handler.current_transcript += " " + transcript
#                                     voice_handler.current_transcript = voice_handler.current_transcript.strip()
#                                     voice_handler.last_speech_time = time.time()
#
#                                     await websocket.send_json({
#                                         "type": "interim_transcript",
#                                         "text": voice_handler.current_transcript
#                                     })
#
#                                 # Process when speech is final
#                                 if speech_final and voice_handler.current_transcript and not voice_handler.is_processing:
#                                     voice_handler.is_processing = True
#                                     final_transcript = voice_handler.current_transcript
#                                     voice_handler.current_transcript = ""
#
#                                     print(f"Processing voice transcript: '{final_transcript}'")
#
#                                     await websocket.send_json({
#                                         "type": "transcript",
#                                         "text": final_transcript
#                                     })
#
#                                     # Process with AI (handles function calls)
#                                     await process_transcript_with_ai(
#                                         final_transcript,
#                                         session_id,
#                                         db,
#                                         websocket,
#                                         voice_handler
#                                     )
#
#                                     voice_handler.is_processing = False
#
#                     elif msg_type == "SpeechStarted":
#                         await websocket.send_json({"type": "speech_started"})
#
#                     elif msg_type == "UtteranceEnd":
#                         if voice_handler.current_transcript and not voice_handler.is_processing:
#                             await asyncio.sleep(0.5)
#
#                             if voice_handler.current_transcript and not voice_handler.is_processing:
#                                 voice_handler.is_processing = True
#                                 final_transcript = voice_handler.current_transcript
#                                 voice_handler.current_transcript = ""
#
#                                 await websocket.send_json({
#                                     "type": "transcript",
#                                     "text": final_transcript
#                                 })
#
#                                 # Process with AI
#                                 await process_transcript_with_ai(
#                                     final_transcript,
#                                     session_id,
#                                     db,
#                                     websocket,
#                                     voice_handler
#                                 )
#
#                                 voice_handler.is_processing = False
#
#                 except asyncio.TimeoutError:
#                     print("Deepgram timeout, but continuing...")
#                     continue
#                 except websockets.exceptions.ConnectionClosed as e:
#                     print(f"Deepgram connection closed: {e}")
#                     break
#                 except Exception as e:
#                     print(f"Error receiving from Deepgram: {e}")
#                     import traceback
#                     traceback.print_exc()
#                     break
#
#         # Run both tasks concurrently
#         await asyncio.gather(
#             receive_from_client(),
#             receive_from_deepgram()
#         )
#
#     except Exception as e:
#         print(f"WebSocket error: {e}")
#         import traceback
#         traceback.print_exc()
#         await websocket.send_json({"type": "error", "message": str(e)})
#     finally:
#         if keepalive_task:
#             keepalive_task.cancel()
#         if deepgram_ws:
#             try:
#                 await deepgram_ws.close()
#             except:
#                 pass
#         db.close()


##third version
#
# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from sqlalchemy.orm import Session
# import asyncio
# import json
# import os
# import websockets
# import time
# from appointment_agent.app.database import get_db
# from appointment_agent.app.utils.voice_handler import VoiceHandler
# from appointment_agent.app.utils.ai_handler import process_chat_message, add_function_result
# from appointment_agent.app import crud
# from datetime import datetime
#
# router = APIRouter(prefix="/api/voice", tags=["voice"])
#
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
#
# # Welcome message for voice
# WELCOME_MESSAGE = "Hello! I'm your medical appointment assistant. I can help you book appointments, check available slots, or manage your existing appointments. How can I help you today?"
#
#
# @router.get("/test-keys")
# async def test_api_keys():
#     """Test if API keys are configured"""
#     return {
#         "deepgram": "configured" if DEEPGRAM_API_KEY else "missing",
#         "deepgram_length": len(DEEPGRAM_API_KEY) if DEEPGRAM_API_KEY else 0,
#         "elevenlabs": "configured" if os.getenv("ELEVENLABS_API_KEY") else "missing"
#     }
#
#
# def execute_function(function_name: str, function_args: dict, db: Session):
#     """Execute the requested function and return result"""
#     try:
#         if function_name == "getPatientDetails":
#             patient = crud.get_patient_by_mobile(db, function_args["mobile_number"])
#             if patient:
#                 return json.dumps({
#                     "success": True,
#                     "data": {
#                         "id": patient.id,
#                         "patient_name": patient.patient_name,
#                         "patient_mrn": patient.patient_mrn,
#                         "dob": str(patient.dob) if patient.dob else None,
#                         "gender": patient.gender,
#                         "mobile_number": patient.mobile_number,
#                         "email": patient.email
#                     }
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "Patient not found"})
#
#         elif function_name == "getDoctorDepartmentDetails":
#             doctors = crud.get_doctors_by_name_or_department(
#                 db,
#                 function_args.get("doctor_name"),
#                 function_args.get("specialization")
#             )
#             if doctors:
#                 return json.dumps({
#                     "success": True,
#                     "data": [
#                         {
#                             "id": doc.id,
#                             "doctor_name": doc.doctor_name,
#                             "specialization": doc.specialization
#                         }
#                         for doc in doctors
#                     ]
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "No doctors found"})
#
#         elif function_name == "getAvailableSlots":
#             date_str = function_args["appointment_date"]
#             date_obj = datetime.strptime(date_str, "%Y-%m-%d")
#
#             slots = crud.get_available_slots(
#                 db,
#                 function_args.get("doctor_id"),
#                 None,
#                 date_obj
#             )
#
#             if slots:
#                 return json.dumps({
#                     "success": True,
#                     "data": [
#                         {
#                             "id": slot.id,
#                             "doctor_id": slot.doctor_id,
#                             "doctor_name": slot.doctor.doctor_name if slot.doctor else None,
#                             "specialization": slot.doctor.specialization if slot.doctor else None,
#                             "start_time": slot.start_time.isoformat(),
#                             "end_time": slot.end_time.isoformat(),
#                             "status": slot.status
#                         }
#                         for slot in slots
#                     ]
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "No available slots found"})
#
#         elif function_name == "bookAnAppointment":
#             appointment_date = datetime.fromisoformat(function_args["appointment_date"])
#             appointment, error = crud.book_appointment(
#                 db,
#                 function_args["patient_id"],
#                 function_args["slot_id"],
#                 appointment_date
#             )
#
#             if error:
#                 return json.dumps({"success": False, "message": error})
#
#             return json.dumps({
#                 "success": True,
#                 "data": {
#                     "id": appointment.id,
#                     "appointment_number": appointment.appointment_number,
#                     "appointment_date": appointment.appointment_date.isoformat(),
#                     "slot_id": appointment.slot_id,
#                     "patient_id": appointment.patient_id
#                 }
#             })
#
#         elif function_name == "cancelAppointment":
#             success, error = crud.cancel_appointment(db, function_args["appointment_id"])
#
#             if error:
#                 return json.dumps({"success": False, "message": error})
#
#             return json.dumps({"success": True, "message": "Appointment cancelled successfully"})
#
#         else:
#             return json.dumps({"success": False, "message": f"Unknown function: {function_name}"})
#
#     except Exception as e:
#         return json.dumps({"success": False, "message": f"Error: {str(e)}"})
#
#
# async def process_transcript_with_ai(transcript: str, session_id: str, db: Session, websocket: WebSocket,
#                                      voice_handler: VoiceHandler):
#     """Process transcript with AI and handle function calls"""
#     try:
#         await websocket.send_json({
#             "type": "status",
#             "message": "Processing..."
#         })
#
#         # Process with AI
#         result = process_chat_message(transcript, session_id)
#
#         # Handle function calls in a loop
#         while result["type"] == "function_call":
#             function_name = result["function_name"]
#             function_args = result["function_args"]
#
#             print(f"Calling function: {function_name} with args: {function_args}")
#
#             # Execute the function
#             function_result = execute_function(function_name, function_args, db)
#
#             # Send result back to AI and get next response
#             result = add_function_result(session_id, function_name, function_result)
#
#         # Get final text response
#         ai_response = result["content"]
#
#         await websocket.send_json({
#             "type": "response",
#             "text": ai_response
#         })
#
#         # Generate speech
#         await websocket.send_json({
#             "type": "status",
#             "message": "Speaking..."
#         })
#
#         audio_bytes = await voice_handler.speak_with_elevenlabs(ai_response)
#
#         if audio_bytes:
#             await websocket.send_bytes(audio_bytes)
#             await websocket.send_json({
#                 "type": "audio_complete",
#                 "message": "Audio sent"
#             })
#
#         await websocket.send_json({
#             "type": "status",
#             "message": "Listening..."
#         })
#
#     except Exception as e:
#         print(f"Error processing transcript: {e}")
#         import traceback
#         traceback.print_exc()
#         await websocket.send_json({
#             "type": "error",
#             "message": str(e)
#         })
#
#
# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     """WebSocket endpoint for real-time voice interaction"""
#     await websocket.accept()
#     session_id = f"voice_session_{id(websocket)}"
#     voice_handler = VoiceHandler(session_id)
#
#     # Get database session
#     db = next(get_db())
#
#     deepgram_ws = None
#     keepalive_task = None
#
#     try:
#         # Connect to Deepgram WebSocket with better configuration
#         deepgram_url = (
#             "wss://api.deepgram.com/v1/listen?"
#             "model=nova-2"
#             "&encoding=linear16"
#             "&sample_rate=16000"
#             "&channels=1"
#             "&interim_results=true"
#             "&punctuate=true"
#             "&vad_events=true"
#             "&endpointing=300"
#         )
#
#         print(f"Connecting to Deepgram...")
#         deepgram_ws = await websockets.connect(
#             deepgram_url,
#             additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
#             ping_interval=5,
#             ping_timeout=10
#         )
#
#         print("Connected to Deepgram successfully")
#
#         # Send welcome message with voice
#         await websocket.send_json({"type": "status", "message": "Voice assistant ready"})
#
#         # Speak welcome message
#         await websocket.send_json({
#             "type": "response",
#             "text": WELCOME_MESSAGE
#         })
#
#         welcome_audio = await voice_handler.speak_with_elevenlabs(WELCOME_MESSAGE)
#         if welcome_audio:
#             await websocket.send_bytes(welcome_audio)
#             await websocket.send_json({
#                 "type": "audio_complete",
#                 "message": "Welcome audio sent"
#             })
#
#         await websocket.send_json({"type": "status", "message": "Listening..."})
#
#         # Keepalive task to prevent Deepgram timeout
#         async def send_keepalive():
#             try:
#                 while True:
#                     await asyncio.sleep(3)
#                     if deepgram_ws and not deepgram_ws.closed:
#                         # Send empty keepalive
#                         await deepgram_ws.send(json.dumps({"type": "KeepAlive"}))
#             except Exception as e:
#                 print(f"Keepalive error: {e}")
#
#         keepalive_task = asyncio.create_task(send_keepalive())
#
#         # Handle messages concurrently
#         async def receive_from_client():
#             audio_chunk_count = 0
#             while True:
#                 try:
#                     message = await websocket.receive()
#
#                     if "bytes" in message:
#                         # Forward audio to Deepgram
#                         audio_size = len(message['bytes'])
#                         if audio_size > 0 and deepgram_ws and not deepgram_ws.closed:
#                             try:
#                                 await deepgram_ws.send(message["bytes"])
#                                 audio_chunk_count += 1
#                                 if audio_chunk_count % 50 == 0:  # Log every 50 chunks
#                                     print(f"Sent {audio_chunk_count} audio chunks to Deepgram")
#                             except Exception as e:
#                                 print(f"Error sending to Deepgram: {e}")
#                                 break
#                     elif "text" in message:
#                         data = json.loads(message["text"])
#                         print(f"Received text message: {data}")
#                         if data.get("type") == "stop":
#                             break
#
#                 except WebSocketDisconnect:
#                     print("Client disconnected")
#                     break
#                 except Exception as e:
#                     print(f"Error receiving from client: {e}")
#                     break
#
#         async def receive_from_deepgram():
#             result_count = 0
#             while True:
#                 try:
#                     response = await asyncio.wait_for(deepgram_ws.recv(), timeout=10.0)
#                     data = json.loads(response)
#
#                     msg_type = data.get("type", "")
#
#                     if msg_type == "Results":
#                         result_count += 1
#                         if result_count % 10 == 0:
#                             print(f"Received {result_count} results from Deepgram")
#
#                         channel = data.get("channel", {})
#                         alternatives = channel.get("alternatives", [])
#
#                         if alternatives:
#                             transcript = alternatives[0].get("transcript", "").strip()
#                             is_final = data.get("is_final", False)
#                             speech_final = data.get("speech_final", False)
#
#                             if transcript:
#                                 print(f"Transcript: '{transcript}' (final={is_final}, speech_final={speech_final})")
#
#                                 if is_final:
#                                     voice_handler.current_transcript += " " + transcript
#                                     voice_handler.current_transcript = voice_handler.current_transcript.strip()
#                                     voice_handler.last_speech_time = time.time()
#
#                                     await websocket.send_json({
#                                         "type": "interim_transcript",
#                                         "text": voice_handler.current_transcript
#                                     })
#
#                                 # Process when speech is final
#                                 if speech_final and voice_handler.current_transcript and not voice_handler.is_processing:
#                                     voice_handler.is_processing = True
#                                     final_transcript = voice_handler.current_transcript
#                                     voice_handler.current_transcript = ""
#
#                                     print(f"Processing voice transcript: '{final_transcript}'")
#
#                                     await websocket.send_json({
#                                         "type": "transcript",
#                                         "text": final_transcript
#                                     })
#
#                                     # Process with AI (handles function calls)
#                                     await process_transcript_with_ai(
#                                         final_transcript,
#                                         session_id,
#                                         db,
#                                         websocket,
#                                         voice_handler
#                                     )
#
#                                     voice_handler.is_processing = False
#
#                     elif msg_type == "SpeechStarted":
#                         print("Speech started detected")
#                         await websocket.send_json({"type": "speech_started"})
#
#                     elif msg_type == "UtteranceEnd":
#                         print("Utterance end detected")
#                         if voice_handler.current_transcript and not voice_handler.is_processing:
#                             await asyncio.sleep(0.5)
#
#                             if voice_handler.current_transcript and not voice_handler.is_processing:
#                                 voice_handler.is_processing = True
#                                 final_transcript = voice_handler.current_transcript
#                                 voice_handler.current_transcript = ""
#
#                                 print(f"Processing from utterance end: '{final_transcript}'")
#
#                                 await websocket.send_json({
#                                     "type": "transcript",
#                                     "text": final_transcript
#                                 })
#
#                                 # Process with AI
#                                 await process_transcript_with_ai(
#                                     final_transcript,
#                                     session_id,
#                                     db,
#                                     websocket,
#                                     voice_handler
#                                 )
#
#                                 voice_handler.is_processing = False
#
#                 except asyncio.TimeoutError:
#                     # This is normal if no speech - just continue
#                     continue
#                 except websockets.exceptions.ConnectionClosed as e:
#                     print(f"Deepgram connection closed: {e}")
#                     break
#                 except Exception as e:
#                     print(f"Error receiving from Deepgram: {e}")
#                     import traceback
#                     traceback.print_exc()
#                     break
#
#         # Run both tasks concurrently
#         await asyncio.gather(
#             receive_from_client(),
#             receive_from_deepgram()
#         )
#
#     except Exception as e:
#         print(f"WebSocket error: {e}")
#         import traceback
#         traceback.print_exc()
#         await websocket.send_json({"type": "error", "message": str(e)})
#     finally:
#         if keepalive_task:
#             keepalive_task.cancel()
#         if deepgram_ws:
#             try:
#                 await deepgram_ws.close()
#             except:
#                 pass
#         db.close()


##fourth version

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import asyncio
import json
import os
import websockets
import time
from appointment_agent.app.database import get_db
from appointment_agent.app.utils.voice_handler import VoiceHandler
from appointment_agent.app.utils.ai_handler import process_chat_message, add_function_result
from appointment_agent.app import crud
from datetime import datetime

router = APIRouter(prefix="/api/voice", tags=["voice"])

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Welcome message for voice
WELCOME_MESSAGE = "Hello! I'm your medical appointment assistant. I can help you book appointments, check available slots, or manage your existing appointments. How can I help you today?"


@router.get("/test-keys")
async def test_api_keys():
    """Test if API keys are configured"""
    return {
        "deepgram": "configured" if DEEPGRAM_API_KEY else "missing",
        "deepgram_length": len(DEEPGRAM_API_KEY) if DEEPGRAM_API_KEY else 0,
        "deepgram_prefix": DEEPGRAM_API_KEY[:10] if DEEPGRAM_API_KEY else "none",
        "elevenlabs": "configured" if os.getenv("ELEVENLABS_API_KEY") else "missing"
    }


@router.get("/test-deepgram")
async def test_deepgram_connection():
    """Test Deepgram WebSocket connection"""
    try:
        deepgram_url = (
            "wss://api.deepgram.com/v1/listen?"
            "model=nova-2"
            "&encoding=linear16"
            "&sample_rate=16000"
        )

        async with websockets.connect(
                deepgram_url,
                additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
                ping_interval=5,
                ping_timeout=10
        ) as ws:
            # Send a test message
            await ws.send(json.dumps({"type": "KeepAlive"}))

            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)

            return {
                "status": "success",
                "message": "Deepgram connection works!",
                "response": response
            }
    except asyncio.TimeoutError:
        return {
            "status": "error",
            "message": "Deepgram timeout - API key might be invalid or no credits"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def execute_function(function_name: str, function_args: dict, db: Session):
    """Execute the requested function and return result"""
    try:
        if function_name == "getPatientDetails":
            patient = crud.get_patient_by_mobile(db, function_args["mobile_number"])
            if patient:
                return json.dumps({
                    "success": True,
                    "data": {
                        "id": patient.id,
                        "patient_name": patient.patient_name,
                        "patient_mrn": patient.patient_mrn,
                        "dob": str(patient.dob) if patient.dob else None,
                        "gender": patient.gender,
                        "mobile_number": patient.mobile_number,
                        "email": patient.email
                    }
                })
            else:
                return json.dumps({"success": False, "message": "Patient not found"})

        elif function_name == "getDoctorDepartmentDetails":
            doctors = crud.get_doctors_by_name_or_department(
                db,
                function_args.get("doctor_name"),
                function_args.get("specialization")
            )
            if doctors:
                return json.dumps({
                    "success": True,
                    "data": [
                        {
                            "id": doc.id,
                            "doctor_name": doc.doctor_name,
                            "specialization": doc.specialization
                        }
                        for doc in doctors
                    ]
                })
            else:
                return json.dumps({"success": False, "message": "No doctors found"})

        elif function_name == "getAvailableSlots":
            date_str = function_args["appointment_date"]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")

            slots = crud.get_available_slots(
                db,
                function_args.get("doctor_id"),
                None,
                date_obj
            )

            if slots:
                return json.dumps({
                    "success": True,
                    "data": [
                        {
                            "id": slot.id,
                            "doctor_id": slot.doctor_id,
                            "doctor_name": slot.doctor.doctor_name if slot.doctor else None,
                            "specialization": slot.doctor.specialization if slot.doctor else None,
                            "start_time": slot.start_time.isoformat(),
                            "end_time": slot.end_time.isoformat(),
                            "status": slot.status
                        }
                        for slot in slots
                    ]
                })
            else:
                return json.dumps({"success": False, "message": "No available slots found"})

        elif function_name == "bookAnAppointment":
            appointment_date = datetime.fromisoformat(function_args["appointment_date"])
            appointment, error = crud.book_appointment(
                db,
                function_args["patient_id"],
                function_args["slot_id"],
                appointment_date
            )

            if error:
                return json.dumps({"success": False, "message": error})

            return json.dumps({
                "success": True,
                "data": {
                    "id": appointment.id,
                    "appointment_number": appointment.appointment_number,
                    "appointment_date": appointment.appointment_date.isoformat(),
                    "slot_id": appointment.slot_id,
                    "patient_id": appointment.patient_id
                }
            })

        elif function_name == "cancelAppointment":
            success, error = crud.cancel_appointment(db, function_args["appointment_id"])

            if error:
                return json.dumps({"success": False, "message": error})

            return json.dumps({"success": True, "message": "Appointment cancelled successfully"})

        else:
            return json.dumps({"success": False, "message": f"Unknown function: {function_name}"})

    except Exception as e:
        return json.dumps({"success": False, "message": f"Error: {str(e)}"})


async def process_transcript_with_ai(transcript: str, session_id: str, db: Session, websocket: WebSocket,
                                     voice_handler: VoiceHandler):
    """Process transcript with AI and handle function calls"""
    try:
        await websocket.send_json({
            "type": "status",
            "message": "Processing..."
        })

        # Process with AI
        result = process_chat_message(transcript, session_id)

        # Handle function calls in a loop
        while result["type"] == "function_call":
            function_name = result["function_name"]
            function_args = result["function_args"]

            print(f"Calling function: {function_name} with args: {function_args}")

            # Execute the function
            function_result = execute_function(function_name, function_args, db)

            # Send result back to AI and get next response
            result = add_function_result(session_id, function_name, function_result)

        # Get final text response
        ai_response = result["content"]

        await websocket.send_json({
            "type": "response",
            "text": ai_response
        })

        # Generate speech
        await websocket.send_json({
            "type": "status",
            "message": "Speaking..."
        })

        audio_bytes = await voice_handler.speak_with_elevenlabs(ai_response)

        if audio_bytes:
            await websocket.send_bytes(audio_bytes)
            await websocket.send_json({
                "type": "audio_complete",
                "message": "Audio sent"
            })

        await websocket.send_json({
            "type": "status",
            "message": "Listening..."
        })

    except Exception as e:
        print(f"Error processing transcript: {e}")
        import traceback
        traceback.print_exc()
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time voice interaction"""
    await websocket.accept()
    session_id = f"voice_session_{id(websocket)}"
    voice_handler = VoiceHandler(session_id)

    # Get database session
    db = next(get_db())

    deepgram_ws = None
    keepalive_task = None

    try:
        # Connect to Deepgram WebSocket with better configuration
        deepgram_url = (
            "wss://api.deepgram.com/v1/listen?"
            "model=nova-2"
            "&encoding=linear16"
            "&sample_rate=16000"
            "&channels=1"
            "&interim_results=true"
            "&punctuate=true"
            "&vad_events=true"
            "&endpointing=300"
        )

        print(f"Connecting to Deepgram...")
        deepgram_ws = await websockets.connect(
            deepgram_url,
            additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
            ping_interval=5,
            ping_timeout=10
        )

        print("Connected to Deepgram successfully")

        # Send welcome message with voice
        await websocket.send_json({"type": "status", "message": "Voice assistant ready"})

        # Speak welcome message
        await websocket.send_json({
            "type": "response",
            "text": WELCOME_MESSAGE
        })

        welcome_audio = await voice_handler.speak_with_elevenlabs(WELCOME_MESSAGE)
        if welcome_audio:
            await websocket.send_bytes(welcome_audio)
            await websocket.send_json({
                "type": "audio_complete",
                "message": "Welcome audio sent"
            })

        await websocket.send_json({"type": "status", "message": "Listening..."})

        # Keepalive task to prevent Deepgram timeout
        async def send_keepalive():
            try:
                while True:
                    await asyncio.sleep(3)
                    if deepgram_ws:
                        try:
                            # Send empty keepalive
                            await deepgram_ws.send(json.dumps({"type": "KeepAlive"}))
                        except:
                            break
            except Exception as e:
                print(f"Keepalive error: {e}")

        keepalive_task = asyncio.create_task(send_keepalive())

        # Handle messages concurrently
        async def receive_from_client():
            audio_chunk_count = 0
            while True:
                try:
                    message = await websocket.receive()

                    if "bytes" in message:
                        # Forward audio to Deepgram
                        audio_size = len(message['bytes'])
                        if audio_size > 0 and deepgram_ws:
                            try:
                                await deepgram_ws.send(message["bytes"])
                                audio_chunk_count += 1
                                if audio_chunk_count % 50 == 0:  # Log every 50 chunks
                                    print(f"Sent {audio_chunk_count} audio chunks to Deepgram")
                            except Exception as e:
                                print(f"Error sending to Deepgram: {e}")
                                break
                    elif "text" in message:
                        data = json.loads(message["text"])
                        print(f"Received text message: {data}")
                        if data.get("type") == "stop":
                            break

                except WebSocketDisconnect:
                    print("Client disconnected")
                    break
                except Exception as e:
                    print(f"Error receiving from client: {e}")
                    break

        async def receive_from_deepgram():
            result_count = 0
            while True:
                try:
                    response = await asyncio.wait_for(deepgram_ws.recv(), timeout=10.0)
                    data = json.loads(response)

                    msg_type = data.get("type", "")

                    if msg_type == "Results":
                        result_count += 1
                        if result_count % 10 == 0:
                            print(f"Received {result_count} results from Deepgram")

                        channel = data.get("channel", {})
                        alternatives = channel.get("alternatives", [])

                        if alternatives:
                            transcript = alternatives[0].get("transcript", "").strip()
                            is_final = data.get("is_final", False)
                            speech_final = data.get("speech_final", False)

                            if transcript:
                                print(f"Transcript: '{transcript}' (final={is_final}, speech_final={speech_final})")

                                if is_final:
                                    voice_handler.current_transcript += " " + transcript
                                    voice_handler.current_transcript = voice_handler.current_transcript.strip()
                                    voice_handler.last_speech_time = time.time()

                                    await websocket.send_json({
                                        "type": "interim_transcript",
                                        "text": voice_handler.current_transcript
                                    })

                                # Process when speech is final
                                if speech_final and voice_handler.current_transcript and not voice_handler.is_processing:
                                    voice_handler.is_processing = True
                                    final_transcript = voice_handler.current_transcript
                                    voice_handler.current_transcript = ""

                                    print(f"Processing voice transcript: '{final_transcript}'")

                                    await websocket.send_json({
                                        "type": "transcript",
                                        "text": final_transcript
                                    })

                                    # Process with AI (handles function calls)
                                    await process_transcript_with_ai(
                                        final_transcript,
                                        session_id,
                                        db,
                                        websocket,
                                        voice_handler
                                    )

                                    voice_handler.is_processing = False

                    elif msg_type == "SpeechStarted":
                        print("Speech started detected")
                        await websocket.send_json({"type": "speech_started"})

                    elif msg_type == "UtteranceEnd":
                        print("Utterance end detected")
                        if voice_handler.current_transcript and not voice_handler.is_processing:
                            await asyncio.sleep(0.5)

                            if voice_handler.current_transcript and not voice_handler.is_processing:
                                voice_handler.is_processing = True
                                final_transcript = voice_handler.current_transcript
                                voice_handler.current_transcript = ""

                                print(f"Processing from utterance end: '{final_transcript}'")

                                await websocket.send_json({
                                    "type": "transcript",
                                    "text": final_transcript
                                })

                                # Process with AI
                                await process_transcript_with_ai(
                                    final_transcript,
                                    session_id,
                                    db,
                                    websocket,
                                    voice_handler
                                )

                                voice_handler.is_processing = False

                except asyncio.TimeoutError:
                    # This is normal if no speech - just continue
                    continue
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"Deepgram connection closed: {e}")
                    break
                except Exception as e:
                    print(f"Error receiving from Deepgram: {e}")
                    import traceback
                    traceback.print_exc()
                    break

        # Run both tasks concurrently
        await asyncio.gather(
            receive_from_client(),
            receive_from_deepgram()
        )

    except Exception as e:
        print(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        if keepalive_task:
            keepalive_task.cancel()
        if deepgram_ws:
            try:
                await deepgram_ws.close()
            except:
                pass
        db.close()