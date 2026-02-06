"""
Conversation History Manager
Handles chat history storage and formatting
"""
from typing import List


class ConversationHistory:
    """Manages conversation history with size limits"""
    
    def __init__(self, max_exchanges: int = 10):
        """
        Initialize conversation history
        
        Args:
            max_exchanges: Maximum number of exchanges to keep
        """
        self.max_exchanges = max_exchanges
        self._history: List[str] = []
    
    def add_user_message(self, message: str):
        """
        Add user message to history
        
        Args:
            message: User's message text
        """
        self._history.append(f"User: {message}")
        self._trim_history()
    
    def add_assistant_message(self, message: str):
        """
        Add assistant message to history
        
        Args:
            message: Assistant's message text
        """
        self._history.append(f"Assistant: {message}")
        self._trim_history()
    
    def _trim_history(self):
        """Keep only the last N exchanges"""
        if len(self._history) > self.max_exchanges * 2:  # *2 for user+assistant pairs
            self._history = self._history[-(self.max_exchanges * 2):]
    
    def get_context(self) -> str:
        """
        Get formatted conversation context
        
        Returns:
            Formatted conversation history as string
        """
        if not self._history:
            return ""
        return "\n".join(self._history)
    
    def get_history(self) -> List[str]:
        """
        Get raw history list
        
        Returns:
            List of conversation messages
        """
        return self._history.copy()
    
    def clear(self):
        """Clear all history"""
        self._history.clear()
    
    def __len__(self) -> int:
        """Get number of messages in history"""
        return len(self._history)
    
    def __str__(self) -> str:
        """String representation"""
        return self.get_context()
