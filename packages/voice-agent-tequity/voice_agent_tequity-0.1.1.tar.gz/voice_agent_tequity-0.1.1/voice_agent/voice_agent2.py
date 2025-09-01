import os
import json
import time
import wave
import pyaudio
import websocket
import threading
from dotenv import load_dotenv
from urllib.parse import urlencode
from datetime import datetime

# --- Import your LLM + TTS + Vector base handler ---
from voice_agent.llm.gemini_llm import GeminiLLm
from voice_agent.llm.openai_llm import OpenAILLM
from voice_agent.llm.ollma_llm import OllamaLLM
from voice_agent.llm.openrouter_service_llm import OpenRouterLLM
from voice_agent.llm.claude_llm import ClaudeLLM
from voice_agent.llm.custom_llm import CustomLLm
from voice_agent.tts.evenlabs_tts import ElevenTTS
from voice_agent.gather.base import BaseVectorHandler

load_dotenv()

# -------------------------------------------------------------------
# CLASS 1: VoiceAgent (LLM only, no vector DB)
# -------------------------------------------------------------------
class VoiceAgent:
    """
    Handles ONLY LLM selection and running prompts.
    Speaks the response automatically using ElevenLabs TTS.
    """
    def __init__(self, llm_type: str = "openai", **kwargs):
        self.llm = self._get_llm(llm_type, **kwargs)

    def _get_llm(self, llm_type: str, **kwargs):
        llm_type = llm_type.lower()
        if llm_type == "gemini":
            return GeminiLLm(api_key=kwargs.get("api_key"))
        elif llm_type == "openai":
            return OpenAILLM(api_key=kwargs.get("api_key"), model_name=kwargs.get("model_name", "gpt-4"))
        elif llm_type == "ollama":
            return OllamaLLM(model_name=kwargs.get("model_name", "gemma3"), api_key=kwargs.get("api_key"))
        elif llm_type == "openrouter":
            return OpenRouterLLM(api_key=kwargs.get("api_key"), model_name=kwargs.get("model_name", "openrouter-model"))
        elif llm_type == "claude":
            return ClaudeLLM(api_key=kwargs.get("api_key"), model_name=kwargs.get("model_name", "claude-3"))
        elif llm_type == "custom":
            return CustomLLm(api_key=kwargs.get("api_key"), model_url=kwargs.get("model_url"))
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

    def run_llm(self, prompt: str, **kwargs):
        if not self.llm:
            raise RuntimeError("No LLM initialized.")
        print(f"[INFO] Running prompt on {self.llm.__class__.__name__}")
        answer = self.llm.ask(prompt, **kwargs)
        if answer:
            tts = ElevenTTS(os.getenv("ELEVEN_API_KEY"))
            tts.speak(answer)
        return answer


# -------------------------------------------------------------------
# CLASS 2: TrainVoiceAgent (Vector DB only)
# -------------------------------------------------------------------
class TrainVoiceAgent(BaseVectorHandler):
    """
    Handles ONLY vector DB operations.
    Inherits from BaseVectorHandler.
    """
    def __init__(self, train=False, folder_path="./data_folder", email="user@example.com"):
        super().__init__(train=train, folder_path=folder_path, email=email)

    def insert_data(self):
        """Explicit method for inserting data into vector DB."""
        print("[INFO] Inserting data into vector DB...")
        self.train_vector_db()

    def retrieve_data(self, query_text: str):
        """Retrieve chunks and run through Gemini LLM with TTS."""
        print("[INFO] Retrieving data from vector DB...")
        relevant_chunks = self.query(query_text)
        llm = GeminiLLm(api_key=os.getenv("GEMINI_API_KEY"))
        answer = llm.ask(query_text, relevant_chunks)
        if answer:
            tts = ElevenTTS(os.getenv("ELEVEN_API_KEY"))
            tts.speak(answer)
        return answer


