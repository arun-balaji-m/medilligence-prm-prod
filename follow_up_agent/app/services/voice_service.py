import httpx
from ..config import settings
from typing import Optional

class VoiceService:
    @staticmethod
    async def speak_with_elevenlabs(text: str) -> Optional[bytes]:
        """Convert text to speech with ElevenLabs"""
        try:
            print(f"ElevenLabs TTS - Text: '{text}'")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}",
                    headers={
                        "xi-api-key": settings.ELEVENLABS_API_KEY,
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

                if response.status_code == 200:
                    audio_bytes = response.content
                    print(f"Successfully got {len(audio_bytes)} bytes from ElevenLabs")
                    return audio_bytes
                else:
                    print(f"ElevenLabs error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            print(f"ElevenLabs exception: {e}")
            return None

