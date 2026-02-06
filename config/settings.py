"""
Configuration settings for the voice agent
Centralized configuration management
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    """LLM configuration settings"""
    api_key: str
    model: str = "sonar-small-chat"
    temperature: float = 0.3
    streaming: bool = True
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """Load configuration from environment variables"""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set")
        
        return cls(
            api_key=api_key,
            model=os.getenv("PERPLEXITY_MODEL", "sonar-small-chat"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            streaming=os.getenv("LLM_STREAMING", "true").lower() == "true"
        )


@dataclass
class VoiceConfig:
    """Voice interaction configuration"""
    # Speech Recognition
    recognition_timeout: float = 1.0  # Seconds to wait for speech to start
    phrase_time_limit: int = 15  # Max seconds for continuous speech
    ambient_noise_duration: float = 2.0  # Calibration duration
    
    # Text-to-Speech
    tts_language: str = "en"
    tts_slow: bool = False
    
    # Audio Playback
    audio_chunk_length: int = 500  # Milliseconds for interrupt checking
    interrupt_timeout: float = 1.0  # Max wait time for interrupt
    
    @classmethod
    def default(cls) -> 'VoiceConfig':
        """Get default voice configuration"""
        return cls()


@dataclass
class AgentConfig:
    """Agent behavior configuration"""
    conversation_history_limit: int = 10  # Number of exchanges to keep
    queue_timeout: float = 0.5  # Seconds to wait for queue items
    
    @classmethod
    def default(cls) -> 'AgentConfig':
        """Get default agent configuration"""
        return cls()


class Config:
    """Master configuration container"""
    
    def __init__(
        self,
        llm: Optional[LLMConfig] = None,
        voice: Optional[VoiceConfig] = None,
        agent: Optional[AgentConfig] = None
    ):
        self.llm = llm or LLMConfig.from_env()
        self.voice = voice or VoiceConfig.default()
        self.agent = agent or AgentConfig.default()
    
    @classmethod
    def load(cls) -> 'Config':
        """Load complete configuration"""
        return cls(
            llm=LLMConfig.from_env(),
            voice=VoiceConfig.default(),
            agent=AgentConfig.default()
        )