# -------------------------------------------------------------------
# CLASS 3: SpeechToText (Real-time transcription + LLM integration)
# -------------------------------------------------------------------
class SpeechToText:
    """
    Streams microphone audio to AssemblyAI WebSocket API for transcription,
    then passes text to LLM (and optionally Vector DB) and speaks the result.
    """
    def __init__(self, api_key, llm_type="gemini", vector_mode=False,
                 input_device_index=None, sample_rate=16000, channels=1):
        self.api_key = api_key
        self.sample_rate = sample_rate
        self.channels = channels
        self.input_device_index = input_device_index
        self.vector_mode = vector_mode

        # Choose LLM or Vector handler
        if vector_mode:
            self.agent = TrainVoiceAgent(train=False)
        else:
            self.agent = VoiceAgent(llm_type=llm_type, api_key=os.getenv("GOOGLE_API_KEY"))

        # WebSocket endpoint
        self.connection_params = {"sample_rate": self.sample_rate, "format_turns": True}
        base_url = "wss://streaming.assemblyai.com/v3/ws"
        self.api_endpoint = f"{base_url}?{urlencode(self.connection_params)}"

        # Audio config
        self.frames_per_buffer = 800
        self.format = pyaudio.paInt16

        # Internal state
        self.audio = None
        self.stream = None
        self.ws_app = None
        self.audio_thread = None
        self.stop_event = threading.Event()
        self.recorded_frames = []
        self.recording_lock = threading.Lock()
        self.final_text = ""

    # --- WebSocket Handlers ---
    def on_open(self, ws):
        print("WebSocket connection opened.")
        print(f"Connected to: {self.api_endpoint}")

        def stream_audio():
            print("🎤 Starting audio streaming...")
            while not self.stop_event.is_set():
                try:
                    audio_data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
                    with self.recording_lock:
                        self.recorded_frames.append(audio_data)
                    ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
                except Exception as e:
                    print(f"Error streaming audio: {e}")
                    break
            print("Audio streaming stopped.")

        self.audio_thread = threading.Thread(target=stream_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data.get("type") == "Turn":
                transcript = data.get("transcript", "")
                formatted = data.get("turn_is_formatted", False)
                if formatted and transcript.strip():
                    print(f"\n[USER SAID]: {transcript}")
                    # Run LLM or Vector Agent + Speak
                    if self.vector_mode:
                        self.agent.retrieve_data(transcript)
                    else:
                        self.agent.run_llm(transcript)
                    self.final_text = transcript
        except Exception as e:
            print(f"Error handling message: {e}")

    def on_error(self, ws, error):
        print(f"\nWebSocket Error: {error}")
        self.stop_event.set()

    def on_close(self, ws, close_status_code, close_msg):
        print(f"\nWebSocket Disconnected: {close_status_code} {close_msg}")
        self.stop_event.set()
        self.save_wav_file()
        self.cleanup_audio()

    # --- Audio Helpers ---
    def save_wav_file(self):
        if not self.recorded_frames:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recorded_audio_{timestamp}.wav"
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            with self.recording_lock:
                wf.writeframes(b"".join(self.recorded_frames))
        print(f"Audio saved to: {filename}")

    def cleanup_audio(self):
        if self.stream:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.audio:
            self.audio.terminate()
            self.audio = None
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)

    # --- Public Methods ---
    def start(self):
        self.audio = pyaudio.PyAudio()
        try:
            self.stream = self.audio.open(
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.frames_per_buffer,
                channels=self.channels,
                format=self.format,
                rate=self.sample_rate,
            )
            print("Microphone stream opened successfully.")
            print("🎤 Speak now. Press Ctrl+C to stop.")
        except Exception as e:
            print(f"Error opening microphone stream: {e}")
            if self.audio:
                self.audio.terminate()
            return ""

        self.ws_app = websocket.WebSocketApp(
            self.api_endpoint,
            header={"Authorization": self.api_key},
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        ws_thread = threading.Thread(target=self.ws_app.run_forever)
        ws_thread.daemon = True
        ws_thread.start()

        try:
            while ws_thread.is_alive() and not self.stop_event.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nCtrl+C received. Stopping...")
            self.stop()
        finally:
            self.cleanup_audio()

        return self.final_text

    def stop(self):
        self.stop_event.set()
        if self.ws_app and self.ws_app.sock and self.ws_app.sock.connected:
            try:
                self.ws_app.send(json.dumps({"type": "Terminate"}))
                time.sleep(2)
            except Exception as e:
                print(f"Error sending termination message: {e}")
        if self.ws_app:
            self.ws_app.close()
        print("Stopped listening.")
