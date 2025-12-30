# """
# Voice Agent Backend with FastAPI
# Handles: Deepgram STT, OpenAI GPT, ElevenLabs TTS
# """
#
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# import asyncio
# import json
# import os
# from dotenv import load_dotenv
# import httpx
# import websockets
# from typing import Optional
#
# load_dotenv()
#
# app = FastAPI()
#
# # Enable CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Configuration
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
#
# # Store conversation history per session
# conversations = {}
#
#
# class VoiceAgent:
#     def __init__(self, session_id: str):
#         self.session_id = session_id
#         self.conversation_history = []
#
#     async def transcribe_with_deepgram(self, audio_data: bytes) -> Optional[str]:
#         """Send audio to Deepgram and get transcription"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     "https://api.deepgram.com/v1/listen",
#                     headers={
#                         "Authorization": f"Token {DEEPGRAM_API_KEY}",
#                         "Content-Type": "audio/wav"
#                     },
#                     content=audio_data,
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
#                     return transcript.strip()
#                 return None
#         except Exception as e:
#             print(f"Deepgram error: {e}")
#             return None
#
#     async def process_with_gpt(self, user_message: str) -> str:
#         """Process user message with GPT"""
#         try:
#             # Add user message to history
#             self.conversation_history.append({
#                 "role": "user",
#                 "content": user_message
#             })
#
#             # Keep only last 10 messages for context
#             if len(self.conversation_history) > 10:
#                 self.conversation_history = self.conversation_history[-10:]
#
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     "https://api.openai.com/v1/chat/completions",
#                     headers={
#                         "Authorization": f"Bearer {OPENAI_API_KEY}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": "gpt-4o-mini",
#                         "messages": [
#                             {
#                                 "role": "system",
#                                 "content": "You are a helpful voice assistant. Keep responses concise and conversational, under 100 words."
#                             },
#                             *self.conversation_history
#                         ],
#                         "max_tokens": 200,
#                         "temperature": 0.7
#                     },
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     assistant_message = result["choices"][0]["message"]["content"]
#
#                     # Add assistant response to history
#                     self.conversation_history.append({
#                         "role": "assistant",
#                         "content": assistant_message
#                     })
#
#                     return assistant_message
#                 return "Sorry, I couldn't process that."
#         except Exception as e:
#             print(f"GPT error: {e}")
#             return "Sorry, I encountered an error."
#
#     async def speak_with_elevenlabs(self, text: str) -> bytes:
#         """Convert text to speech with ElevenLabs"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
#                     headers={
#                         "xi-api-key": ELEVENLABS_API_KEY,
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "text": text,
#                         "model_id": "eleven_monolingual_v1",
#                         "voice_settings": {
#                             "stability": 0.5,
#                             "similarity_boost": 0.75
#                         }
#                     },
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     return response.content
#                 return None
#         except Exception as e:
#             print(f"ElevenLabs error: {e}")
#             return None
#
#
# @app.websocket("/ws/voice")
# async def websocket_endpoint(websocket: WebSocket):
#     """WebSocket endpoint for real-time voice interaction"""
#     await websocket.accept()
#     session_id = f"session_{id(websocket)}"
#     agent = VoiceAgent(session_id)
#
#     deepgram_ws = None
#
#     try:
#         # Connect to Deepgram WebSocket
#         deepgram_url = "wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000&channels=1&model=nova-2"
#         deepgram_ws = await websockets.connect(
#             deepgram_url,
#             extra_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
#         )
#
#         await websocket.send_json({"type": "status", "message": "Connected and ready"})
#
#         # Handle messages concurrently
#         async def receive_from_client():
#             while True:
#                 try:
#                     message = await websocket.receive()
#
#                     if "bytes" in message:
#                         # Forward audio to Deepgram
#                         await deepgram_ws.send(message["bytes"])
#                     elif "text" in message:
#                         data = json.loads(message["text"])
#
#                         if data.get("type") == "stop":
#                             break
#
#                 except WebSocketDisconnect:
#                     break
#
#         async def receive_from_deepgram():
#             while True:
#                 try:
#                     response = await deepgram_ws.recv()
#                     data = json.loads(response)
#
#                     # Check if we have a final transcript
#                     transcript = data.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
#                     is_final = data.get("is_final", False)
#
#                     if transcript and is_final:
#                         # Send transcript to client
#                         await websocket.send_json({
#                             "type": "transcript",
#                             "text": transcript
#                         })
#
#                         # Process with GPT
#                         await websocket.send_json({
#                             "type": "status",
#                             "message": "Thinking..."
#                         })
#
#                         gpt_response = await agent.process_with_gpt(transcript)
#
#                         await websocket.send_json({
#                             "type": "response",
#                             "text": gpt_response
#                         })
#
#                         # Generate speech
#                         await websocket.send_json({
#                             "type": "status",
#                             "message": "Speaking..."
#                         })
#
#                         audio_bytes = await agent.speak_with_elevenlabs(gpt_response)
#
#                         if audio_bytes:
#                             await websocket.send_bytes(audio_bytes)
#                             await websocket.send_json({
#                                 "type": "audio_complete",
#                                 "message": "Audio sent"
#                             })
#
#                         await websocket.send_json({
#                             "type": "status",
#                             "message": "Ready"
#                         })
#
#                 except websockets.exceptions.ConnectionClosed:
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
#         await websocket.send_json({"type": "error", "message": str(e)})
#     finally:
#         if deepgram_ws:
#             await deepgram_ws.close()
#
#
# @app.post("/api/process")
# async def process_audio(audio_data: bytes):
#     """Alternative REST endpoint for processing audio"""
#     agent = VoiceAgent("rest_session")
#
#     # Transcribe
#     transcript = await agent.transcribe_with_deepgram(audio_data)
#     if not transcript:
#         return {"error": "Transcription failed"}
#
#     # Process with GPT
#     response_text = await agent.process_with_gpt(transcript)
#
#     # Generate speech
#     audio_bytes = await agent.speak_with_elevenlabs(response_text)
#
#     return {
#         "transcript": transcript,
#         "response": response_text,
#         "audio": audio_bytes.hex() if audio_bytes else None
#     }
#
#
# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "deepgram": "configured" if DEEPGRAM_API_KEY else "missing",
#         "elevenlabs": "configured" if ELEVENLABS_API_KEY else "missing",
#         "openai": "configured" if OPENAI_API_KEY else "missing"
#     }
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)


