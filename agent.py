"""
Pet Health Voice Agent
Main agent orchestrator that coordinates all components
"""
import asyncio
import queue
import threading
from typing import Optional

from config import Config, PromptTemplates
from voice import VoiceManager
from chains import ReasoningChains
from utils import ConversationHistory, Logger


class PetHealthVoiceAgent:
    """Main orchestrator for real-time voice conversation"""
    
    def __init__(self, config: Config):
        """
        Initialize the voice agent
        
        Args:
            config: Complete configuration object
        """
        self.config = config
        
        # Initialize components
        self.voice_manager = VoiceManager(config.voice)
        self.reasoning_chains = ReasoningChains(config.llm)
        self.conversation_history = ConversationHistory(
            max_exchanges=config.agent.conversation_history_limit
        )
        
        # Queue for passing speech between threads
        self.pending_input_queue = queue.Queue()
        
        # Control flags
        self.is_running = False
        self.stop_event = threading.Event()
    
    def _handle_user_speech(self, text: str):
        """
        Callback for when user speech is detected
        Called by the listening thread
        
        Args:
            text: Transcribed speech text
        """
        Logger.user_speech(text)
        
        # Interrupt AI if currently speaking (barge-in)
        if self.voice_manager.is_speaking():
            Logger.info("Interrupting AI response...")
            self.voice_manager.interrupt()
        
        # Queue the input for processing
        self.pending_input_queue.put(text)
    
    async def _process_input_loop(self):
        """
        Process user inputs from queue
        Main processing loop that runs in the main thread
        """
        while self.is_running:
            try:
                # Get user input from queue (with timeout to allow loop exit)
                try:
                    user_input = self.pending_input_queue.get(
                        timeout=self.config.agent.queue_timeout
                    )
                except queue.Empty:
                    # No input yet, continue loop
                    continue
                
                # Add user message to history
                self.conversation_history.add_user_message(user_input)
                conversation_context = self.conversation_history.get_context()
                
                # Analyze and generate response using LangChain
                structured, response = await self.reasoning_chains.analyze_and_respond(
                    conversation_context,
                    user_input
                )
                
                # Log structured reasoning (for transparency)
                Logger.structured_analysis(structured)
                
                # Add assistant response to history
                self.conversation_history.add_assistant_message(response)
                
                # Speak the conversational response
                Logger.agent_response(response)
                self.voice_manager.speak(response)
            
            except Exception as e:
                Logger.error(f"Error processing input: {e}")
    
    def _listen_loop(self):
        """
        Continuous listening loop
        Runs in separate thread
        """
        self.voice_manager.listen_streaming(
            callback=self._handle_user_speech,
            stop_event=self.stop_event
        )
    
    async def start(self):
        """Start the voice agent"""
        # Print banner
        Logger.banner()
        
        # Play initial greeting
        greeting = PromptTemplates.get_greeting_prompt()
        Logger.agent_response(greeting)
        self.voice_manager.speak(greeting)
        
        # Set running flag
        self.is_running = True
        
        # Start listening thread
        listen_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True,
            name="ListeningThread"
        )
        listen_thread.start()
        
        # Start processing loop in main thread
        try:
            await self._process_input_loop()
        except KeyboardInterrupt:
            Logger.info("Shutting down agent...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the agent gracefully"""
        self.is_running = False
        self.stop_event.set()
        Logger.info("Agent stopped")
