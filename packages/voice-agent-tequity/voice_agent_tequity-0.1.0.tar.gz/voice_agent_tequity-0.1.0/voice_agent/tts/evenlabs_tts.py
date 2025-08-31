# eleven_tts.py
from elevenlabs.client import ElevenLabs
from elevenlabs import play

class ElevenTTS:
    def __init__(self, api_key: str):
        """
        Initialize the ElevenLabs client.
        """
        self.client = ElevenLabs(api_key=api_key)

    def speak(self, text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
              model_id: str = "eleven_multilingual_v2",
              output_format: str = "mp3_44100_128"):
        """
        Convert text to speech and play it.
        """
        audio = self.client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format
        )
        play(audio)
        return audio  # Optional: return audio object if you want to save or process it