"""
Voice Agent Backend with FastAPI
Handles: Deepgram STT, OpenAI GPT, ElevenLabs TTS
"""
##second version
#
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# import asyncio
# import json
# import os
# from dotenv import load_dotenv
# import httpx
# import websockets
# from typing import Optional
#
# load_dotenv()
#
# app = FastAPI()
#
# # Enable CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Configuration
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
#
# # Store conversation history per session
# conversations = {}
#
#
# class VoiceAgent:
#     def __init__(self, session_id: str):
#         self.session_id = session_id
#         self.conversation_history = []
#
#     async def transcribe_with_deepgram(self, audio_data: bytes) -> Optional[str]:
#         """Send audio to Deepgram and get transcription"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     "https://api.deepgram.com/v1/listen",
#                     headers={
#                         "Authorization": f"Token {DEEPGRAM_API_KEY}",
#                         "Content-Type": "audio/wav"
#                     },
#                     content=audio_data,
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
#                     return transcript.strip()
#                 return None
#         except Exception as e:
#             print(f"Deepgram error: {e}")
#             return None
#
#     async def process_with_gpt(self, user_message: str) -> str:
#         """Process user message with GPT"""
#         try:
#             # Add user message to history
#             self.conversation_history.append({
#                 "role": "user",
#                 "content": user_message
#             })
#
#             # Keep only last 10 messages for context
#             if len(self.conversation_history) > 10:
#                 self.conversation_history = self.conversation_history[-10:]
#
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     "https://api.openai.com/v1/chat/completions",
#                     headers={
#                         "Authorization": f"Bearer {OPENAI_API_KEY}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": "gpt-4o-mini",
#                         "messages": [
#                             {
#                                 "role": "system",
#                                 "content": "You are a helpful voice assistant. Keep responses concise and conversational, under 100 words."
#                             },
#                             *self.conversation_history
#                         ],
#                         "max_tokens": 200,
#                         "temperature": 0.7
#                     },
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     assistant_message = result["choices"][0]["message"]["content"]
#
#                     # Add assistant response to history
#                     self.conversation_history.append({
#                         "role": "assistant",
#                         "content": assistant_message
#                     })
#
#                     return assistant_message
#                 return "Sorry, I couldn't process that."
#         except Exception as e:
#             print(f"GPT error: {e}")
#             return "Sorry, I encountered an error."
#
#     async def speak_with_elevenlabs(self, text: str) -> bytes:
#         """Convert text to speech with ElevenLabs"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
#                     headers={
#                         "xi-api-key": ELEVENLABS_API_KEY,
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "text": text,
#                         "model_id": "eleven_monolingual_v1",
#                         "voice_settings": {
#                             "stability": 0.5,
#                             "similarity_boost": 0.75
#                         }
#                     },
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     return response.content
#                 return None
#         except Exception as e:
#             print(f"ElevenLabs error: {e}")
#             return None
#
#
# @app.websocket("/ws/voice")
# async def websocket_endpoint(websocket: WebSocket):
#     """WebSocket endpoint for real-time voice interaction"""
#     await websocket.accept()
#     session_id = f"session_{id(websocket)}"
#     agent = VoiceAgent(session_id)
#
#     deepgram_ws = None
#
#     try:
#         # Connect to Deepgram WebSocket with proper headers
#         deepgram_url = "wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000&channels=1&model=nova-2"
#
#         # For websockets 11.0+, use additional_headers instead of extra_headers
#         deepgram_ws = await websockets.connect(
#             deepgram_url,
#             additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
#         )
#
#         await websocket.send_json({"type": "status", "message": "Connected and ready"})
#
#         # Handle messages concurrently
#         async def receive_from_client():
#             while True:
#                 try:
#                     message = await websocket.receive()
#
#                     if "bytes" in message:
#                         # Forward audio to Deepgram
#                         await deepgram_ws.send(message["bytes"])
#                     elif "text" in message:
#                         data = json.loads(message["text"])
#
#                         if data.get("type") == "stop":
#                             break
#
#                 except WebSocketDisconnect:
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
#                     # Check if we have a final transcript
#                     transcript = data.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
#                     is_final = data.get("is_final", False)
#
#                     if transcript and is_final:
#                         # Send transcript to client
#                         await websocket.send_json({
#                             "type": "transcript",
#                             "text": transcript
#                         })
#
#                         # Process with GPT
#                         await websocket.send_json({
#                             "type": "status",
#                             "message": "Thinking..."
#                         })
#
#                         gpt_response = await agent.process_with_gpt(transcript)
#
#                         await websocket.send_json({
#                             "type": "response",
#                             "text": gpt_response
#                         })
#
#                         # Generate speech
#                         await websocket.send_json({
#                             "type": "status",
#                             "message": "Speaking..."
#                         })
#
#                         audio_bytes = await agent.speak_with_elevenlabs(gpt_response)
#
#                         if audio_bytes:
#                             await websocket.send_bytes(audio_bytes)
#                             await websocket.send_json({
#                                 "type": "audio_complete",
#                                 "message": "Audio sent"
#                             })
#
#                         await websocket.send_json({
#                             "type": "status",
#                             "message": "Ready"
#                         })
#
#                 except websockets.exceptions.ConnectionClosed:
#                     break
#                 except Exception as e:
#                     print(f"Error receiving from Deepgram: {e}")
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
#         await websocket.send_json({"type": "error", "message": str(e)})
#     finally:
#         if deepgram_ws:
#             await deepgram_ws.close()
#
#
# @app.post("/api/process")
# async def process_audio(audio_data: bytes):
#     """Alternative REST endpoint for processing audio"""
#     agent = VoiceAgent("rest_session")
#
#     # Transcribe
#     transcript = await agent.transcribe_with_deepgram(audio_data)
#     if not transcript:
#         return {"error": "Transcription failed"}
#
#     # Process with GPT
#     response_text = await agent.process_with_gpt(transcript)
#
#     # Generate speech
#     audio_bytes = await agent.speak_with_elevenlabs(response_text)
#
#     return {
#         "transcript": transcript,
#         "response": response_text,
#         "audio": audio_bytes.hex() if audio_bytes else None
#     }
#
#
# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "deepgram": "configured" if DEEPGRAM_API_KEY else "missing",
#         "elevenlabs": "configured" if ELEVENLABS_API_KEY else "missing",
#         "openai": "configured" if OPENAI_API_KEY else "missing"
#     }
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)


