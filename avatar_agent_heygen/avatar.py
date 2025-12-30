import aiohttp
from avatar_agent_heygen.config import HEYGEN_API_KEY, HEYGEN_AVATAR_ID

HEYGEN_CREATE_URL = "https://api.heygen.com/v1/streaming.new"
HEYGEN_WS_URL = "wss://api.heygen.com/v1/streaming"

class HeyGenAvatar:
    def __init__(self):
        self.session_id = None
        self.ws = None
        self.http = None

    async def create_session(self):
        headers = {
            "Authorization": f"Bearer {HEYGEN_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "avatar_id": HEYGEN_AVATAR_ID,
            "voice": {"speed": 1.0, "pitch": 1.0}
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(HEYGEN_CREATE_URL, json=payload) as resp:
                data = await resp.json()
                print("HEYGEN CREATE RESPONSE:", data)  # 🔥 ADD THIS
                resp.raise_for_status()
                self.session_id = data["data"]["session_id"]
                return data["data"]

    async def connect(self):
        headers = {
            "Authorization": f"Bearer {HEYGEN_API_KEY}"
        }
        self.http = aiohttp.ClientSession(headers=headers)
        self.ws = await self.http.ws_connect(HEYGEN_WS_URL)

    async def speak(self, text):
        await self.ws.send_json({
            "type": "talk",
            "session_id": self.session_id,
            "text": text
        })

    async def close(self):
        if self.ws:
            await self.ws.close()
        if self.http:
            await self.http.close()
