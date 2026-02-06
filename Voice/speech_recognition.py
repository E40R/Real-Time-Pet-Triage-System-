"""
Speech Recognition Module
Handles speech-to-text conversion
"""
import speech_recognition as sr
from typing import Callable, Optional
from threading import Event

from config.settings import VoiceConfig


class SpeechRecognizer:
    """Handles speech recognition with Google Speech API"""
    
    def __init__(self, config: VoiceConfig):
        """
        Initialize speech recognizer
        
        Args:
            config: Voice configuration settings
        """
        self.config = config
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        self._calibrate()
    
    def _calibrate(self):
        """Calibrate microphone for ambient noise"""
        print("🎙️  Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(
                source, 
                duration=self.config.ambient_noise_duration
            )
        print("✅ Calibration complete.")
    
    def listen_streaming(
        self, 
        callback: Callable[[str], None], 
        stop_event: Event
    ):
        """
        Continuously listen for speech and call callback with transcribed text
        
        Args:
            callback: Function to call with transcribed text
            stop_event: Event to signal when to stop listening
        """
        with self.microphone as source:
            print("\n🎤 Listening... (speak naturally)")
            
            while not stop_event.is_set():
                try:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(
                        source,
                        timeout=self.config.recognition_timeout,
                        phrase_time_limit=self.config.phrase_time_limit
                    )
                    
                    # Transcribe using Google Speech Recognition
                    text = self.recognizer.recognize_google(audio)
                    
                    if text.strip():
                        callback(text)
                
                except sr.WaitTimeoutError:
                    # No speech detected, continue listening
                    continue
                
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    print("⚠️  Could not understand audio, please repeat")
                    continue
                
                except sr.RequestError as e:
                    # API error
                    print(f"❌ Speech recognition error: {e}")
                    continue
                
                except Exception as e:
                    # Unexpected error
                    print(f"❌ Unexpected error in speech recognition: {e}")
                    continue
    
    def recognize_once(self, audio_data) -> Optional[str]:
        """
        Recognize speech from audio data (single attempt)
        
        Args:
            audio_data: Audio data to transcribe
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            return self.recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
