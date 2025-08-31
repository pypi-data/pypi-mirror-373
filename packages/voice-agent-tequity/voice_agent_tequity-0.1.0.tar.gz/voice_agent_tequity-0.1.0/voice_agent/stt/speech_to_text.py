import pyaudio
import websocket
import json
import threading
import time
import wave
from urllib.parse import urlencode
from datetime import datetime

class SpeechToText:
    def __init__(self, api_key, input_device_index=None, sample_rate=16000, channels=1):
        self.api_key = api_key
        self.sample_rate = sample_rate
        self.channels = channels
        self.input_device_index = input_device_index

        # WebSocket connection
        self.connection_params = {"sample_rate": self.sample_rate, "format_turns": True}
        self.api_endpoint_base_url = "wss://streaming.assemblyai.com/v3/ws"
        self.api_endpoint = f"{self.api_endpoint_base_url}?{urlencode(self.connection_params)}"

        # Audio configuration
        self.frames_per_buffer = 800
        self.format = pyaudio.paInt16

        # Global variables
        self.audio = None
        self.stream = None
        self.ws_app = None
        self.audio_thread = None
        self.stop_event = threading.Event()
        self.recorded_frames = []
        self.recording_lock = threading.Lock()
        self.final_text = ""

    # --- WebSocket Event Handlers ---
    def on_open(self, ws):
        print("WebSocket connection opened.")
        print(f"Connected to: {self.api_endpoint}")

        def stream_audio():
            print("Starting audio streaming...")
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
            msg_type = data.get("type")

            if msg_type == "Turn":
                transcript = data.get("transcript", "")
                formatted = data.get("turn_is_formatted", False)
                if formatted:
                    from dotenv import load_dotenv
                    load_dotenv()
                    import os 
                    from voice_agent.llm.gemini_llm import GeminiLLm
                    client = GeminiLLm(api_key=os.getenv("GOOGLE_API_KEY"))
                    # now make the llm intergeration also for the data and for the
                    #  // swapping/
                    answer = client.ask(transcript)
                    if answer:
                        print('answer got')
                        from voice_agent.tts.evenlabs_tts import ElevenTTS
                        tts = ElevenTTS(api_key=os.getenv("ELEVEN_API_KEY"))
                        tts.speak(answer)
                    print("Gemini says:", answer)
                    # Return live transcript
                    self.final_text = transcript
                    print("\r" + " " * 80 + "\r", end="")
                    # print(transcript)
        except Exception as e:
            print(f"Error handling message: {e}")

    def on_error(self, ws, error):
        print(f"\nWebSocket Error: {error}")
        self.stop_event.set()

    def on_close(self, ws, close_status_code, close_msg):
        print(f"\nWebSocket Disconnected: Status={close_status_code}, Msg={close_msg}")
        self.stop_event.set()
        self.save_wav_file()
        self.cleanup_audio()

    # --- Audio Helpers ---
    def save_wav_file(self):
        if not self.recorded_frames:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recorded_audio_{timestamp}.wav"
        try:
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                with self.recording_lock:
                    wf.writeframes(b"".join(self.recorded_frames))
            print(f"Audio saved to: {filename}")
        except Exception as e:
            print(f"Error saving WAV file: {e}")

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

