# from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
# from sqlalchemy.orm import Session
# import json
# import asyncio
# import websockets
# import time
# from patient_fao_agent.app.database import get_db
# from patient_fao_agent.app.services.voice_service import VoiceService
# from patient_fao_agent.app.services.education_service import EducationService
# from patient_fao_agent.app.services.patient_service import PatientService
# from patient_fao_agent.app.config import settings
#
# router = APIRouter()
#
#
# class VoiceAgent:
#     def __init__(self, patient_id: int, db: Session):
#         self.patient_id = patient_id
#         self.db = db
#         self.voice_service = VoiceService()
#         self.education_service = EducationService(db)
#         self.patient_service = PatientService(db)
#         self.current_transcript = ""
#         self.last_speech_time = time.time()
#         self.is_processing = False
#         self.patient = None
#
#     async def initialize(self):
#         """Initialize patient data"""
#         self.patient = await self.patient_service.get_patient_by_id(self.patient_id)
#         return f"Hello {self.patient.patient_name}! I can help explain your medical documents and answer health questions. How can I assist you today?"
#
#
# @router.websocket("/ws/voice/{patient_id}")
# async def voice_websocket(websocket: WebSocket, patient_id: int):
#     """WebSocket endpoint for voice interaction"""
#     await websocket.accept()
#
#     # Get DB session
#     db = next(get_db())
#     agent = VoiceAgent(patient_id, db)
#     deepgram_ws = None
#
#     try:
#         # Initialize and send welcome message
#         welcome_message = await agent.initialize()
#
#         await websocket.send_json({
#             "type": "status",
#             "message": "Connected and ready"
#         })
#
#         # Send welcome message as text and audio
#         await websocket.send_json({
#             "type": "response",
#             "text": welcome_message
#         })
#
#         # Generate welcome audio
#         welcome_audio = await agent.voice_service.text_to_speech(welcome_message)
#         if welcome_audio:
#             await websocket.send_bytes(welcome_audio)
#             await websocket.send_json({
#                 "type": "audio_complete",
#                 "message": "Welcome audio sent"
#             })
#
#         await websocket.send_json({
#             "type": "status",
#             "message": "Listening..."
#         })
#
#         # Connect to Deepgram
#         deepgram_url = "wss://api.deepgram.com/v1/listen?model=nova-2&interim_results=true&punctuate=true&vad_events=true"
#         deepgram_ws = await websockets.connect(
#             deepgram_url,
#             extra_headers={"Authorization": f"Token {settings.DEEPGRAM_API_KEY}"}
#         )
#
#         print(f"[Voice] Connected to Deepgram for patient {patient_id}")
#
#         async def receive_from_client():
#             """Receive audio from client"""
#             while True:
#                 try:
#                     message = await websocket.receive()
#
#                     if "bytes" in message:
#                         audio_size = len(message['bytes'])
#                         if audio_size > 0:
#                             await deepgram_ws.send(message["bytes"])
#                     elif "text" in message:
#                         data = json.loads(message["text"])
#                         if data.get("type") == "stop":
#                             break
#
#                 except WebSocketDisconnect:
#                     print("[Voice] Client disconnected")
#                     break
#                 except Exception as e:
#                     print(f"[Voice] Error receiving from client: {e}")
#                     break
#
#         async def receive_from_deepgram():
#             """Process Deepgram transcriptions"""
#             while True:
#                 try:
#                     response = await deepgram_ws.recv()
#                     data = json.loads(response)
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
#                                     agent.current_transcript += " " + transcript
#                                     agent.current_transcript = agent.current_transcript.strip()
#                                     agent.last_speech_time = time.time()
#
#                                     # Send interim transcript
#                                     await websocket.send_json({
#                                         "type": "interim_transcript",
#                                         "text": agent.current_transcript
#                                     })
#
#                                 # Process when speech is final
#                                 if speech_final and agent.current_transcript and not agent.is_processing:
#                                     await process_user_speech(agent, websocket)
#
#                     elif msg_type == "UtteranceEnd":
#                         print("[Voice] Utterance end detected")
#                         if agent.current_transcript and not agent.is_processing:
#                             await asyncio.sleep(0.5)
#                             if agent.current_transcript and not agent.is_processing:
#                                 await process_user_speech(agent, websocket)
#
#                     elif msg_type == "SpeechStarted":
#                         await websocket.send_json({"type": "speech_started"})
#
#                 except websockets.exceptions.ConnectionClosed:
#                     print("[Voice] Deepgram connection closed")
#                     break
#                 except Exception as e:
#                     print(f"[Voice] Error from Deepgram: {e}")
#                     break
#
#         await asyncio.gather(
#             receive_from_client(),
#             receive_from_deepgram()
#         )
#
#     except Exception as e:
#         print(f"[Voice] WebSocket error: {e}")
#         await websocket.send_json({"type": "error", "message": str(e)})
#     finally:
#         if deepgram_ws:
#             await deepgram_ws.close()
#         db.close()
#
#
# async def process_user_speech(agent: VoiceAgent, websocket: WebSocket):
#     """Process user's speech and generate response"""
#     agent.is_processing = True
#     final_transcript = agent.current_transcript
#     agent.current_transcript = ""
#
#     print(f"[Voice] Processing: '{final_transcript}'")
#
#     try:
#         # Send final transcript
#         await websocket.send_json({
#             "type": "transcript",
#             "text": final_transcript
#         })
#
#         # Show thinking status
#         await websocket.send_json({
#             "type": "status",
#             "message": "Thinking..."
#         })
#
#         # Use existing education service to process query
#         response = await agent.education_service.handle_query(
#             patient_id=agent.patient_id,
#             query=final_transcript,
#             session_id=None
#         )
#
#         # Send text response
#         await websocket.send_json({
#             "type": "response",
#             "text": response.response
#         })
#
#         # Generate speech
#         await websocket.send_json({
#             "type": "status",
#             "message": "Speaking..."
#         })
#
#         audio_bytes = await agent.voice_service.text_to_speech(response.response)
#
#         if audio_bytes:
#             await websocket.send_bytes(audio_bytes)
#             await websocket.send_json({
#                 "type": "audio_complete",
#                 "message": "Audio sent"
#             })
#
#         # Ready for next input
#         await websocket.send_json({
#             "type": "status",
#             "message": "Listening..."
#         })
#
#     except Exception as e:
#         print(f"[Voice] Processing error: {e}")
#         error_msg = "Sorry, I encountered an error processing your request."
#
#         await websocket.send_json({
#             "type": "response",
#             "text": error_msg
#         })
#
#         error_audio = await agent.voice_service.text_to_speech(error_msg)
#         if error_audio:
#             await websocket.send_bytes(error_audio)
#             await websocket.send_json({
#                 "type": "audio_complete",
#                 "message": "Error audio sent"
#             })
#
#         await websocket.send_json({
#             "type": "status",
#             "message": "Listening..."
#         })
#
#     finally:
#         agent.is_processing = False


