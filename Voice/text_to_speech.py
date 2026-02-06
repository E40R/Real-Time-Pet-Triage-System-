"""
Text-to-Speech Module
Handles speech synthesis and playback
"""
import io
import threading
from typing import Optional

from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

from config.settings import VoiceConfig


class TextToSpeech:
    """Handles text-to-speech conversion and playback with interrupt support"""
    
    def __init__(self, config: VoiceConfig):
        """
        Initialize TTS engine
        
        Args:
            config: Voice configuration settings
        """
        self.config = config
        self.is_speaking = False
        self.should_stop_speaking = False
        self.audio_thread: Optional[threading.Thread] = None
    
    def speak(self, text: str):
        """
        Convert text to speech and play with interrupt support
        Runs in separate thread for non-blocking playback
        
        Args:
            text: Text to convert to speech
        """
        def _play_audio():
            try:
                self.is_speaking = True
                self.should_stop_speaking = False
                
                # Generate speech using Google TTS
                tts = gTTS(
                    text=text,
                    lang=self.config.tts_language,
                    slow=self.config.tts_slow
                )
                
                # Write to in-memory file
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                
                # Load audio
                audio = AudioSegment.from_mp3(fp)
                
                # Play in chunks to allow interruption
                chunk_length = self.config.audio_chunk_length
                for i in range(0, len(audio), chunk_length):
                    if self.should_stop_speaking:
                        print("\n🔇 [Audio interrupted]")
                        break
                    
                    chunk = audio[i:i + chunk_length]
                    play(chunk)
            
            except Exception as e:
                print(f"❌ Error in speech playback: {e}")
            
            finally:
                self.is_speaking = False
        
        # Run playback in separate thread
        self.audio_thread = threading.Thread(target=_play_audio, daemon=True)
        self.audio_thread.start()
    
    def interrupt(self):
        """
        Stop current speech playback (barge-in)
        Sets interrupt flag and waits for playback to stop
        """
        if self.is_speaking:
            self.should_stop_speaking = True
            if self.audio_thread:
                self.audio_thread.join(timeout=self.config.interrupt_timeout)
    
    def is_currently_speaking(self) -> bool:
        """
        Check if currently speaking
        
        Returns:
            True if speech is being played
        """
        return self.is_speaking
    
    def wait_until_finished(self, timeout: Optional[float] = None):
        """
        Wait until current speech finishes
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=timeout)