# ##third version
# """
# Voice Agent Backend with FastAPI
# Handles: Deepgram STT, OpenAI GPT, ElevenLabs TTS
# """
#
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# import asyncio
# import json
# import os
# from dotenv import load_dotenv
# import httpx
# import websockets
# from typing import Optional
#
# load_dotenv()
#
# app = FastAPI()
#
# # Enable CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Configuration
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
#
# # Store conversation history per session
# conversations = {}
#
#
# class VoiceAgent:
#     def __init__(self, session_id: str):
#         self.session_id = session_id
#         self.conversation_history = []
#
#     async def transcribe_with_deepgram(self, audio_data: bytes) -> Optional[str]:
#         """Send audio to Deepgram and get transcription"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     "https://api.deepgram.com/v1/listen",
#                     headers={
#                         "Authorization": f"Token {DEEPGRAM_API_KEY}",
#                         "Content-Type": "audio/wav"
#                     },
#                     content=audio_data,
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
#                     return transcript.strip()
#                 return None
#         except Exception as e:
#             print(f"Deepgram error: {e}")
#             return None
#
#     async def process_with_gpt(self, user_message: str) -> str:
#         """Process user message with GPT"""
#         try:
#             # Add user message to history
#             self.conversation_history.append({
#                 "role": "user",
#                 "content": user_message
#             })
#
#             # Keep only last 10 messages for context
#             if len(self.conversation_history) > 10:
#                 self.conversation_history = self.conversation_history[-10:]
#
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     "https://api.openai.com/v1/chat/completions",
#                     headers={
#                         "Authorization": f"Bearer {OPENAI_API_KEY}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": "gpt-4o-mini",
#                         "messages": [
#                             {
#                                 "role": "system",
#                                 "content": "You are a helpful voice assistant. Keep responses concise and conversational, under 100 words."
#                             },
#                             *self.conversation_history
#                         ],
#                         "max_tokens": 200,
#                         "temperature": 0.7
#                     },
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     assistant_message = result["choices"][0]["message"]["content"]
#
#                     # Add assistant response to history
#                     self.conversation_history.append({
#                         "role": "assistant",
#                         "content": assistant_message
#                     })
#
#                     return assistant_message
#                 return "Sorry, I couldn't process that."
#         except Exception as e:
#             print(f"GPT error: {e}")
#             return "Sorry, I encountered an error."
#
#     async def speak_with_elevenlabs(self, text: str) -> bytes:
#         """Convert text to speech with ElevenLabs"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
#                     headers={
#                         "xi-api-key": ELEVENLABS_API_KEY,
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "text": text,
#                         "model_id": "eleven_monolingual_v1",
#                         "voice_settings": {
#                             "stability": 0.5,
#                             "similarity_boost": 0.75
#                         }
#                     },
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     return response.content
#                 return None
#         except Exception as e:
#             print(f"ElevenLabs error: {e}")
#             return None
#
#
# @app.websocket("/ws/voice")
# async def websocket_endpoint(websocket: WebSocket):
#     """WebSocket endpoint for real-time voice interaction"""
#     await websocket.accept()
#     session_id = f"session_{id(websocket)}"
#     agent = VoiceAgent(session_id)
#
#     deepgram_ws = None
#
#     try:
#         # Connect to Deepgram WebSocket with proper headers
#         deepgram_url = "wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000&channels=1&model=nova-2"
#
#         # For websockets 11.0+, use additional_headers instead of extra_headers
#         deepgram_ws = await websockets.connect(
#             deepgram_url,
#             additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
#         )
#
#         await websocket.send_json({"type": "status", "message": "Connected and ready"})
#
#         # Handle messages concurrently
#         async def receive_from_client():
#             while True:
#                 try:
#                     message = await websocket.receive()
#
#                     if "bytes" in message:
#                         # Forward audio to Deepgram
#                         print(f"Received audio chunk: {len(message['bytes'])} bytes")
#                         await deepgram_ws.send(message["bytes"])
#                     elif "text" in message:
#                         data = json.loads(message["text"])
#                         print(f"Received text message: {data}")
#
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
#                     print(f"Deepgram response: {data}")
#
#                     # Check if we have a final transcript
#                     transcript = data.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
#                     is_final = data.get("is_final", False)
#
#                     print(f"Transcript: '{transcript}', is_final: {is_final}")
#
#                     if transcript and is_final:
#                         print(f"Processing final transcript: {transcript}")
#
#                         # Send transcript to client
#                         await websocket.send_json({
#                             "type": "transcript",
#                             "text": transcript
#                         })
#
#                         # Process with GPT
#                         await websocket.send_json({
#                             "type": "status",
#                             "message": "Thinking..."
#                         })
#
#                         print("Calling GPT...")
#                         gpt_response = await agent.process_with_gpt(transcript)
#                         print(f"GPT response: {gpt_response}")
#
#                         await websocket.send_json({
#                             "type": "response",
#                             "text": gpt_response
#                         })
#
#                         # Generate speech
#                         await websocket.send_json({
#                             "type": "status",
#                             "message": "Speaking..."
#                         })
#
#                         print("Calling ElevenLabs...")
#                         audio_bytes = await agent.speak_with_elevenlabs(gpt_response)
#                         print(f"ElevenLabs returned: {len(audio_bytes) if audio_bytes else 0} bytes")
#
#                         if audio_bytes:
#                             await websocket.send_bytes(audio_bytes)
#                             await websocket.send_json({
#                                 "type": "audio_complete",
#                                 "message": "Audio sent"
#                             })
#
#                         await websocket.send_json({
#                             "type": "status",
#                             "message": "Ready"
#                         })
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
#         await websocket.send_json({"type": "error", "message": str(e)})
#     finally:
#         if deepgram_ws:
#             await deepgram_ws.close()
#
#
# @app.post("/api/process")
# async def process_audio(audio_data: bytes):
#     """Alternative REST endpoint for processing audio"""
#     agent = VoiceAgent("rest_session")
#
#     # Transcribe
#     transcript = await agent.transcribe_with_deepgram(audio_data)
#     if not transcript:
#         return {"error": "Transcription failed"}
#
#     # Process with GPT
#     response_text = await agent.process_with_gpt(transcript)
#
#     # Generate speech
#     audio_bytes = await agent.speak_with_elevenlabs(response_text)
#
#     return {
#         "transcript": transcript,
#         "response": response_text,
#         "audio": audio_bytes.hex() if audio_bytes else None
#     }
#
#
# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "deepgram": "configured" if DEEPGRAM_API_KEY else "missing",
#         "elevenlabs": "configured" if ELEVENLABS_API_KEY else "missing",
#         "openai": "configured" if OPENAI_API_KEY else "missing"
#     }
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)


