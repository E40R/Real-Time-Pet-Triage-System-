"""
Voice Manager
Combines speech recognition and text-to-speech
"""
from threading import Event
from typing import Callable

from config.settings import VoiceConfig
from .speech_recognition import SpeechRecognizer
from .text_to_speech import TextToSpeech


class VoiceManager:
    """Manages all voice interactions (speech recognition + TTS)"""
    
    def __init__(self, config: VoiceConfig):
        """
        Initialize voice manager
        
        Args:
            config: Voice configuration settings
        """
        self.config = config
        self.speech_recognizer = SpeechRecognizer(config)
        self.tts = TextToSpeech(config)
    
    def listen_streaming(
        self, 
        callback: Callable[[str], None], 
        stop_event: Event
    ):
        """
        Start continuous speech recognition
        
        Args:
            callback: Function to call with recognized text
            stop_event: Event to signal when to stop
        """
        self.speech_recognizer.listen_streaming(callback, stop_event)
    
    def speak(self, text: str):
        """
        Speak text using TTS
        
        Args:
            text: Text to speak
        """
        self.tts.speak(text)
    
    def interrupt(self):
        """Interrupt current speech (barge-in)"""
        self.tts.interrupt()
    
    def is_speaking(self) -> bool:
        """
        Check if currently speaking
        
        Returns:
            True if speech is being played
        """
        return self.tts.is_currently_speaking()
