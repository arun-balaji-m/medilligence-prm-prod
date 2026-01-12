# import os
# import httpx
# from typing import Optional
#
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
#
#
# class VoiceHandler:
#     def __init__(self):
#         self.current_transcript = ""
#         self.is_processing = False
#
#     async def text_to_speech(self, text: str) -> Optional[bytes]:
#         """Convert text to speech using ElevenLabs"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
#                     headers={
#                         "xi-api-key": ELEVENLABS_API_KEY,
#                         "Content-Type": "application/json",
#                         "Accept": "audio/mpeg"
#                     },
#                     json={
#                         "text": text,
#                         "model_id": "eleven_turbo_v2_5",
#                         "voice_settings": {
#                             "stability": 0.5,
#                             "similarity_boost": 0.75,
#                             "use_speaker_boost": True
#                         }
#                     },
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     return response.content
#                 return None
#
#         except Exception as e:
#             print(f"[VoiceHandler] ElevenLabs error: {e}")
#             return None


from elevenlabs import ElevenLabs
import os

client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])


class VoiceHandler:
    def __init__(self):
        self.current_transcript = ""
        self.is_processing = False

    async def text_to_speech(self, text: str):
        try:
            audio_stream = client.text_to_speech.stream(
                voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
                model_id="eleven_multilingual_v2",
                text=text
            )

            audio_bytes = b""
            for chunk in audio_stream:
                if chunk:
                    audio_bytes += chunk

            return audio_bytes

        except Exception as e:
            print("🔴 ElevenLabs TTS failed:", e)
            return None
