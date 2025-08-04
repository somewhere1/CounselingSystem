"""
Refactored Counseling System Package

A modular, well-structured counseling system with AI agents for patient-counselor interactions.
"""

from .main import CounselingSystemApp
from .config import config
from .agents import ConversationSession, PatientAgent, CounselorAgent
from .dialogue_manager import DialogueManager, ConversationMode
from .llm_client import get_llm_client
from .prompts import PromptManager
from .reasoning_engine import ReasoningEngine
from .file_utils import get_file_manager, get_session_data_manager

__version__ = "1.0.0"
__author__ = "Counseling System Developer"

# Public API
__all__ = [
    "CounselingSystemApp",
    "config",
    "ConversationSession",
    "PatientAgent", 
    "CounselorAgent",
    "DialogueManager",
    "ConversationMode",
    "get_llm_client",
    "PromptManager",
    "ReasoningEngine",
    "get_file_manager",
    "get_session_data_manager"
] 