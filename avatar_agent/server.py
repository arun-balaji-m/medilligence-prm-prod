import os
import threading
import traceback
from pathlib import Path

import requests
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions
)

# ------------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------------
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVUS_API_KEY = os.getenv("TAVUS_API_KEY")

if not DEEPGRAM_API_KEY:
    raise RuntimeError("DEEPGRAM_API_KEY is missing")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing")
if not TAVUS_API_KEY:
    raise RuntimeError("TAVUS_API_KEY is missing")

openai.api_key = OPENAI_API_KEY

# ------------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------------
app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

# ------------------------------------------------------------------
# Tavus configuration (REPLACE THESE)
# ------------------------------------------------------------------
TAVUS_BASE = "https://tavusapi.com/v2"
REPLICA_ID = "r9fa0878977a"
PERSONA_ID = "pcc5b5a65111"

# NOTE: for demo only (single user)
conversation_id: str | None = None

# ------------------------------------------------------------------
# Serve frontend
# ------------------------------------------------------------------
@app.get("/")
def home():
    html_path = BASE_DIR / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------
# Start Tavus avatar conversation
# ------------------------------------------------------------------
@app.post("/start-avatar")
def start_avatar():
    global conversation_id

    resp = requests.post(
        f"{TAVUS_BASE}/conversations",
        headers={
            "x-api-key": TAVUS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "replica_id": REPLICA_ID,
            "persona_id": PERSONA_ID,
            "conversation_name": "Medical Pre-Assessment"
        },
        timeout=15
    )

    resp.raise_for_status()
    data = resp.json()

    print("🧾 Tavus response:", data)  # <<< IMPORTANT

    conversation_id = data["conversation_id"]

    # TEMP: don’t assume join_url
    return data



# ------------------------------------------------------------------
# GPT processing (SYNC – thread-safe)
# ------------------------------------------------------------------
def ask_gpt(text: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a medical pre-assessment assistant. "
                    "Collect symptoms politely. "
                    "Ask follow-up questions. "
                    "Do NOT diagnose."
                )
            },
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content


# ------------------------------------------------------------------
# Send message to Tavus (avatar speaks)
# ------------------------------------------------------------------
def send_to_tavus(text: str):
    if not conversation_id:
        print("⚠️ Tavus conversation not started yet, skipping send")
        return

    try:
        requests.post(
            f"{TAVUS_BASE}/conversations/{conversation_id}/events",
            headers={
                "x-api-key": TAVUS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "type": "agent_message",
                "text": text
            },
            timeout=10
        )
        print("🗣️ Sent response to Tavus")

    except Exception:
        print("❌ Failed sending message to Tavus")
        traceback.print_exc()


# ------------------------------------------------------------------
# Combined GPT + Tavus processing (BACKGROUND THREAD)
# ------------------------------------------------------------------
def process_text(text: str):
    try:
        print("🧠 process_text received:", text)

        reply = ask_gpt(text)
        print("🤖 GPT reply:", reply)

        send_to_tavus(reply)

    except Exception:
        print("❌ ERROR inside process_text")
        traceback.print_exc()


# ------------------------------------------------------------------
# Deepgram STT (SYNC streaming – CORRECT USAGE)
# ------------------------------------------------------------------
dg = DeepgramClient(DEEPGRAM_API_KEY)


@app.websocket("/stt")
async def websocket_stt(ws: WebSocket):
    await ws.accept()
    print("🎤 WebSocket connected")

    dg_socket = dg.listen.live.v("1")

    options = LiveOptions(
        model="nova-2",
        language="en-US",
        encoding="linear16",
        sample_rate=16000,
        punctuate=True,
        interim_results=False,
    )

    # IMPORTANT: correct callback signature
    def on_transcript(result=None, **kwargs):
        if result is None:
            result = kwargs.get("result")

        if not result:
            return

        transcript = result.channel.alternatives[0].transcript
        if transcript:
            print("👤 Patient:", transcript)

            threading.Thread(
                target=process_text,
                args=(transcript,),
                daemon=True
            ).start()

    dg_socket.on(LiveTranscriptionEvents.Transcript, on_transcript)

    # START Deepgram (NO await – sync API)
    dg_socket.start(options)

    try:
        while True:
            audio = await ws.receive_bytes()
            dg_socket.send(audio)  # sync send
    except Exception as e:
        print("🔌 WebSocket closed:", e)
    finally:
        dg_socket.finish()
        print("🛑 Deepgram session finished")
