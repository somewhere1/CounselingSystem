"""
Reasoning engine module for the counseling system.
Handles R1 reasoning logic, evaluation, and modification suggestions.
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from .config import config
from .llm_client import get_llm_client
from .prompts import PromptManager, ReasoningPrompts

logger = logging.getLogger(__name__)


@dataclass
class ReasoningResult:
    """Represents the result of a reasoning operation."""
    conclusion: str  # "是" or "否"
    improvement_suggestion: str
    current_stage: str
    reasoning_content: str
    raw_response: str
    is_valid: bool = True
    error_message: Optional[str] = None


@dataclass
class ModificationRecord:
    """Represents a modification attempt."""
    attempt_number: int
    original_content: str
    improvement_suggestion: str
    modified_content: Optional[str] = None
    reasoning_result: Optional[ReasoningResult] = None


class ReasoningEngine:
    """Handles reasoning and evaluation logic for counselor responses."""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.prompt_manager = PromptManager()
        self.reasoning_prompts = ReasoningPrompts()
        
    def evaluate_response(self, 
                         is_first_session: bool,
                         is_first_evaluation: bool,
                         upper_round: int,
                         history: str,
                         modify_history: List[ModificationRecord],
                         counselor_response: str,
                         dialogue_history: List[Dict]) -> ReasoningResult:
        """
        Evaluate a counselor response using R1 reasoning.
        
        Args:
            is_first_session: Whether this is the first session
            is_first_evaluation: Whether this is the first evaluation of this response
            upper_round: Maximum number of rounds for the session
            history: Summary of conversation history
            modify_history: History of previous modifications
            counselor_response: The counselor's response to evaluate
            dialogue_history: Complete dialogue history
            
        Returns:
            ReasoningResult containing evaluation and suggestions
        """
        try:
            # Generate appropriate prompt based on session type and evaluation state
            if is_first_evaluation:
                if is_first_session:
                    messages = self.reasoning_prompts.get_first_session_prompt(
                        upper_round, history, counselor_response, dialogue_history
                    )
                else:
                    messages = self.reasoning_prompts.get_second_session_prompt(
                        upper_round, history, counselor_response, dialogue_history
                    )
                
                logger.info("🧠 Performing first evaluation of counselor response")
            else:
                # This is a revision evaluation
                modify_history_str = self._format_modify_history(modify_history)
                messages = self.reasoning_prompts.get_revision_prompt(
                    history, modify_history_str, counselor_response, is_first_session
                )
                
                logger.info("😵‍💫 Performing revision evaluation")
            
            # Get reasoning response
            content, reasoning_content = self.llm_client.generate_reasoning(messages)
            print("\n")
            print("current content:",content)
            print("\n")
            print("reasoning_content:",reasoning_content)
            # Parse the response
            result = self._parse_reasoning_response(content, reasoning_content)
            
            logger.info(f"Reasoning result: {result.conclusion}, Stage: {result.current_stage}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in reasoning evaluation: {e}")
            return ReasoningResult(
                conclusion="否",
                improvement_suggestion=f"评估过程中发生错误: {str(e)}",
                current_stage="未知",
                reasoning_content="",
                raw_response="",
                is_valid=False,
                error_message=str(e)
            )
    
    def _format_modify_history(self, modify_history: List[ModificationRecord]) -> str:
        """Format modification history for prompt."""
        if not modify_history:
            return ""
        
        history_items = []
        for i, record in enumerate(modify_history, 1):
            history_items.append(f"第{i}次修改请求: {record.improvement_suggestion}")
        
        return "; ".join(history_items)
    
    def _parse_reasoning_response(self, content: str, reasoning_content: str) -> ReasoningResult:
        """Parse the reasoning response to extract structured information."""
        # 分别匹配每个字段，避免相互干扰
        
        # 1. 匹配结论
        conclusion_pattern = r'"结论"\s*:\s*(".*?"|\S+?)(?=\s*[,}])'
        conclusion_matches = re.findall(conclusion_pattern, content, re.DOTALL)
        conclusion = "否"  # 默认值
        if conclusion_matches:
            conclusion = conclusion_matches[0].strip().strip('"')
        
        # 2. 匹配改进意见 - 停止在下一个字段或结束符号处
        suggestion_pattern = r'"改进意见"\s*:\s*(".*?"|\S.*?)(?=\s*,\s*"所处阶段"|\s*}|\s*$)'
        suggestion_matches = re.findall(suggestion_pattern, content, re.DOTALL)
        improvement_suggestion = "需要进一步改进回复内容"  # 默认值
        if suggestion_matches:
            improvement_suggestion = suggestion_matches[0].strip().strip('"')
        
        # 3. 匹配所处阶段
        stage_pattern = r'"所处阶段"\s*:\s*(".*?"|\S.*?)(?=\s*[,}]|\s*$)'
        stage_matches = re.findall(stage_pattern, content, re.DOTALL)
        current_stage = "未识别"  # 默认值
        if stage_matches:
            current_stage = stage_matches[0].strip().strip('"')
            
        print("conclusion:", conclusion)
        print("improvement_suggestion:", improvement_suggestion)
        print("current_stage:", current_stage)
        
        # 检查是否至少匹配到了结论或改进意见
        if conclusion_matches or suggestion_matches:
            return ReasoningResult(
                conclusion=conclusion,
                improvement_suggestion=improvement_suggestion,
                current_stage=current_stage,
                reasoning_content=reasoning_content,
                raw_response=content,
                is_valid=True
            )
        else:
            # Fallback: try to extract information more loosely
            logger.warning("Could not parse reasoning response with strict pattern, using fallback")
            
            # Try to find conclusion
            conclusion = "否"  # Default
            if "结论" in content:
                if "是" in content:
                    conclusion = "是"
            
            # Try to find improvement suggestion
            improvement_suggestion = "需要进一步改进回复内容"
            if "改进意见" in content:
                # Extract text after "改进意见"
                suggestion_match = re.search(r'改进意见[：:]\s*([^,}]+)', content, re.DOTALL)
                if suggestion_match:
                    improvement_suggestion = suggestion_match.group(1).strip()
            
            # Try to find current stage
            current_stage = "未识别"
            if "所处阶段" in content:
                stage_match = re.search(r'所处阶段[：:]\s*([^,}]+)', content, re.DOTALL)
                if stage_match:
                    current_stage = stage_match.group(1).strip()
            
            return ReasoningResult(
                conclusion=conclusion,
                improvement_suggestion=improvement_suggestion,
                current_stage=current_stage,
                reasoning_content=reasoning_content,
                raw_response=content,
                is_valid=False,
                error_message="Failed to parse with strict pattern"
            )
    
    def should_continue_modification(self, 
                                   result: ReasoningResult, 
                                   attempt_count: int) -> bool:
        """
        Determine if modification should continue based on result and attempt count.
        
        Args:
            result: The reasoning result
            attempt_count: Current number of modification attempts
            
        Returns:
            True if modification should continue, False otherwise
        """
        # Stop if we've reached max attempts
        if attempt_count >= config.system.MAX_MODIFICATION_ATTEMPTS:
            logger.info(f"Reached maximum modification attempts ({attempt_count})")
            return False
        
        # Stop if conclusion is positive
        if "是" in result.conclusion:
            logger.info("Reasoning conclusion is positive, stopping modification")
            return False
        
        # Continue if conclusion is negative and we haven't reached max attempts
        if "否" in result.conclusion and attempt_count < config.system.MAX_MODIFICATION_ATTEMPTS:
            logger.info(f"Continuing modification (attempt {attempt_count + 1})")
            return True
        
        # Default: stop modification
        logger.info("Stopping modification (default case)")
        return False
    
    def create_modification_prompt(self, 
                                 modify_history: List[ModificationRecord],
                                 original_response: str) -> str:
        """
        Create a modification prompt based on the history of modifications.
        
        Args:
            modify_history: List of previous modification attempts
            original_response: The original counselor response
            
        Returns:
            Modification prompt string
        """
        if not modify_history:
            logger.warning("No modification history provided")
            return ""
        
        # Format the modification history
        history_items = []
        for i, record in enumerate(modify_history, 1):
            if i == len(modify_history):
                # Current modification request
                history_items.append(f"当前修改请求: {record.improvement_suggestion}")
            else:
                # Previous modification requests
                history_items.append(f"第{i}次修改请求: {record.improvement_suggestion}")
        
        # Create the modification prompt
        prompt = (
            f"请按照修改请求的历史记录 {'; '.join(history_items)}。"
            f"和对话历史，修改当前回复：{original_response}"
        )
        
        return prompt
    
    def process_modification_cycle(self,
                                 is_first_session: bool,
                                 upper_round: int,
                                 history: str,
                                 dialogue_history: List[Dict],
                                 initial_response: str) -> Tuple[str, List[ReasoningResult], List[ModificationRecord]]:
        """
        Process a complete modification cycle for a counselor response.
        
        Args:
            is_first_session: Whether this is the first session
            upper_round: Maximum number of rounds
            history: Conversation history summary
            dialogue_history: Complete dialogue history
            initial_response: Initial counselor response
            
        Returns:
            Tuple of (final_response, reasoning_history, modification_history)
        """
        modification_history: List[ModificationRecord] = []
        reasoning_history: List[ReasoningResult] = []
        current_response = initial_response
        attempt_count = 0
        
        while True:
            # Evaluate current response
            is_first_evaluation = (attempt_count == 0)
            result = self.evaluate_response(
                is_first_session=is_first_session,
                is_first_evaluation=is_first_evaluation,
                upper_round=upper_round,
                history=history,
                modify_history=modification_history,
                counselor_response=current_response,
                dialogue_history=dialogue_history
            )
            
            reasoning_history.append(result)
            
            # Check if we should continue modification
            if not self.should_continue_modification(result, attempt_count):
                break
            
            # Create modification record
            modification_record = ModificationRecord(
                attempt_number=attempt_count + 1,
                original_content=current_response,
                improvement_suggestion=result.improvement_suggestion,
                reasoning_result=result
            )
            modification_history.append(modification_record)
            
            # Create modification prompt
            modification_prompt = self.create_modification_prompt(
                modification_history, 
                initial_response
            )
            
            # Here you would typically call the counselor agent to generate
            # a modified response based on the modification prompt
            # For now, we'll just use the original response
            # In the full implementation, this would be:
            # current_response = counselor_agent.generate_modified_response(modification_prompt)
            
            attempt_count += 1
            
            logger.info(f"Completed modification attempt {attempt_count}")
        
        logger.info(f"Modification cycle completed with {len(reasoning_history)} evaluations")
        
        return current_response, reasoning_history, modification_history


class ReasoningCache:
    """Cache for reasoning results to avoid redundant computations."""
    
    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, ReasoningResult] = {}
        self.max_size = max_size
        self.access_order: List[str] = []
    
    def _generate_key(self, 
                     is_first_session: bool,
                     history: str,
                     counselor_response: str,
                     upper_round: int) -> str:
        """Generate a cache key for the reasoning request."""
        import hashlib
        
        key_content = f"{is_first_session}:{upper_round}:{history}:{counselor_response}"
        return hashlib.md5(key_content.encode()).hexdigest()
    
    def get(self, 
            is_first_session: bool,
            history: str,
            counselor_response: str,
            upper_round: int) -> Optional[ReasoningResult]:
        """Get cached reasoning result."""
        key = self._generate_key(is_first_session, history, counselor_response, upper_round)
        
        if key in self.cache:
            # Move to end of access order
            self.access_order.remove(key)
            self.access_order.append(key)
            logger.debug(f"Cache hit for reasoning request")
            return self.cache[key]
        
        logger.debug(f"Cache miss for reasoning request")
        return None
    
    def put(self, 
            is_first_session: bool,
            history: str,
            counselor_response: str,
            upper_round: int,
            result: ReasoningResult):
        """Cache reasoning result."""
        key = self._generate_key(is_first_session, history, counselor_response, upper_round)
        
        # Remove oldest if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = result
        
        # Update access order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        logger.debug(f"Cached reasoning result")
    
    def clear(self):
        """Clear all cached results."""
        self.cache.clear()
        self.access_order.clear()
        logger.info("Reasoning cache cleared")


# Global reasoning cache
reasoning_cache = ReasoningCache()


def get_reasoning_engine() -> ReasoningEngine:
    """Get a reasoning engine instance."""
    return ReasoningEngine() 