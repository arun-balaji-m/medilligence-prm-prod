import asyncio
import tkinter as tk
from tkinter import scrolledtext
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_response import LLMAssistantResponseAggregator, LLMUserResponseAggregator
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.transports.local.audio import LocalAudioTransport
#from pipecat.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import EndFrame, LLMMessagesFrame
import threading

# API Keys
DEEPGRAM_API_KEY = "79f68f29e6c239b47d0cfb210abb761fe858e45d"
OPENAI_API_KEY = "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"
CARTESIA_API_KEY = "sk_car_BUjgUbHpMe2PkbUV3FLDHY"

class PipecatVoiceAssistant:
    def __init__(self):
        self.pipeline_task = None
        self.is_running = False

    async def create_pipeline(self, gui_callback):
        # Services
        stt = DeepgramSTTService(
            api_key=DEEPGRAM_API_KEY,
            model="nova-2"
        )

        llm = OpenAILLMService(
            api_key=OPENAI_API_KEY,
            model="gpt-3.5-turbo"
        )

        tts = CartesiaTTSService(
            api_key=CARTESIA_API_KEY,
            voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22"  # Friendly voice
        )

        # Transport (uses local audio)
        transport = LocalAudioTransport(
                audio_in_enabled=True,
                audio_out_enabled=True,
        )

        # VAD
        # vad = SileroVADAnalyzer()

        # Message aggregators for conversation history
        user_response = LLMUserResponseAggregator()
        assistant_response = LLMAssistantResponseAggregator()

        # Pipeline
        pipeline = Pipeline([
            transport.input(),
            # vad,
            stt,
            user_response,
            llm,
            tts,
            assistant_response,
            transport.output(),
        ])

        return pipeline, transport

    async def run(self, gui_callback):
        self.is_running = True
        pipeline, transport = await self.create_pipeline(gui_callback)

        task = PipelineTask(pipeline)

        runner = PipelineRunner()
        await runner.run(task)


# GUI remains similar but simpler
class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pipecat Voice Assistant")
        self.root.geometry("800x600")

        self.assistant = PipecatVoiceAssistant()
        self.create_widgets()

    def create_widgets(self):
        # Similar to your current GUI
        # But MUCH simpler - just start/stop buttons
        # Pipecat handles everything else!
        pass

    def start_assistant(self):
        threading.Thread(
            target=lambda: asyncio.run(self.assistant.run(self.update_conversation)),
            daemon=True
        ).start()

    def update_conversation(self, text, role):
        # Update GUI with conversation
        pass


def main():
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()