# ##fourth version
# """
# Voice Agent Backend with FastAPI
# Handles: Deepgram STT, OpenAI GPT, ElevenLabs TTS
# """
#
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# import asyncio
# import json
# import os
# from dotenv import load_dotenv
# import httpx
# import websockets
# from typing import Optional
# import time
#
# load_dotenv()
#
# app = FastAPI()
#
# # Enable CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Configuration
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
#
# # Store conversation history per session
# conversations = {}
#
#
# class VoiceAgent:
#     def __init__(self, session_id: str):
#         self.session_id = session_id
#         self.conversation_history = []
#         self.current_transcript = ""
#         self.last_speech_time = time.time()
#         self.is_processing = False
#
#     async def transcribe_with_deepgram(self, audio_data: bytes) -> Optional[str]:
#         """Send audio to Deepgram and get transcription"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     "https://api.deepgram.com/v1/listen",
#                     headers={
#                         "Authorization": f"Token {DEEPGRAM_API_KEY}",
#                         "Content-Type": "audio/wav"
#                     },
#                     content=audio_data,
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
#                     return transcript.strip()
#                 return None
#         except Exception as e:
#             print(f"Deepgram error: {e}")
#             return None
#
#     async def process_with_gpt(self, user_message: str) -> str:
#         """Process user message with GPT"""
#         try:
#             # Add user message to history
#             self.conversation_history.append({
#                 "role": "user",
#                 "content": user_message
#             })
#
#             # Keep only last 10 messages for context
#             if len(self.conversation_history) > 10:
#                 self.conversation_history = self.conversation_history[-10:]
#
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     "https://api.openai.com/v1/chat/completions",
#                     headers={
#                         "Authorization": f"Bearer {OPENAI_API_KEY}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": "gpt-4o-mini",
#                         "messages": [
#                             {
#                                 "role": "system",
#                                 "content": "You are a helpful voice assistant. Keep responses concise and conversational, under 100 words."
#                             },
#                             *self.conversation_history
#                         ],
#                         "max_tokens": 200,
#                         "temperature": 0.7
#                     },
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     assistant_message = result["choices"][0]["message"]["content"]
#
#                     # Add assistant response to history
#                     self.conversation_history.append({
#                         "role": "assistant",
#                         "content": assistant_message
#                     })
#
#                     return assistant_message
#                 return "Sorry, I couldn't process that."
#         except Exception as e:
#             print(f"GPT error: {e}")
#             return "Sorry, I encountered an error."
#
#     async def speak_with_elevenlabs(self, text: str) -> bytes:
#         """Convert text to speech with ElevenLabs"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
#                     headers={
#                         "xi-api-key": ELEVENLABS_API_KEY,
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "text": text,
#                         "model_id": "eleven_monolingual_v1",
#                         "voice_settings": {
#                             "stability": 0.5,
#                             "similarity_boost": 0.75
#                         }
#                     },
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     return response.content
#                 return None
#         except Exception as e:
#             print(f"ElevenLabs error: {e}")
#             return None
#
#
# @app.websocket("/ws/voice")
# async def websocket_endpoint(websocket: WebSocket):
#     """WebSocket endpoint for real-time voice interaction"""
#     await websocket.accept()
#     session_id = f"session_{id(websocket)}"
#     agent = VoiceAgent(session_id)
#
#     deepgram_ws = None
#
#     try:
#         # Connect to Deepgram WebSocket with proper configuration
#         # Using mulaw encoding which works better with browser audio
#         deepgram_url = "wss://api.deepgram.com/v1/listen?model=nova-2&interim_results=true&punctuate=true&vad_events=true"
#
#         deepgram_ws = await websockets.connect(
#             deepgram_url,
#             additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
#         )
#
#         print("Connected to Deepgram")
#         await websocket.send_json({"type": "status", "message": "Connected and ready"})
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
#                             print(f"Forwarding audio chunk: {audio_size} bytes")
#                             await deepgram_ws.send(message["bytes"])
#                     elif "text" in message:
#                         data = json.loads(message["text"])
#                         print(f"Received command: {data}")
#
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
#                     # Handle different Deepgram message types
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
#                             print(f"Transcript: '{transcript}', is_final: {is_final}, speech_final: {speech_final}")
#
#                             # Accumulate transcript
#                             if transcript:
#                                 if is_final:
#                                     agent.current_transcript += " " + transcript
#                                     agent.current_transcript = agent.current_transcript.strip()
#                                     agent.last_speech_time = time.time()
#
#                                     print(f"Accumulated transcript: '{agent.current_transcript}'")
#
#                                     # Send interim transcript to client
#                                     await websocket.send_json({
#                                         "type": "interim_transcript",
#                                         "text": agent.current_transcript
#                                     })
#
#                                 # Process when speech is final (user stopped talking)
#                                 if speech_final and agent.current_transcript and not agent.is_processing:
#                                     agent.is_processing = True
#                                     final_transcript = agent.current_transcript
#                                     agent.current_transcript = ""
#
#                                     print(f"Processing final transcript: '{final_transcript}'")
#
#                                     # Send final transcript to client
#                                     await websocket.send_json({
#                                         "type": "transcript",
#                                         "text": final_transcript
#                                     })
#
#                                     # Process with GPT
#                                     await websocket.send_json({
#                                         "type": "status",
#                                         "message": "Thinking..."
#                                     })
#
#                                     print("Calling GPT...")
#                                     gpt_response = await agent.process_with_gpt(final_transcript)
#                                     print(f"GPT response: {gpt_response}")
#
#                                     await websocket.send_json({
#                                         "type": "response",
#                                         "text": gpt_response
#                                     })
#
#                                     # Generate speech
#                                     await websocket.send_json({
#                                         "type": "status",
#                                         "message": "Speaking..."
#                                     })
#
#                                     print("Calling ElevenLabs...")
#                                     audio_bytes = await agent.speak_with_elevenlabs(gpt_response)
#                                     print(f"ElevenLabs returned: {len(audio_bytes) if audio_bytes else 0} bytes")
#
#                                     if audio_bytes:
#                                         await websocket.send_bytes(audio_bytes)
#                                         await websocket.send_json({
#                                             "type": "audio_complete",
#                                             "message": "Audio sent"
#                                         })
#
#                                     await websocket.send_json({
#                                         "type": "status",
#                                         "message": "Listening..."
#                                     })
#
#                                     agent.is_processing = False
#
#                     elif msg_type == "SpeechStarted":
#                         print("Speech started detected")
#                         await websocket.send_json({
#                             "type": "speech_started"
#                         })
#
#                     elif msg_type == "UtteranceEnd":
#                         print("Utterance end detected")
#                         # This is another indicator that user stopped talking
#                         if agent.current_transcript and not agent.is_processing:
#                             # Wait a bit to see if more speech comes
#                             await asyncio.sleep(0.5)
#
#                             if agent.current_transcript and not agent.is_processing:
#                                 agent.is_processing = True
#                                 final_transcript = agent.current_transcript
#                                 agent.current_transcript = ""
#
#                                 print(f"Processing from utterance end: '{final_transcript}'")
#
#                                 await websocket.send_json({
#                                     "type": "transcript",
#                                     "text": final_transcript
#                                 })
#
#                                 await websocket.send_json({
#                                     "type": "status",
#                                     "message": "Thinking..."
#                                 })
#
#                                 gpt_response = await agent.process_with_gpt(final_transcript)
#
#                                 await websocket.send_json({
#                                     "type": "response",
#                                     "text": gpt_response
#                                 })
#
#                                 await websocket.send_json({
#                                     "type": "status",
#                                     "message": "Speaking..."
#                                 })
#
#                                 audio_bytes = await agent.speak_with_elevenlabs(gpt_response)
#
#                                 if audio_bytes:
#                                     await websocket.send_bytes(audio_bytes)
#                                     await websocket.send_json({
#                                         "type": "audio_complete",
#                                         "message": "Audio sent"
#                                     })
#
#                                 await websocket.send_json({
#                                     "type": "status",
#                                     "message": "Listening..."
#                                 })
#
#                                 agent.is_processing = False
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
#
#
# @app.post("/api/process")
# async def process_audio(audio_data: bytes):
#     """Alternative REST endpoint for processing audio"""
#     agent = VoiceAgent("rest_session")
#
#     # Transcribe
#     transcript = await agent.transcribe_with_deepgram(audio_data)
#     if not transcript:
#         return {"error": "Transcription failed"}
#
#     # Process with GPT
#     response_text = await agent.process_with_gpt(transcript)
#
#     # Generate speech
#     audio_bytes = await agent.speak_with_elevenlabs(response_text)
#
#     return {
#         "transcript": transcript,
#         "response": response_text,
#         "audio": audio_bytes.hex() if audio_bytes else None
#     }
#
#
# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "deepgram": "configured" if DEEPGRAM_API_KEY else "missing",
#         "elevenlabs": "configured" if ELEVENLABS_API_KEY else "missing",
#         "openai": "configured" if OPENAI_API_KEY else "missing"
#     }
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)

