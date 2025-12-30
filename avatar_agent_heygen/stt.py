from deepgram import DeepgramClient, LiveOptions
from avatar_agent_heygen.config import DEEPGRAM_API_KEY

deepgram = DeepgramClient(DEEPGRAM_API_KEY)

async def transcribe_audio(audio_chunks):
    transcript = ""

    async def on_message(msg):
        nonlocal transcript
        if "channel" in msg:
            alt = msg["channel"]["alternatives"]
            if alt and alt[0]["transcript"]:
                transcript += alt[0]["transcript"] + " "

    options = LiveOptions(
        model="nova-2",
        language="en-US",
        punctuate=True,
        interim_results=False
    )

    conn = deepgram.listen.asyncwebsocket.v("1")
    conn.on("transcript", on_message)

    await conn.start(options)

    async for chunk in audio_chunks:
        await conn.send(chunk)

    await conn.finish()
    return transcript.strip()
