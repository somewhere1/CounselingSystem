"""
Dialogue management module for the counseling system.
Handles conversation history, format transformations, and summary management.
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import json
import logging
from .config import config
from .llm_client import get_llm_client
from .prompts import PromptManager

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """Represents a single conversation turn."""
    role: str  # "咨询师" or "求助者"
    content: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DialogueHistory:
    """Manages conversation history and transformations."""
    
    def __init__(self):
        self.turns: List[ConversationTurn] = []
        self.summary_history: List[str] = []
        self.current_summary: str = ""
        
    def add_turn(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a conversation turn."""
        turn = ConversationTurn(role=role, content=content, metadata=metadata)
        self.turns.append(turn)
        logger.debug(f"Added turn: {role} - {content[:50]}...")
    
    def get_turns(self) -> List[ConversationTurn]:
        """Get all conversation turns."""
        return self.turns
    
    def get_recent_turns(self, count: int) -> List[ConversationTurn]:
        """Get recent conversation turns."""
        return self.turns[-count:] if count > 0 else []
    
    def get_turn_count(self) -> int:
        """Get total number of turns."""
        return len(self.turns)
    
    def to_dict_format(self) -> List[Dict[str, str]]:
        """Convert to dictionary format for compatibility."""
        result = []
        for turn in self.turns:
            result.append({turn.role: turn.content})
        return result
    
    def to_openai_format(self, identity: str) -> List[Dict[str, str]]:
        """
        Convert to OpenAI message format.
        
        Args:
            identity: "Doctor" or "Patient" to determine role mapping
        """
        result = []
        
        for i, turn in enumerate(self.turns):
            if identity == "Doctor":
                if i % 2 == 0:
                    # Even index: user message (patient)
                    if turn.role == "求助者":
                        result.append({"role": "user", "content": turn.content})
                    else:
                        result.append({"role": "assistant", "content": turn.content})
                else:
                    # Odd index: assistant message (doctor)
                    if turn.role == "咨询师":
                        result.append({"role": "assistant", "content": turn.content})
                    else:
                        result.append({"role": "user", "content": turn.content})
            else:  # Patient
                if i % 2 == 0:
                    # Even index: assistant message (patient)
                    if turn.role == "求助者":
                        result.append({"role": "assistant", "content": turn.content})
                    else:
                        result.append({"role": "user", "content": turn.content})
                else:
                    # Odd index: user message (doctor)
                    if turn.role == "咨询师":
                        result.append({"role": "user", "content": turn.content})
                    else:
                        result.append({"role": "assistant", "content": turn.content})
        
        return result
    
    def to_doctor_first_format(self, identity: str) -> List[Dict[str, str]]:
        """
        Convert to OpenAI format when doctor speaks first.
        
        Args:
            identity: "Doctor" or "Patient" to determine role mapping
        """
        result = []
        
        for i, turn in enumerate(self.turns):
            if identity == "Doctor":
                if i % 2 == 0:
                    # Even index: doctor speaks first
                    if turn.role == "咨询师":
                        result.append({"role": "assistant", "content": turn.content})
                    else:
                        result.append({"role": "user", "content": turn.content})
                else:
                    # Odd index: patient responds
                    if turn.role == "求助者":
                        result.append({"role": "user", "content": turn.content})
                    else:
                        result.append({"role": "assistant", "content": turn.content})
            else:  # Patient
                if i % 2 == 0:
                    # Even index: doctor speaks first
                    if turn.role == "咨询师":
                        result.append({"role": "user", "content": turn.content})
                    else:
                        result.append({"role": "assistant", "content": turn.content})
                else:
                    # Odd index: patient responds
                    if turn.role == "求助者":
                        result.append({"role": "assistant", "content": turn.content})
                    else:
                        result.append({"role": "user", "content": turn.content})
        
        return result
    
    def clear(self):
        """Clear all conversation history."""
        self.turns.clear()
        self.summary_history.clear()
        self.current_summary = ""
        logger.info("Conversation history cleared")
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = {
            "turns": [
                {
                    "role": turn.role,
                    "content": turn.content,
                    "timestamp": turn.timestamp,
                    "metadata": turn.metadata
                }
                for turn in self.turns
            ],
            "summary_history": self.summary_history,
            "current_summary": self.current_summary
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DialogueHistory':
        """Create from JSON string."""
        data = json.loads(json_str)
        history = cls()
        
        for turn_data in data.get("turns", []):
            turn = ConversationTurn(
                role=turn_data["role"],
                content=turn_data["content"],
                timestamp=turn_data.get("timestamp"),
                metadata=turn_data.get("metadata")
            )
            history.turns.append(turn)
        
        history.summary_history = data.get("summary_history", [])
        history.current_summary = data.get("current_summary", "")
        
        return history


class SummaryManager:
    """Manages conversation summarization."""
    
    def __init__(self):
        self.prompt_manager = PromptManager()
        self.llm_client = get_llm_client()
    
    def should_summarize(self, dialogue_history: DialogueHistory) -> bool:
        """Determine if summarization should be triggered."""
        turn_count = dialogue_history.get_turn_count()
        
        # First summary at start_size
        if turn_count == config.system.SUMMARY_START_SIZE:
            return True
        
        # Subsequent summaries at buffer_size intervals
        if turn_count > config.system.SUMMARY_START_SIZE:
            remaining_turns = turn_count - config.system.SUMMARY_START_SIZE
            return remaining_turns % config.system.SUMMARY_BUFFER_SIZE == 0
        
        return False
    
    def generate_summary(self, dialogue_history: DialogueHistory) -> str:
        """Generate summary for the conversation."""
        try:
            # Get recent turns for context
            recent_turns = dialogue_history.get_recent_turns(config.system.SUMMARY_RECENT_TURNS)
            
            # Prepare content for summarization
            full_history = dialogue_history.to_dict_format()
            recent_content = [
                {turn.role: turn.content} for turn in recent_turns
            ]
            
            # Generate summary using the prompt manager
            messages = self.prompt_manager.get_summary_prompt(
                str(full_history),
                str(recent_content)
            )
            
            summary = self.llm_client.generate_summary(messages)
            logger.info(f"Generated summary with {len(summary)} characters")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Summary generation failed: {str(e)}"
    
    def execute_summary(self, dialogue_history: DialogueHistory) -> Tuple[str, str]:
        """
        Execute summarization based on current state.
        
        Returns:
            Tuple of (content_for_processing, new_summary)
        """
        turn_count = dialogue_history.get_turn_count()
        
        if turn_count < config.system.SUMMARY_START_SIZE:
            # Not enough turns for summary
            content = str(dialogue_history.to_dict_format())
            return content, dialogue_history.current_summary
        
        if self.should_summarize(dialogue_history):
            # Generate new summary
            new_summary = self.generate_summary(dialogue_history)
            dialogue_history.current_summary = new_summary
            dialogue_history.summary_history.append(new_summary)
            logger.info("Generated new summary")
            return new_summary, new_summary
        else:
            # Use existing summary + new content
            if dialogue_history.current_summary:
                # Calculate how much new content to include
                buffer_size = config.system.SUMMARY_BUFFER_SIZE
                start_index = buffer_size * ((turn_count - 1) // buffer_size) + 1
                new_turns = dialogue_history.turns[start_index:]
                new_content = [
                    {turn.role: turn.content} for turn in new_turns
                ]
                
                content = f"历史对话摘要：{dialogue_history.current_summary}。当前聊天记录：{str(new_content)}"
                logger.info(f"Added {len(new_turns)} turns to existing summary")
                return content, dialogue_history.current_summary
            else:
                # No summary yet, use full history
                content = str(dialogue_history.to_dict_format())
                return content, dialogue_history.current_summary


class ConversationMode:
    """Defines conversation modes."""
    PATIENT_FIRST = "patient-first"
    DOCTOR_FIRST = "doctor-first"


class DialogueManager:
    """Main dialogue management class."""
    
    def __init__(self):
        self.history = DialogueHistory()
        self.summary_manager = SummaryManager()
        self.mode = ConversationMode.PATIENT_FIRST
        self.prompt_manager = PromptManager()
    
    def set_mode(self, mode: str):
        """Set conversation mode."""
        self.mode = mode
        logger.info(f"Conversation mode set to: {mode}")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation."""
        self.history.add_turn(role, content, metadata)
    
    def get_openai_messages(self, identity: str) -> List[Dict[str, str]]:
        """Get messages in OpenAI format."""
        if self.mode == ConversationMode.DOCTOR_FIRST:
            return self.history.to_doctor_first_format(identity)
        else:
            return self.history.to_openai_format(identity)
    
    def get_summary_content(self) -> Tuple[str, str]:
        """Get content for processing and current summary."""
        return self.summary_manager.execute_summary(self.history)
    
    def should_end_conversation(self) -> bool:
        """Check if conversation should end."""
        turn_count = self.history.get_turn_count()
        
        if self.mode == ConversationMode.DOCTOR_FIRST:
            return turn_count >= config.system.DOCTOR_PATIENT_MAX_LENGTH
        else:
            return turn_count >= config.system.MAX_DIALOGUE_LENGTH
    
    def get_last_message(self) -> Optional[ConversationTurn]:
        """Get the last message."""
        if self.history.turns:
            return self.history.turns[-1]
        return None
    
    def contains_goodbye(self) -> bool:
        """Check if the last message contains goodbye."""
        last_turn = self.get_last_message()
        if last_turn and last_turn.role == "咨询师":
            return "再见" in last_turn.content
        return False
    
    def export_to_dict(self) -> List[Dict[str, str]]:
        """Export conversation to dictionary format."""
        return self.history.to_dict_format()
    
    def export_to_json(self) -> str:
        """Export conversation to JSON."""
        return self.history.to_json()
    
    def import_from_dict(self, data: List[Dict[str, str]]):
        """Import conversation from dictionary format."""
        self.history.clear()
        for turn_data in data:
            for role, content in turn_data.items():
                self.history.add_turn(role, content)
    
    def clear(self):
        """Clear all conversation data."""
        self.history.clear()
        logger.info("Dialogue manager cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        counselor_turns = sum(1 for turn in self.history.turns if turn.role == "咨询师")
        patient_turns = sum(1 for turn in self.history.turns if turn.role == "求助者")
        
        return {
            "total_turns": self.history.get_turn_count(),
            "counselor_turns": counselor_turns,
            "patient_turns": patient_turns,
            "summaries_generated": len(self.history.summary_history),
            "current_summary_length": len(self.history.current_summary),
            "mode": self.mode
        } 