import asyncio
import json
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)
import pyaudio
import openai
from gtts import gTTS
import pygame
import io
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import queue

# API Keys
DEEPGRAM_API_KEY = "79f68f29e6c239b47d0cfb210abb761fe858e45d"
OPENAI_API_KEY = "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"  # Replace with your OpenAI API key

# Audio configuration
CHUNK = 8000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Queue for thread-safe GUI updates
gui_queue = queue.Queue()


class VoiceAIAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice AI Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        self.is_listening = False
        self.conversation_history = []

        # Create GUI elements
        self.create_widgets()

        # Start GUI update checker
        self.root.after(100, self.check_queue)

    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#2563eb", pady=20)
        title_frame.pack(fill=tk.X)

        title_label = tk.Label(
            title_frame,
            text="🎤 Voice AI Assistant",
            font=("Arial", 24, "bold"),
            bg="#2563eb",
            fg="white"
        )
        title_label.pack()

        # Status Frame
        status_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        status_frame.pack(fill=tk.X, padx=20)

        self.status_label = tk.Label(
            status_frame,
            text="Status: Ready",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#374151"
        )
        self.status_label.pack()

        # Control Buttons Frame
        button_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        button_frame.pack()

        self.start_button = tk.Button(
            button_frame,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            font=("Arial", 14, "bold"),
            bg="#10b981",
            fg="white",
            padx=30,
            pady=15,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_conversation,
            font=("Arial", 12),
            bg="#6b7280",
            fg="white",
            padx=20,
            pady=15,
            relief=tk.RAISED,
            cursor="hand2"
        )
        clear_button.pack(side=tk.LEFT, padx=5)

        # Conversation Display
        conv_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        conv_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        conv_label = tk.Label(
            conv_frame,
            text="Conversation:",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            anchor="w"
        )
        conv_label.pack(fill=tk.X)

        self.conversation_text = scrolledtext.ScrolledText(
            conv_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="white",
            fg="#1f2937",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for styling
        self.conversation_text.tag_config("user", foreground="#2563eb", font=("Arial", 11, "bold"))
        self.conversation_text.tag_config("assistant", foreground="#059669", font=("Arial", 11, "bold"))
        self.conversation_text.tag_config("system", foreground="#dc2626", font=("Arial", 10, "italic"))

    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.start_button.config(
                text="🛑 Stop Listening",
                bg="#ef4444"
            )
            self.update_status("Listening...")
            # Start the async voice assistant in a separate thread
            threading.Thread(target=self.start_voice_assistant, daemon=True).start()
        else:
            self.is_listening = False
            self.start_button.config(
                text="🎤 Start Listening",
                bg="#10b981"
            )
            self.update_status("Stopped")

    def start_voice_assistant(self):
        asyncio.run(voice_assistant_loop(self))

    def update_status(self, status):
        gui_queue.put(("status", status))

    def add_transcript(self, text):
        gui_queue.put(("transcript", text))

    def add_response(self, text):
        gui_queue.put(("response", text))

    def add_system_message(self, text):
        gui_queue.put(("system", text))

    def clear_conversation(self):
        self.conversation_text.delete(1.0, tk.END)
        self.conversation_history = []
        self.update_status("Conversation cleared")

    def check_queue(self):
        try:
            while True:
                msg_type, content = gui_queue.get_nowait()

                if msg_type == "status":
                    self.status_label.config(text=f"Status: {content}")

                elif msg_type == "transcript":
                    self.conversation_text.insert(tk.END, "You: ", "user")
                    self.conversation_text.insert(tk.END, f"{content}\n\n")
                    self.conversation_text.see(tk.END)

                elif msg_type == "response":
                    self.conversation_text.insert(tk.END, "AI: ", "assistant")
                    self.conversation_text.insert(tk.END, f"{content}\n\n")
                    self.conversation_text.see(tk.END)

                elif msg_type == "system":
                    self.conversation_text.insert(tk.END, f"[{content}]\n", "system")
                    self.conversation_text.see(tk.END)

        except queue.Empty:
            pass

        self.root.after(100, self.check_queue)


async def send_to_gpt(text, gui):
    """Send text to OpenAI GPT and get response"""
    try:
        gui.update_status("Thinking...")

        # Add user message to history
        gui.conversation_history.append({"role": "user", "content": text})

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper responses
            messages=gui.conversation_history,
            max_tokens=500,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content

        # Add assistant response to history
        gui.conversation_history.append({"role": "assistant", "content": ai_response})

        gui.add_response(ai_response)

        # Convert response to speech
        await text_to_speech(ai_response, gui)

    except Exception as e:
        error_msg = f"Error with GPT: {str(e)}"
        print(error_msg)
        gui.add_system_message(error_msg)
        gui.update_status("Error getting response")


async def text_to_speech(text, gui):
    """Convert text to speech using gTTS"""
    try:
        gui.update_status("Speaking...")

        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)

        # Save to in-memory file
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)

        # Play audio using pygame
        pygame.mixer.music.load(audio_fp)
        pygame.mixer.music.play()

        # Wait for audio to finish
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

        gui.update_status("Listening...")

    except Exception as e:
        error_msg = f"Error with TTS: {str(e)}"
        print(error_msg)
        gui.add_system_message(error_msg)


async def voice_assistant_loop(gui):
    """Main voice assistant loop"""
    try:
        # Initialize Deepgram client
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        dg_connection = deepgram.listen.live.v("1")

        # Store complete sentences
        complete_sentence = []

        # Define event handlers
        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) > 0:
                is_final = result.is_final

                if is_final:
                    complete_sentence.append(sentence)
                    print(f"Final Transcript: {sentence}")

                    # If sentence ends with punctuation, send to GPT
                    if sentence.strip().endswith(('.', '?', '!')):
                        full_text = ' '.join(complete_sentence)
                        complete_sentence.clear()

                        gui.add_transcript(full_text)

                        # Create a new task to send to GPT
                        asyncio.create_task(send_to_gpt(full_text, gui))
                else:
                    print(f"Interim: {sentence}")

        def on_error(self, error, **kwargs):
            error_msg = f"Deepgram Error: {error}"
            print(error_msg)
            gui.add_system_message(error_msg)

        def on_close(self, close_msg, **kwargs):
            print("Deepgram connection closed")

        # Register event handlers
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
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
            punctuate=True,
        )

        # Start the connection
        if dg_connection.start(options) is False:
            gui.add_system_message("Failed to start Deepgram connection")
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

        gui.add_system_message("Started listening... Speak into your microphone")

        # Stream audio to Deepgram
        try:
            while gui.is_listening:
                data = stream.read(CHUNK, exception_on_overflow=False)
                dg_connection.send(data)
                await asyncio.sleep(0.01)

        except Exception as e:
            print(f"Streaming error: {e}")

        finally:
            # Clean up
            stream.stop_stream()
            stream.close()
            audio.terminate()
            dg_connection.finish()
            gui.update_status("Stopped")

    except Exception as e:
        error_msg = f"Voice Assistant Error: {str(e)}"
        print(error_msg)
        gui.add_system_message(error_msg)
        import traceback
        traceback.print_exc()


def main():
    root = tk.Tk()
    app = VoiceAIAssistantGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()