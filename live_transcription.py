import asyncio
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)
import pyaudio

# Your Deepgram API key
DEEPGRAM_API_KEY = "79f68f29e6c239b47d0cfb210abb761fe858e45d"

# Audio configuration
CHUNK = 8000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


async def main():
    try:
        # Initialize Deepgram client (without extra options)
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        # Create a live transcription connection
        dg_connection = deepgram.listen.live.v("1")

        # Define event handlers
        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) > 0:
                print(f"Transcription: {sentence}")

        def on_metadata(self, metadata, **kwargs):
            print(f"Metadata: {metadata}")

        def on_error(self, error, **kwargs):
            print(f"Error: {error}")

        def on_close(self, close_msg, **kwargs):
            print("Connection closed")

        # Register event handlers
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)

        # Configure transcription options
        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=CHANNELS,
            sample_rate=RATE,
            interim_results=True,
        )

        # Start the connection
        if dg_connection.start(options) is False:
            print("Failed to start connection")
            return

        # Initialize PyAudio for microphone input
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        print("Started listening... Speak into your microphone. Press Ctrl+C to stop.")

        # Stream audio to Deepgram
        try:
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                dg_connection.send(data)
                await asyncio.sleep(0.01)

        except KeyboardInterrupt:
            print("\nStopping...")

        finally:
            # Clean up
            stream.stop_stream()
            stream.close()
            audio.terminate()
            dg_connection.finish()

    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())