"""
Voice Agent Backend with FastAPI
Handles: Deepgram STT, OpenAI GPT, ElevenLabs TTS
"""

# ##fifth version
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# import asyncio
# import json
# import os
# from dotenv import load_dotenv
# import httpx
# import websockets
# from typing import Optional
# import time
#
# load_dotenv()
#
# app = FastAPI()
#
# # Enable CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Configuration
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
#
# # Store conversation history per session
# conversations = {}
#
#
# class VoiceAgent:
#     def __init__(self, session_id: str):
#         self.session_id = session_id
#         self.conversation_history = []
#         self.current_transcript = ""
#         self.last_speech_time = time.time()
#         self.is_processing = False
#
#     async def transcribe_with_deepgram(self, audio_data: bytes) -> Optional[str]:
#         """Send audio to Deepgram and get transcription"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     "https://api.deepgram.com/v1/listen",
#                     headers={
#                         "Authorization": f"Token {DEEPGRAM_API_KEY}",
#                         "Content-Type": "audio/wav"
#                     },
#                     content=audio_data,
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
#                     return transcript.strip()
#                 return None
#         except Exception as e:
#             print(f"Deepgram error: {e}")
#             return None
#
#     async def process_with_gpt(self, user_message: str) -> str:
#         """Process user message with GPT"""
#         try:
#             # Add user message to history
#             self.conversation_history.append({
#                 "role": "user",
#                 "content": user_message
#             })
#
#             # Keep only last 10 messages for context
#             if len(self.conversation_history) > 10:
#                 self.conversation_history = self.conversation_history[-10:]
#
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     "https://api.openai.com/v1/chat/completions",
#                     headers={
#                         "Authorization": f"Bearer {OPENAI_API_KEY}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": "gpt-4o-mini",
#                         "messages": [
#                             {
#                                 "role": "system",
#                                 "content": "You are a helpful voice assistant. Keep responses concise and conversational, under 100 words."
#                             },
#                             *self.conversation_history
#                         ],
#                         "max_tokens": 200,
#                         "temperature": 0.7
#                     },
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     assistant_message = result["choices"][0]["message"]["content"]
#
#                     # Add assistant response to history
#                     self.conversation_history.append({
#                         "role": "assistant",
#                         "content": assistant_message
#                     })
#
#                     return assistant_message
#                 return "Sorry, I couldn't process that."
#         except Exception as e:
#             print(f"GPT error: {e}")
#             return "Sorry, I encountered an error."
#
#     async def speak_with_elevenlabs(self, text: str) -> bytes:
#         """Convert text to speech with ElevenLabs"""
#         try:
#             print(f"ElevenLabs request - Text: '{text}'")
#             print(f"ElevenLabs API Key: {ELEVENLABS_API_KEY[:10]}..." if ELEVENLABS_API_KEY else "Missing!")
#             print(f"Voice ID: {ELEVENLABS_VOICE_ID}")
#
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
#                     headers={
#                         "xi-api-key": ELEVENLABS_API_KEY,
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "text": text,
#                         "model_id": "eleven_monolingual_v1",
#                         "voice_settings": {
#                             "stability": 0.5,
#                             "similarity_boost": 0.75
#                         }
#                     },
#                     timeout=30.0
#                 )
#
#                 print(f"ElevenLabs status code: {response.status_code}")
#
#                 if response.status_code == 200:
#                     audio_bytes = response.content
#                     print(f"Successfully got {len(audio_bytes)} bytes from ElevenLabs")
#                     return audio_bytes
#                 else:
#                     print(f"ElevenLabs error: {response.status_code}")
#                     print(f"Response: {response.text}")
#                     return None
#
#         except Exception as e:
#             print(f"ElevenLabs exception: {e}")
#             import traceback
#             traceback.print_exc()
#             return None
#
#
# @app.websocket("/ws/voice")
# async def websocket_endpoint(websocket: WebSocket):
#     """WebSocket endpoint for real-time voice interaction"""
#     await websocket.accept()
#     session_id = f"session_{id(websocket)}"
#     agent = VoiceAgent(session_id)
#
#     deepgram_ws = None
#
#     try:
#         # Connect to Deepgram WebSocket with proper configuration
#         # Using mulaw encoding which works better with browser audio
#         deepgram_url = "wss://api.deepgram.com/v1/listen?model=nova-2&interim_results=true&punctuate=true&vad_events=true"
#
#         deepgram_ws = await websockets.connect(
#             deepgram_url,
#             additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
#         )
#
#         print("Connected to Deepgram")
#         await websocket.send_json({"type": "status", "message": "Connected and ready"})
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
#                             print(f"Forwarding audio chunk: {audio_size} bytes")
#                             await deepgram_ws.send(message["bytes"])
#                     elif "text" in message:
#                         data = json.loads(message["text"])
#                         print(f"Received command: {data}")
#
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
#                     # Handle different Deepgram message types
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
#                             print(f"Transcript: '{transcript}', is_final: {is_final}, speech_final: {speech_final}")
#
#                             # Accumulate transcript
#                             if transcript:
#                                 if is_final:
#                                     agent.current_transcript += " " + transcript
#                                     agent.current_transcript = agent.current_transcript.strip()
#                                     agent.last_speech_time = time.time()
#
#                                     print(f"Accumulated transcript: '{agent.current_transcript}'")
#
#                                     # Send interim transcript to client
#                                     await websocket.send_json({
#                                         "type": "interim_transcript",
#                                         "text": agent.current_transcript
#                                     })
#
#                                 # Process when speech is final (user stopped talking)
#                                 if speech_final and agent.current_transcript and not agent.is_processing:
#                                     agent.is_processing = True
#                                     final_transcript = agent.current_transcript
#                                     agent.current_transcript = ""
#
#                                     print(f"Processing final transcript: '{final_transcript}'")
#
#                                     # Send final transcript to client
#                                     await websocket.send_json({
#                                         "type": "transcript",
#                                         "text": final_transcript
#                                     })
#
#                                     # Process with GPT
#                                     await websocket.send_json({
#                                         "type": "status",
#                                         "message": "Thinking..."
#                                     })
#
#                                     print("Calling GPT...")
#                                     gpt_response = await agent.process_with_gpt(final_transcript)
#                                     print(f"GPT response: {gpt_response}")
#
#                                     await websocket.send_json({
#                                         "type": "response",
#                                         "text": gpt_response
#                                     })
#
#                                     # Generate speech
#                                     await websocket.send_json({
#                                         "type": "status",
#                                         "message": "Speaking..."
#                                     })
#
#                                     print("Calling ElevenLabs...")
#                                     audio_bytes = await agent.speak_with_elevenlabs(gpt_response)
#                                     print(f"ElevenLabs returned: {len(audio_bytes) if audio_bytes else 0} bytes")
#
#                                     if audio_bytes:
#                                         await websocket.send_bytes(audio_bytes)
#                                         await websocket.send_json({
#                                             "type": "audio_complete",
#                                             "message": "Audio sent"
#                                         })
#
#                                     await websocket.send_json({
#                                         "type": "status",
#                                         "message": "Listening..."
#                                     })
#
#                                     agent.is_processing = False
#
#                     elif msg_type == "SpeechStarted":
#                         print("Speech started detected")
#                         await websocket.send_json({
#                             "type": "speech_started"
#                         })
#
#                     elif msg_type == "UtteranceEnd":
#                         print("Utterance end detected")
#                         # This is another indicator that user stopped talking
#                         if agent.current_transcript and not agent.is_processing:
#                             # Wait a bit to see if more speech comes
#                             await asyncio.sleep(0.5)
#
#                             if agent.current_transcript and not agent.is_processing:
#                                 agent.is_processing = True
#                                 final_transcript = agent.current_transcript
#                                 agent.current_transcript = ""
#
#                                 print(f"Processing from utterance end: '{final_transcript}'")
#
#                                 await websocket.send_json({
#                                     "type": "transcript",
#                                     "text": final_transcript
#                                 })
#
#                                 await websocket.send_json({
#                                     "type": "status",
#                                     "message": "Thinking..."
#                                 })
#
#                                 gpt_response = await agent.process_with_gpt(final_transcript)
#
#                                 await websocket.send_json({
#                                     "type": "response",
#                                     "text": gpt_response
#                                 })
#
#                                 await websocket.send_json({
#                                     "type": "status",
#                                     "message": "Speaking..."
#                                 })
#
#                                 audio_bytes = await agent.speak_with_elevenlabs(gpt_response)
#
#                                 if audio_bytes:
#                                     await websocket.send_bytes(audio_bytes)
#                                     await websocket.send_json({
#                                         "type": "audio_complete",
#                                         "message": "Audio sent"
#                                     })
#
#                                 await websocket.send_json({
#                                     "type": "status",
#                                     "message": "Listening..."
#                                 })
#
#                                 agent.is_processing = False
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
#
#
# @app.post("/api/process")
# async def process_audio(audio_data: bytes):
#     """Alternative REST endpoint for processing audio"""
#     agent = VoiceAgent("rest_session")
#
#     # Transcribe
#     transcript = await agent.transcribe_with_deepgram(audio_data)
#     if not transcript:
#         return {"error": "Transcription failed"}
#
#     # Process with GPT
#     response_text = await agent.process_with_gpt(transcript)
#
#     # Generate speech
#     audio_bytes = await agent.speak_with_elevenlabs(response_text)
#
#     return {
#         "transcript": transcript,
#         "response": response_text,
#         "audio": audio_bytes.hex() if audio_bytes else None
#     }
#
#
# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "deepgram": "configured" if DEEPGRAM_API_KEY else "missing",
#         "elevenlabs": "configured" if ELEVENLABS_API_KEY else "missing",
#         "openai": "configured" if OPENAI_API_KEY else "missing"
#     }
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)


