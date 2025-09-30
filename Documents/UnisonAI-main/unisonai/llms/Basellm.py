from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseLLM(ABC):
    """
    A base class for interacting with language models.
    
    Attributes:
        messages (List[Dict[str, str]]): A list of messages in the conversation.
    """
    USER = "user"
    MODEL = "assistant"
    SYSTEM = "system"

    def __init__(self, 
                 messages: Optional[List[Dict[str, str]]] = None,
                 system_prompt: Optional[str] = None) -> None:
        self.messages = messages or []
        if system_prompt is not None:
            self.add_message(self.SYSTEM, system_prompt)

    def add_message(self, role: str, content: str) -> None:
        """Append a message with a given role to the conversation."""
        self.messages.append({"role": role, "content": content})

    @abstractmethod
    def run(self, prompt: str, save_messages: bool = True) -> str:
        """
        Run the model with the given prompt.
        
        Subclasses must implement this method.
        """
        pass

    def reset(self) -> None:
        """Reset the conversation messages."""
        self.messages = []