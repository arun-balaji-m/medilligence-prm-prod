import httpx
import asyncio
from typing import Optional
from patient_fao_agent.app.config import settings
import json


class VoiceService:
    def __init__(self):
        self.deepgram_api_key = settings.DEEPGRAM_API_KEY
        self.elevenlabs_api_key = settings.ELEVENLABS_API_KEY
        self.elevenlabs_voice_id = settings.ELEVENLABS_VOICE_ID

    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using Deepgram"""
        try:
            print(f"[Deepgram] Transcribing {len(audio_data)} bytes...")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepgram.com/v1/listen",
                    headers={
                        "Authorization": f"Token {self.deepgram_api_key}",
                        "Content-Type": "audio/wav"
                    },
                    content=audio_data,
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
                    print(f"[Deepgram] Transcript: {transcript}")
                    return transcript.strip()
                else:
                    print(f"[Deepgram] Error: {response.status_code}")
                    return None

        except Exception as e:
            print(f"[Deepgram] Exception: {str(e)}")
            return None

    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech using ElevenLabs"""
        try:
            print(f"[ElevenLabs] Converting text: '{text[:50]}...'")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}",
                    headers={
                        "xi-api-key": self.elevenlabs_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_turbo_v2_5",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                            "style": 0.0,
                            "use_speaker_boost": True
                        }
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    audio_bytes = response.content
                    print(f"[ElevenLabs] Generated {len(audio_bytes)} bytes")
                    return audio_bytes
                else:
                    print(f"[ElevenLabs] Error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            print(f"[ElevenLabs] Exception: {str(e)}")
            return None