"""
Voice Agent Backend with FastAPI
Handles: Deepgram STT, OpenAI GPT, ElevenLabs TTS
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import json
import os
from dotenv import load_dotenv
import httpx
import websockets
from typing import Optional
import time

load_dotenv()

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# Store conversation history per session
conversations = {}


class VoiceAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation_history = []
        self.current_transcript = ""
        self.last_speech_time = time.time()
        self.is_processing = False

    async def transcribe_with_deepgram(self, audio_data: bytes) -> Optional[str]:
        """Send audio to Deepgram and get transcription"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepgram.com/v1/listen",
                    headers={
                        "Authorization": f"Token {DEEPGRAM_API_KEY}",
                        "Content-Type": "audio/wav"
                    },
                    content=audio_data,
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
                    return transcript.strip()
                return None
        except Exception as e:
            print(f"Deepgram error: {e}")
            return None

    async def process_with_gpt(self, user_message: str) -> str:
        """Process user message with GPT"""
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Keep only last 10 messages for context
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful voice assistant. Keep responses concise and conversational, under 100 words."
                            },
                            *self.conversation_history
                        ],
                        "max_tokens": 200,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    assistant_message = result["choices"][0]["message"]["content"]

                    # Add assistant response to history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": assistant_message
                    })

                    return assistant_message
                return "Sorry, I couldn't process that."
        except Exception as e:
            print(f"GPT error: {e}")
            return "Sorry, I encountered an error."

    async def speak_with_elevenlabs(self, text: str) -> bytes:
        """Convert text to speech with ElevenLabs"""
        try:
            print(f"ElevenLabs request - Text: '{text}'")
            print(f"ElevenLabs API Key: {ELEVENLABS_API_KEY[:10]}..." if ELEVENLABS_API_KEY else "Missing!")
            print(f"Voice ID: {ELEVENLABS_VOICE_ID}")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                    headers={
                        "xi-api-key": ELEVENLABS_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_turbo_v2_5",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    },
                    timeout=30.0
                )

                print(f"ElevenLabs status code: {response.status_code}")

                if response.status_code == 200:
                    audio_bytes = response.content
                    print(f"Successfully got {len(audio_bytes)} bytes from ElevenLabs")
                    return audio_bytes
                else:
                    print(f"ElevenLabs error: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None

        except Exception as e:
            print(f"ElevenLabs exception: {e}")
            import traceback
            traceback.print_exc()
            return None


@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time voice interaction"""
    await websocket.accept()
    session_id = f"session_{id(websocket)}"
    agent = VoiceAgent(session_id)

    deepgram_ws = None

    try:
        # Connect to Deepgram WebSocket with proper configuration
        # Using mulaw encoding which works better with browser audio
        deepgram_url = "wss://api.deepgram.com/v1/listen?model=nova-2&interim_results=true&punctuate=true&vad_events=true"

        deepgram_ws = await websockets.connect(
            deepgram_url,
            additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
        )

        print("Connected to Deepgram")
        await websocket.send_json({"type": "status", "message": "Connected and ready"})

        # Handle messages concurrently
        async def receive_from_client():
            while True:
                try:
                    message = await websocket.receive()

                    if "bytes" in message:
                        # Forward audio to Deepgram
                        audio_size = len(message['bytes'])
                        if audio_size > 0:
                            print(f"Forwarding audio chunk: {audio_size} bytes")
                            await deepgram_ws.send(message["bytes"])
                    elif "text" in message:
                        data = json.loads(message["text"])
                        print(f"Received command: {data}")

                        if data.get("type") == "stop":
                            break

                except WebSocketDisconnect:
                    print("Client disconnected")
                    break
                except Exception as e:
                    print(f"Error receiving from client: {e}")
                    break

        async def receive_from_deepgram():
            while True:
                try:
                    response = await deepgram_ws.recv()
                    data = json.loads(response)

                    # Handle different Deepgram message types
                    msg_type = data.get("type", "")

                    if msg_type == "Results":
                        channel = data.get("channel", {})
                        alternatives = channel.get("alternatives", [])

                        if alternatives:
                            transcript = alternatives[0].get("transcript", "").strip()
                            is_final = data.get("is_final", False)
                            speech_final = data.get("speech_final", False)

                            print(f"Transcript: '{transcript}', is_final: {is_final}, speech_final: {speech_final}")

                            # Accumulate transcript
                            if transcript:
                                if is_final:
                                    agent.current_transcript += " " + transcript
                                    agent.current_transcript = agent.current_transcript.strip()
                                    agent.last_speech_time = time.time()

                                    print(f"Accumulated transcript: '{agent.current_transcript}'")

                                    # Send interim transcript to client
                                    await websocket.send_json({
                                        "type": "interim_transcript",
                                        "text": agent.current_transcript
                                    })

                                # Process when speech is final (user stopped talking)
                                if speech_final and agent.current_transcript and not agent.is_processing:
                                    agent.is_processing = True
                                    final_transcript = agent.current_transcript
                                    agent.current_transcript = ""

                                    print(f"Processing final transcript: '{final_transcript}'")

                                    # Send final transcript to client
                                    await websocket.send_json({
                                        "type": "transcript",
                                        "text": final_transcript
                                    })

                                    # Process with GPT
                                    await websocket.send_json({
                                        "type": "status",
                                        "message": "Thinking..."
                                    })

                                    print("Calling GPT...")
                                    gpt_response = await agent.process_with_gpt(final_transcript)
                                    print(f"GPT response: {gpt_response}")

                                    await websocket.send_json({
                                        "type": "response",
                                        "text": gpt_response
                                    })

                                    # Generate speech
                                    await websocket.send_json({
                                        "type": "status",
                                        "message": "Speaking..."
                                    })

                                    print("Calling ElevenLabs...")
                                    audio_bytes = await agent.speak_with_elevenlabs(gpt_response)
                                    print(f"ElevenLabs returned: {len(audio_bytes) if audio_bytes else 0} bytes")

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

                                    agent.is_processing = False

                    elif msg_type == "SpeechStarted":
                        print("Speech started detected")
                        await websocket.send_json({
                            "type": "speech_started"
                        })

                    elif msg_type == "UtteranceEnd":
                        print("Utterance end detected")
                        # This is another indicator that user stopped talking
                        if agent.current_transcript and not agent.is_processing:
                            # Wait a bit to see if more speech comes
                            await asyncio.sleep(0.5)

                            if agent.current_transcript and not agent.is_processing:
                                agent.is_processing = True
                                final_transcript = agent.current_transcript
                                agent.current_transcript = ""

                                print(f"Processing from utterance end: '{final_transcript}'")

                                await websocket.send_json({
                                    "type": "transcript",
                                    "text": final_transcript
                                })

                                await websocket.send_json({
                                    "type": "status",
                                    "message": "Thinking..."
                                })

                                gpt_response = await agent.process_with_gpt(final_transcript)

                                await websocket.send_json({
                                    "type": "response",
                                    "text": gpt_response
                                })

                                await websocket.send_json({
                                    "type": "status",
                                    "message": "Speaking..."
                                })

                                audio_bytes = await agent.speak_with_elevenlabs(gpt_response)

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

                                agent.is_processing = False

                except websockets.exceptions.ConnectionClosed:
                    print("Deepgram connection closed")
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
        if deepgram_ws:
            await deepgram_ws.close()


@app.post("/api/process")
async def process_audio(audio_data: bytes):
    """Alternative REST endpoint for processing audio"""
    agent = VoiceAgent("rest_session")

    # Transcribe
    transcript = await agent.transcribe_with_deepgram(audio_data)
    if not transcript:
        return {"error": "Transcription failed"}

    # Process with GPT
    response_text = await agent.process_with_gpt(transcript)

    # Generate speech
    audio_bytes = await agent.speak_with_elevenlabs(response_text)

    return {
        "transcript": transcript,
        "response": response_text,
        "audio": audio_bytes.hex() if audio_bytes else None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "deepgram": "configured" if DEEPGRAM_API_KEY else "missing",
        "elevenlabs": "configured" if ELEVENLABS_API_KEY else "missing",
        "openai": "configured" if OPENAI_API_KEY else "missing"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)