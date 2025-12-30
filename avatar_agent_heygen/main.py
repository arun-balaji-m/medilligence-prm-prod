from fastapi import FastAPI, WebSocket
from starlette.staticfiles import StaticFiles
from avatar_agent_heygen.stt import transcribe_audio
from avatar_agent_heygen.llm import get_gpt_response
from avatar_agent_heygen.avatar import HeyGenAvatar
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()
print("🔥 MAIN.PY LOADED 🔥")
print("🔥 MAIN.PY LOADED 🔥")


BASE_DIR = Path(__file__).parent

app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

@app.get("/")
async def serve_index():
    return HTMLResponse(
        (BASE_DIR / "index.html").read_text(encoding="utf-8")
    )




#
# @app.websocket("/ws/conversation/{client_session_id}")
# async def conversation(ws: WebSocket, client_session_id: str):
#     print("🔌 WebSocket handler entered")
#     await ws.accept()
#     print("✅ WebSocket accepted")
#     print("Frontend connected:", client_session_id)
#
#     avatar = HeyGenAvatar()
#
#     # 🔹 CREATE HEYGEN SESSION
#     heygen_details = await avatar.create_session()
#     await avatar.connect()
#
#     # 🔹 SEND DETAILS TO FRONTEND
#     await ws.send_json({
#         "type": "heygen_session",
#         "data": heygen_details
#     })
#
#     # ---- AUDIO BUFFER ----
#     audio_queue = asyncio.Queue()
#
#     async def audio_stream():
#         """Generator consumed by Deepgram"""
#         while True:
#             chunk = await audio_queue.get()
#             yield chunk
#
#     try:
#         while True:
#             # 🔹 RECEIVE ANY MESSAGE (text OR bytes)
#             message = await ws.receive()
#
#             if message["type"] == "websocket.disconnect":
#                 print("🔌 Client disconnected")
#                 break
#
#             # 🔹 TEXT MESSAGE (ping / control)
#             if "text" in message and message["text"] is not None:
#                 text = message["text"]
#                 print("📩 Text from frontend:", text)
#
#                 # optional: keepalive / ping handling
#                 if text == "ping":
#                     await ws.send_text("pong")
#                 continue
#
#             # 🔹 BINARY MESSAGE (audio)
#             if "bytes" in message and message["bytes"] is not None:
#                 await audio_queue.put(message["bytes"])
#
#                 # 🔹 START STT ONLY WHEN AUDIO ARRIVES
#                 user_text = await transcribe_audio(audio_stream())
#                 print("🗣 User said:", user_text)
#
#                 if not user_text:
#                     continue
#
#                 reply = await get_gpt_response(client_session_id, user_text)
#                 print("🤖 GPT reply:", reply)
#
#                 await avatar.speak(reply)
#
#     except WebSocketDisconnect:
#         print("⚠️ WebSocket disconnected")
#     except Exception as e:
#         print("❌ Session error:", e)
#     finally:
#         await avatar.close()
#         await ws.close()
#         print("🧹 Session cleaned up")
#

@app.websocket("/ws/conversation/{client_session_id}")
async def conversation(ws: WebSocket, client_session_id: str):
    print("🔌 WebSocket handler entered")
    await ws.accept()
    print("✅ WebSocket accepted")
    print("Frontend connected:", client_session_id)

    avatar = HeyGenAvatar()

    # Create HeyGen session
    heygen_details = await avatar.create_session()
    await avatar.connect()

    # Send session to frontend
    await ws.send_json({
        "type": "heygen_session",
        "data": heygen_details
    })

    try:
        while True:
            message = await ws.receive()

            # Client disconnected
            if message["type"] == "websocket.disconnect":
                print("🔌 Client disconnected")
                break

            # Ignore text messages for now
            if message.get("text"):
                print("📩 Text:", message["text"])
                continue

            # Audio bytes
            if message.get("bytes"):
                print("🎧 Audio chunk received:", len(message["bytes"]))
                # (STT pipeline comes here later)

    except WebSocketDisconnect:
        print("⚠️ WebSocketDisconnect")
    except Exception as e:
        print("❌ WebSocket error:", e)
    finally:
        # ❌ DO NOT CLOSE ws HERE
        await avatar.close()
        print("🧹 Avatar session closed")