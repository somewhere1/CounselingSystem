"""
Agent classes for the counseling system.
Encapsulates patient and counselor behavior and response generation.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from .config import config
from .llm_client import get_llm_client
from .prompts import PromptManager
from .dialogue_manager import DialogueManager, ConversationMode
from .reasoning_engine import ReasoningEngine, ReasoningResult, ModificationRecord
from .utils.sentence_rewriter import CounselorResponseEnhancer

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Represents a response from an agent."""
    content: str
    metadata: Optional[Dict[str, Any]] = None
    reasoning_data: Optional[Dict[str, Any]] = None
    modification_history: Optional[List[ModificationRecord]] = None


class BaseAgent(ABC):
    """Base class for all agents in the counseling system."""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.llm_client = get_llm_client()
        self.prompt_manager = PromptManager()
        
    @abstractmethod
    def generate_response(self, 
                         dialogue_manager: DialogueManager,
                         context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Generate a response based on the current dialogue state."""
        pass
    
    def _prepare_messages(self, 
                         system_message: str, 
                         dialogue_manager: DialogueManager,
                         identity: str) -> List[Dict[str, str]]:
        """Prepare messages for LLM interaction."""
        openai_messages = dialogue_manager.get_openai_messages(identity)
        return [{"role": "system", "content": system_message}] + openai_messages


class PatientAgent(BaseAgent):
    """Represents a patient/client in the counseling session."""
    
    def __init__(self, patient_info: str):
        super().__init__("patient")
        self.patient_info = patient_info
        self.system_message = self.prompt_manager.get_patient_system_message(patient_info)
        
    def generate_response(self, 
                         dialogue_manager: DialogueManager,
                         context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Generate a patient response."""
        try:
            # Prepare messages based on conversation mode
            identity = "Patient"
            messages = self._prepare_messages(self.system_message, dialogue_manager, identity)
            
            # Generate response
            response = self.llm_client.generate_conversation_response(messages)
            
            logger.info(f"Patient: {response}")
            
            # Create metadata
            metadata = {
                "agent_type": self.agent_type,
                "patient_info_length": len(self.patient_info),
                "message_count": len(messages)
            }
            
            return AgentResponse(
                content=response,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error generating patient response: {e}")
            return AgentResponse(
                content="我现在有点不太知道该说什么...",
                metadata={"error": str(e)}
            )
    
    def update_patient_info(self, new_info: str):
        """Update patient information."""
        self.patient_info = new_info
        self.system_message = self.prompt_manager.get_patient_system_message(new_info)
        logger.info("Patient information updated")


class CounselorAgent(BaseAgent):
    """Represents a counselor in the counseling session."""
    
    def __init__(self, is_first_session: bool = True):
        super().__init__("counselor")
        self.is_first_session = is_first_session
        self.reasoning_engine = ReasoningEngine()
        self.modification_suggestion = ""
        self.response_enhancer = CounselorResponseEnhancer()
        
    def generate_response(self, 
                         dialogue_manager: DialogueManager,
                         context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Generate a counselor response with reasoning and modification."""
        try:
            # Get summary content for processing
            content, summary = dialogue_manager.get_summary_content()
            
            # Initialize modification tracking
            modification_history: List[ModificationRecord] = []
            reasoning_history: List[ReasoningResult] = []
            revising_flag = 0
            
            # Generate the original response (before any R1 reasoning modifications)
            original_response = self._generate_counselor_response(dialogue_manager, "")
            current_response = original_response
            
            while True:
                
                # Evaluate response with reasoning engine
                if not modification_history:
                    # First evaluation
                    result = self.reasoning_engine.evaluate_response(
                        is_first_session=self.is_first_session,
                        is_first_evaluation=True,
                        upper_round=50,  # Could be configurable
                        history=content,
                        modify_history=modification_history,
                        counselor_response=current_response,
                        dialogue_history=dialogue_manager.export_to_dict()
                    )
                else:
                    # Revision evaluation
                    result = self.reasoning_engine.evaluate_response(
                        is_first_session=self.is_first_session,
                        is_first_evaluation=False,
                        upper_round=50,
                        history=content,
                        modify_history=modification_history,
                        counselor_response=current_response,
                        dialogue_history=dialogue_manager.export_to_dict()
                    )
                
                reasoning_history.append(result)
                
                # Check if we should continue modification
                if ("是" in result.conclusion) or revising_flag >= config.system.MAX_MODIFICATION_ATTEMPTS:
                    # Response is acceptable or max attempts reached
                    # Enhance the response with sentence rewriter
                    dialogue_context = {
                        'current_stage': result.current_stage,
                        'patient_emotion': '平静',  # Could be extracted from context
                        'session_type': '首次会话' if self.is_first_session else '后续会话'
                    }
                    current_response = self.response_enhancer.enhance_response(
                        current_response, 
                        dialogue_context
                    )
                    break
                
                # Create modification record
                modification_record = ModificationRecord(
                    attempt_number=revising_flag + 1,
                    original_content=current_response,
                    improvement_suggestion=result.improvement_suggestion,
                    reasoning_result=result
                )
                modification_history.append(modification_record)
                
                # Create modification prompt
                self.modification_suggestion = self.reasoning_engine.create_modification_prompt(
                    modification_history,
                    current_response
                )
                
                # Generate new response based on modification suggestion
                current_response = self._generate_counselor_response(
                    dialogue_manager, 
                    self.modification_suggestion
                )
                
                revising_flag += 1
                logger.info(f"Modification attempt {revising_flag}: Generated new response based on feedback")
            
            # Clear modification suggestion for next response
            self.modification_suggestion = ""
            
            logger.info(f"Counselor: {current_response}")
            
            # Create metadata
            metadata = {
                "agent_type": self.agent_type,
                "modification_attempts": revising_flag,
                "final_conclusion": result.conclusion,
                "current_stage": result.current_stage,
                "is_first_session": self.is_first_session
            }
            
            # Create reasoning data
            reasoning_data = {
                "original_response": original_response,  # 保存原始回复
                "reasoning_history": [
                    {
                        "conclusion": r.conclusion,
                        "improvement_suggestion": r.improvement_suggestion,
                        "current_stage": r.current_stage,
                        "reasoning_content": r.reasoning_content
                    }
                    for r in reasoning_history
                ],
                "modification_history": [
                    {
                        "attempt_number": m.attempt_number,
                        "improvement_suggestion": m.improvement_suggestion
                    }
                    for m in modification_history
                ]
            }
            
            return AgentResponse(
                content=current_response,
                metadata=metadata,
                reasoning_data=reasoning_data,
                modification_history=modification_history
            )
            
        except Exception as e:
            logger.error(f"Error generating counselor response: {e}")
            return AgentResponse(
                content="我需要一点时间来思考，让我们稍后继续。",
                metadata={"error": str(e)}
            )
    
    def _generate_counselor_response(self, 
                                   dialogue_manager: DialogueManager,
                                   modification_suggestion: str) -> str:
        """Generate a counselor response."""
        # Prepare system message
        system_message = self.prompt_manager.get_counselor_system_message(modification_suggestion)
        
        # Prepare messages
        identity = "Doctor"
        messages = self._prepare_messages(system_message, dialogue_manager, identity)
        
        # Generate response
        response = self.llm_client.generate_conversation_response(
            messages, 
            temperature=config.model.DEFAULT_TEMPERATURE
        )
        
        return response
    
    def set_session_type(self, is_first_session: bool):
        """Set whether this is the first session."""
        self.is_first_session = is_first_session
        logger.info(f"Session type set to: {'first' if is_first_session else 'subsequent'}")


class ConversationSession:
    """Manages a complete counseling conversation session."""
    
    def __init__(self, 
                 patient_info: str,
                 is_first_session: bool = True,
                 conversation_mode: str = ConversationMode.PATIENT_FIRST):
        self.prompt_manager = PromptManager()
        self.patient_agent = PatientAgent(patient_info)
        self.counselor_agent = CounselorAgent(is_first_session)
        self.dialogue_manager = DialogueManager()
        self.dialogue_manager.set_mode(conversation_mode)
        
        self.session_data = {
            "reasoning_history_by_round": [],  # 按轮次分组: [{"round": 1, "counselor_response": "...", "reasoning_history": [...]}]
            "reasoning_history": [],  # 保留原格式以兼容现有逻辑
            "modification_history": [],
            "summary_history": [],
            "original_dialogue_history": []  # 保存原始对话历史（未经R1修改的咨询师回复）
        }
        self.current_counselor_round = 0  # 当前咨询师回复轮次计数器
        
        logger.info(f"Session initialized: {'first' if is_first_session else 'subsequent'}, mode: {conversation_mode}")
    
    def start_session(self) -> str:
        """Start the conversation session."""
        # Generate opening statement based on mode
        if self.dialogue_manager.mode == ConversationMode.DOCTOR_FIRST:
            opening = self.prompt_manager.openings.get_random_opening("counselor")
            self.dialogue_manager.add_message("咨询师", opening)
            logger.info(f"Session started with counselor opening: {opening}")
            return opening
        else:
            opening = self.prompt_manager.openings.get_random_opening("general")
            self.dialogue_manager.add_message("求助者", opening)
            logger.info(f"Session started with patient opening: {opening}")
            return opening
    
    def get_next_response(self) -> Tuple[str, str, AgentResponse]:
        """
        Get the next response in the conversation.
        
        Returns:
            Tuple of (role, content, agent_response)
        """
        try:
            # Determine who should respond next
            last_message = self.dialogue_manager.get_last_message()
            
            if last_message is None:
                # No messages yet, start the session
                opening = self.start_session()
                if self.dialogue_manager.mode == ConversationMode.DOCTOR_FIRST:
                    return "咨询师", opening, AgentResponse(content=opening)
                else:
                    return "求助者", opening, AgentResponse(content=opening)
            
            # Generate response from the other agent
            if last_message.role == "求助者":
                # Patient spoke last, counselor responds
                self.current_counselor_round += 1  # 增加咨询师回复轮次
                
                agent_response = self.counselor_agent.generate_response(self.dialogue_manager)
                role = "咨询师"
                
                # Store reasoning data
                if agent_response.reasoning_data:
                    reasoning_data = agent_response.reasoning_data.get("reasoning_history", [])
                    original_response = agent_response.reasoning_data.get("original_response", "")
                    
                    # 保存原始对话历史（咨询师的原始回复）
                    if original_response:
                        # 添加患者的最后一条消息（如果有的话）
                        last_patient_message = self.dialogue_manager.get_last_message()
                        if last_patient_message and last_patient_message.role == "求助者":
                            # 确保患者消息已添加到原始历史中
                            if (not self.session_data["original_dialogue_history"] or 
                                self.session_data["original_dialogue_history"][-1].get("求助者") != last_patient_message.content):
                                self.session_data["original_dialogue_history"].append(
                                    {"求助者": last_patient_message.content}
                                )
                        
                        # 添加咨询师的原始回复
                        self.session_data["original_dialogue_history"].append(
                            {"咨询师": original_response}
                        )
                        logger.info(f"📝 Saved original counselor response for round {self.current_counselor_round}")
                    
                    # 按轮次分组保存推理历史
                    if reasoning_data:
                        round_data = {
                            "round": self.current_counselor_round,
                            "original_counselor_response": original_response,  # 原始回复
                            "final_counselor_response": agent_response.content,  # 最终回复
                            "reasoning_history": reasoning_data
                        }
                        self.session_data["reasoning_history_by_round"].append(round_data)
                        logger.info(f"💾 Saved {len(reasoning_data)} reasoning results for counselor round {self.current_counselor_round}")
                    
                    # 保持原有扁平结构以兼容现有逻辑
                    self.session_data["reasoning_history"].extend(reasoning_data)
                    self.session_data["modification_history"].extend(
                        agent_response.reasoning_data.get("modification_history", [])
                    )
                
            else:
                # Counselor spoke last, patient responds
                agent_response = self.patient_agent.generate_response(self.dialogue_manager)
                role = "求助者"
                
                # 患者回复直接添加到原始对话历史（患者回复不经过R1推理修改）
                self.session_data["original_dialogue_history"].append(
                    {"求助者": agent_response.content}
                )
            
            # Add message to dialogue manager
            self.dialogue_manager.add_message(role, agent_response.content, agent_response.metadata)
            
            return role, agent_response.content, agent_response
            
        except Exception as e:
            logger.error(f"Error getting next response: {e}")
            return "系统", f"会话过程中发生错误: {str(e)}", AgentResponse(content="", metadata={"error": str(e)})
    
    def should_end_session(self) -> bool:
        """Check if the session should end."""
        # Check for goodbye message
        if self.dialogue_manager.contains_goodbye():
            return True
        
        # Check for maximum length
        if self.dialogue_manager.should_end_conversation():
            return True
        
        return False
    
    def run_full_session(self) -> Dict[str, Any]:
        """Run a complete conversation session."""
        logger.info("Starting full conversation session")
        
        # Start the session
        if self.dialogue_manager.mode == ConversationMode.PATIENT_FIRST:
            self.start_session()
        
        # Run conversation loop
        while not self.should_end_session():
            try:
                role, content, agent_response = self.get_next_response()
                
                # Log the interaction
                logger.info(f"{role}: {content[:100]}...")
                
                # Check for session end conditions
                if self.should_end_session():
                    logger.info("Session ending conditions met")
                    break
                    
            except Exception as e:
                logger.error(f"Error in conversation loop: {e}")
                break
        
        # Generate session summary
        session_summary = self._generate_session_summary()
        
        logger.info(f"Session completed with {self.dialogue_manager.history.get_turn_count()} turns")
        
        return {
            "dialogue_history": self.dialogue_manager.export_to_dict(),
            "session_summary": session_summary,
            "session_data": self.session_data,
            "statistics": self.dialogue_manager.get_statistics()
        }
    
    def _generate_session_summary(self) -> Dict[str, Any]:
        """Generate a summary of the session."""
        stats = self.dialogue_manager.get_statistics()
        
        return {
            "total_turns": stats["total_turns"],
            "counselor_turns": stats["counselor_turns"],
            "patient_turns": stats["patient_turns"],
            "reasoning_evaluations": len(self.session_data["reasoning_history"]),
            "modification_attempts": len(self.session_data["modification_history"]),
            "session_type": "first" if self.counselor_agent.is_first_session else "subsequent",
            "conversation_mode": self.dialogue_manager.mode,
            "ended_with_goodbye": self.dialogue_manager.contains_goodbye()
        }
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export all session data for saving."""
        return {
            "dialogue_history": self.dialogue_manager.export_to_dict(),  # 经过R1推理修改的最终对话
            "original_dialogue_history": self.session_data["original_dialogue_history"],  # 未经R1修改的原始对话
            "reasoning_history": self.session_data["reasoning_history"],  # 原有扁平结构
            "reasoning_history_by_round": self.session_data["reasoning_history_by_round"],  # 新增按轮次分组
            "modification_history": self.session_data["modification_history"],
            "summary_history": self.session_data["summary_history"],
            "session_summary": self._generate_session_summary(),
            "patient_info": self.patient_agent.patient_info,
            "session_config": {
                "is_first_session": self.counselor_agent.is_first_session,
                "conversation_mode": self.dialogue_manager.mode,
                "total_counselor_rounds": self.current_counselor_round  # 添加总轮次信息
            }
        }


class SessionManager:
    """Manages multiple conversation sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
        self.active_sessions: List[str] = []
        
    def create_session(self, 
                      session_id: str,
                      patient_info: str,
                      is_first_session: bool = True,
                      conversation_mode: str = ConversationMode.PATIENT_FIRST) -> ConversationSession:
        """Create a new conversation session."""
        session = ConversationSession(
            patient_info=patient_info,
            is_first_session=is_first_session,
            conversation_mode=conversation_mode
        )
        
        self.sessions[session_id] = session
        self.active_sessions.append(session_id)
        
        logger.info(f"Created session {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get an existing session."""
        return self.sessions.get(session_id)
    
    def end_session(self, session_id: str):
        """End a session."""
        if session_id in self.active_sessions:
            self.active_sessions.remove(session_id)
            logger.info(f"Ended session {session_id}")
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return self.active_sessions.copy()
    
    def cleanup_sessions(self):
        """Clean up completed sessions."""
        to_remove = []
        for session_id in self.active_sessions:
            session = self.sessions.get(session_id)
            if session and session.should_end_session():
                to_remove.append(session_id)
        
        for session_id in to_remove:
            self.end_session(session_id)
        
        logger.info(f"Cleaned up {len(to_remove)} completed sessions")


# Global session manager
session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the global session manager."""
    return session_manager 