from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json
import asyncio
import websockets
import time
from patient_fao_agent.app.database import get_db
from patient_fao_agent.app.services.voice_service import VoiceService
from patient_fao_agent.app.services.education_service import EducationService
from patient_fao_agent.app.services.patient_service import PatientService
from patient_fao_agent.app.config import settings

router = APIRouter()


class VoiceAgent:
    def __init__(self, patient_id: int, db: Session):
        self.patient_id = patient_id
        self.db = db
        self.voice_service = VoiceService()
        self.education_service = EducationService(db)
        self.patient_service = PatientService(db)
        self.current_transcript = ""
        self.last_speech_time = time.time()
        self.is_processing = False
        self.patient = None

    async def initialize(self):
        """Initialize patient data"""
        self.patient = await self.patient_service.get_patient_by_id(self.patient_id)
        return f"Hello {self.patient.patient_name}! I can help explain your medical documents and answer health questions. How can I assist you today?"


@router.websocket("/ws/voice/{patient_id}")
async def voice_websocket(websocket: WebSocket, patient_id: int):
    """WebSocket endpoint for voice interaction"""
    await websocket.accept()

    # Get DB session
    db = next(get_db())
    agent = VoiceAgent(patient_id, db)
    deepgram_ws = None

    try:
        # Initialize and send welcome message
        welcome_message = await agent.initialize()

        await websocket.send_json({
            "type": "status",
            "message": "Connected and ready"
        })

        # Send welcome message as text and audio
        await websocket.send_json({
            "type": "response",
            "text": welcome_message
        })

        # Generate welcome audio
        welcome_audio = await agent.voice_service.text_to_speech(welcome_message)
        if welcome_audio:
            await websocket.send_bytes(welcome_audio)
            await websocket.send_json({
                "type": "audio_complete",
                "message": "Welcome audio sent"
            })

        await websocket.send_json({
            "type": "status",
            "message": "Listening..."
        })

        # Connect to Deepgram
        deepgram_url = "wss://api.deepgram.com/v1/listen?model=nova-2&interim_results=true&punctuate=true&vad_events=true"
        deepgram_ws = await websockets.connect(
            deepgram_url,
            additional_headers={"Authorization": f"Token {settings.DEEPGRAM_API_KEY}"}
        )

        print(f"[Voice] Connected to Deepgram for patient {patient_id}")

        async def receive_from_client():
            """Receive audio from client"""
            while True:
                try:
                    message = await websocket.receive()

                    if "bytes" in message:
                        audio_size = len(message['bytes'])
                        if audio_size > 0:
                            await deepgram_ws.send(message["bytes"])
                    elif "text" in message:
                        data = json.loads(message["text"])
                        if data.get("type") == "stop":
                            break

                except WebSocketDisconnect:
                    print("[Voice] Client disconnected")
                    break
                except Exception as e:
                    print(f"[Voice] Error receiving from client: {e}")
                    break

        async def receive_from_deepgram():
            """Process Deepgram transcriptions"""
            while True:
                try:
                    response = await deepgram_ws.recv()
                    data = json.loads(response)
                    msg_type = data.get("type", "")

                    if msg_type == "Results":
                        channel = data.get("channel", {})
                        alternatives = channel.get("alternatives", [])

                        if alternatives:
                            transcript = alternatives[0].get("transcript", "").strip()
                            is_final = data.get("is_final", False)
                            speech_final = data.get("speech_final", False)

                            if transcript:
                                if is_final:
                                    agent.current_transcript += " " + transcript
                                    agent.current_transcript = agent.current_transcript.strip()
                                    agent.last_speech_time = time.time()

                                    # Send interim transcript
                                    await websocket.send_json({
                                        "type": "interim_transcript",
                                        "text": agent.current_transcript
                                    })

                                # Process when speech is final
                                if speech_final and agent.current_transcript and not agent.is_processing:
                                    await process_user_speech(agent, websocket)

                    elif msg_type == "UtteranceEnd":
                        print("[Voice] Utterance end detected")
                        if agent.current_transcript and not agent.is_processing:
                            await asyncio.sleep(0.5)
                            if agent.current_transcript and not agent.is_processing:
                                await process_user_speech(agent, websocket)

                    elif msg_type == "SpeechStarted":
                        await websocket.send_json({"type": "speech_started"})

                except websockets.exceptions.ConnectionClosed:
                    print("[Voice] Deepgram connection closed")
                    break
                except Exception as e:
                    print(f"[Voice] Error from Deepgram: {e}")
                    break

        await asyncio.gather(
            receive_from_client(),
            receive_from_deepgram()
        )

    except Exception as e:
        print(f"[Voice] WebSocket error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        if deepgram_ws:
            await deepgram_ws.close()
        db.close()


async def process_user_speech(agent: VoiceAgent, websocket: WebSocket):
    """Process user's speech and generate response"""
    agent.is_processing = True
    final_transcript = agent.current_transcript
    agent.current_transcript = ""

    print(f"[Voice] Processing: '{final_transcript}'")

    try:
        # Send final transcript
        await websocket.send_json({
            "type": "transcript",
            "text": final_transcript
        })

        # Show thinking status
        await websocket.send_json({
            "type": "status",
            "message": "Thinking..."
        })

        # Use existing education service to process query
        response = await agent.education_service.handle_query(
            patient_id=agent.patient_id,
            query=final_transcript,
            session_id=None
        )

        # Send text response
        await websocket.send_json({
            "type": "response",
            "text": response.response
        })

        # Generate speech
        await websocket.send_json({
            "type": "status",
            "message": "Speaking..."
        })

        audio_bytes = await agent.voice_service.text_to_speech(response.response)

        if audio_bytes:
            await websocket.send_bytes(audio_bytes)
            await websocket.send_json({
                "type": "audio_complete",
                "message": "Audio sent"
            })

        # Ready for next input
        await websocket.send_json({
            "type": "status",
            "message": "Listening..."
        })

    except Exception as e:
        print(f"[Voice] Processing error: {e}")
        error_msg = "Sorry, I encountered an error processing your request."

        await websocket.send_json({
            "type": "response",
            "text": error_msg
        })

        error_audio = await agent.voice_service.text_to_speech(error_msg)
        if error_audio:
            await websocket.send_bytes(error_audio)
            await websocket.send_json({
                "type": "audio_complete",
                "message": "Error audio sent"
            })

        await websocket.send_json({
            "type": "status",
            "message": "Listening..."
        })

    finally:
        agent.is_processing = False