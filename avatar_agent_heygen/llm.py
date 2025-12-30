from openai import AsyncOpenAI
from avatar_agent_heygen.config import OPENAI_API_KEY
from avatar_agent_heygen.session import session_store

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a medical pre-assessment assistant.
Do not diagnose.
Ask structured clarifying questions.
Be calm and empathetic.
"""

async def get_gpt_response(session_id, user_text):
    session_store.add(session_id, "user", user_text)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(session_store.get(session_id))

    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    reply = response.choices[0].message.content
    session_store.add(session_id, "assistant", reply)
    return reply
