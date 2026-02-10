"""
STT Manager using OpenAI Whisper for offline speech-to-text
"""
import os
import whisper
import tempfile
from pathlib import Path

class WhisperSTTManager:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.model_size = "base"  # Options: tiny, base, small, medium, large
        
    def load_model(self):
        """Load Whisper model (lazy loading)"""
        if self._model is None:
            print(f"🎤 Loading Whisper {self.model_size} model...")
            self._model = whisper.load_model(self.model_size)
            print(f"✅ Whisper model loaded successfully")
        return self._model
    
    def transcribe_audio(self, audio_file_path: str, language: str = "en") -> dict:
        """
        Transcribe audio file to text using Whisper
        
        Args:
            audio_file_path: Path to audio file (wav, mp3, etc.)
            language: Language code (default: "en" for English)
            
        Returns:
            dict with 'text' and 'language' keys
        """
        try:
            model = self.load_model()
            
            # Transcribe with Whisper
            result = model.transcribe(
                audio_file_path,
                language=language if language != "auto" else None,
                fp16=False  # Use FP32 for CPU compatibility
            )
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", language)
            }
            
        except Exception as e:
            print(f"❌ Whisper transcription error: {e}")
            raise
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, language: str = "en") -> dict:
        """
        Transcribe audio from bytes
        
        Args:
            audio_bytes: Audio data as bytes
            language: Language code (default: "en" for English)
            
        Returns:
            dict with 'text' and 'language' keys
        """
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            result = self.transcribe_audio(temp_path, language)
            return result
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)


# Singleton instance
def get_stt_manager() -> WhisperSTTManager:
    """Get the singleton STT manager instance"""
    return WhisperSTTManager()
