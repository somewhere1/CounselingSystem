"""
Main application module for the counseling system.
Coordinates all modules and provides the primary interface.
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from .config import config
from .agents import ConversationSession, PatientAgent, CounselorAgent, get_session_manager
from .dialogue_manager import ConversationMode
from .file_utils import (
    get_file_manager, 
    get_session_data_manager, 
    get_processing_log,
    ConfigLoader
)
from .llm_client import get_llm_client
from .prompts import PromptManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CounselingSystemApp:
    """Main application class for the counseling system."""
    
    def __init__(self):
        self.file_manager = get_file_manager()
        self.session_data_manager = get_session_data_manager()
        self.processing_log = get_processing_log()
        self.session_manager = get_session_manager()
        self.llm_client = get_llm_client()
        self.prompt_manager = PromptManager()
        
        # 添加线程锁用于并发安全
        self._processing_lock = threading.Lock()
        
        logger.info("Counseling system initialized")
    
    def run_single_session(self, 
                          patient_info: str,
                          filename: str,
                          is_first_session: bool = True,
                          conversation_mode: str = ConversationMode.PATIENT_FIRST) -> Dict[str, Any]:
        """
        Run a single counseling session.
        
        Args:
            patient_info: Patient information and profile
            filename: Base filename for saving results
            is_first_session: Whether this is the first session
            conversation_mode: Conversation mode (patient-first or doctor-first)
            
        Returns:
            Dictionary containing session results
        """
        try:
            logger.info(f"Starting session for {filename}")
            
            # Create session
            session = ConversationSession(
                patient_info=patient_info,
                is_first_session=is_first_session,
                conversation_mode=conversation_mode
            )
            
            # Run the session
            session_results = session.run_full_session()
            
            # Save session results
            self._save_session_results(filename, session_results)
            
            # Mark file as processed
            self.processing_log.mark_processed(filename)
            
            logger.info(f"Session completed for {filename}")
            
            return session_results
            
        except Exception as e:
            logger.error(f"Error running session for {filename}: {e}")
            return {"error": str(e)}
    
    def _save_session_results(self, filename: str, session_results: Dict[str, Any]):
        """Save session results to files."""
        try:
            # Extract data from session results
            dialogue_history = session_results.get("dialogue_history", [])  # 经过R1推理修改的最终对话
            original_history = session_results.get("session_data", {}).get("original_dialogue_history", [])  # 未经R1修改的原始对话
            reasoning_history = session_results.get("session_data", {}).get("reasoning_history", [])
            reasoning_history_by_round = session_results.get("session_data", {}).get("reasoning_history_by_round", [])
            summary_history = session_results.get("session_data", {}).get("summary_history", [])
            modification_history = session_results.get("session_data", {}).get("modification_history", [])
            
            # Fallback: if no original history is available, use dialogue history as backup
            if not original_history:
                original_history = dialogue_history.copy()
                logger.warning("No original dialogue history found, using dialogue history as fallback")
            
            # Save all session data
            success = self.session_data_manager.save_session_results(
                filename=filename,
                dialogue_history=dialogue_history,
                reasoning_history=reasoning_history,
                summary_history=summary_history,
                modification_history=modification_history,
                original_history=original_history,
                reasoning_history_by_round=reasoning_history_by_round
            )
            
            if success:
                logger.info(f"Successfully saved session results for {filename}")
            else:
                logger.error(f"Failed to save session results for {filename}")
                
        except Exception as e:
            logger.error(f"Error saving session results for {filename}: {e}")
    
    def process_patient_folder(self, 
                             folder_path: str,
                             is_first_session: bool = True,
                             conversation_mode: str = ConversationMode.PATIENT_FIRST) -> Dict[str, Any]:
        """
        Process all patient profiles in a folder.
        
        Args:
            folder_path: Path to folder containing patient profiles
            is_first_session: Whether these are first sessions
            conversation_mode: Conversation mode to use
            
        Returns:
            Dictionary containing processing results
        """
        try:
            logger.info(f"Processing patient folder: {folder_path}")
            
            # Get list of files in folder
            files = self.file_manager.list_files(folder_path, "txt")
            
            results = {
                "total_files": len(files),
                "processed": 0,
                "skipped": 0,
                "errors": 0,
                "session_results": {}
            }
            
            for filename in files:
                try:
                    # Check if already processed
                    if self.processing_log.is_processed(filename):
                        logger.info(f"Skipping already processed file: {filename}")
                        results["skipped"] += 1
                        continue
                    
                    # Load patient profile
                    file_path = os.path.join(folder_path, filename)
                    patient_info = ConfigLoader.load_patient_profile(file_path)
                    
                    if patient_info is None:
                        logger.error(f"Failed to load patient profile: {filename}")
                        results["errors"] += 1
                        continue
                    
                    # Extract base filename (without extension)
                    base_filename = os.path.splitext(filename)[0]
                    
                    # Run session
                    session_results = self.run_single_session(
                        patient_info=patient_info,
                        filename=base_filename,
                        is_first_session=is_first_session,
                        conversation_mode=conversation_mode
                    )
                    
                    if "error" in session_results:
                        results["errors"] += 1
                    else:
                        results["processed"] += 1
                        results["session_results"][base_filename] = session_results
                    
                except Exception as e:
                    logger.error(f"Error processing file {filename}: {e}")
                    results["errors"] += 1
            
            logger.info(f"Folder processing complete. Processed: {results['processed']}, "
                       f"Skipped: {results['skipped']}, Errors: {results['errors']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing patient folder: {e}")
            return {"error": str(e)}
    
    def process_patient_folder_concurrent(self, 
                                        folder_path: str,
                                        max_workers: int = 3,
                                        is_first_session: bool = True,
                                        conversation_mode: str = ConversationMode.PATIENT_FIRST) -> Dict[str, Any]:
        """
        并发处理患者文件夹中的所有档案。
        
        Args:
            folder_path: 包含患者档案的文件夹路径
            max_workers: 最大并发线程数（默认3个，避免API限制）
            is_first_session: 是否为首次会话
            conversation_mode: 对话模式
            
        Returns:
            包含处理结果的字典
        """
        try:
            logger.info(f"Starting concurrent processing of patient folder: {folder_path}")
            logger.info(f"Max concurrent workers: {max_workers}")
            
            # 获取文件夹中的所有文件
            files = self.file_manager.list_files(folder_path, "txt")
            
            results = {
                "total_files": len(files),
                "processed": 0,
                "skipped": 0,
                "errors": 0,
                "session_results": {},
                "concurrent_workers": max_workers
            }
            
            # 过滤出需要处理的文件
            files_to_process = []
            for filename in files:
                if not self.processing_log.is_processed(filename):
                    files_to_process.append(filename)
                else:
                    logger.info(f"Skipping already processed file: {filename}")
                    results["skipped"] += 1
            
            if not files_to_process:
                logger.info("No files to process - all files already processed")
                return results
            
            logger.info(f"Processing {len(files_to_process)} files with {max_workers} concurrent workers")
            
            # 使用线程池并发处理
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_file = {}
                for filename in files_to_process:
                    future = executor.submit(
                        self._process_single_file_concurrent,
                        folder_path,
                        filename,
                        is_first_session,
                        conversation_mode
                    )
                    future_to_file[future] = filename
                
                # 收集结果
                for future in as_completed(future_to_file):
                    filename = future_to_file[future]
                    try:
                        session_results = future.result()
                        
                        with self._processing_lock:
                            if "error" in session_results:
                                results["errors"] += 1
                                logger.error(f"Error processing {filename}: {session_results['error']}")
                            else:
                                results["processed"] += 1
                                base_filename = os.path.splitext(filename)[0]
                                results["session_results"][base_filename] = session_results
                                logger.info(f"Successfully processed {filename}")
                                
                    except Exception as e:
                        with self._processing_lock:
                            results["errors"] += 1
                            logger.error(f"Exception processing {filename}: {e}")
            
            logger.info(f"Concurrent processing complete. Processed: {results['processed']}, "
                       f"Skipped: {results['skipped']}, Errors: {results['errors']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in concurrent processing: {e}")
            return {"error": str(e)}
    
    def _process_single_file_concurrent(self, 
                                       folder_path: str,
                                       filename: str,
                                       is_first_session: bool,
                                       conversation_mode: str) -> Dict[str, Any]:
        """
        并发处理单个文件的内部方法。
        
        Args:
            folder_path: 文件夹路径
            filename: 文件名
            is_first_session: 是否为首次会话
            conversation_mode: 对话模式
            
        Returns:
            会话结果字典
        """
        try:
            # 加载患者档案
            file_path = os.path.join(folder_path, filename)
            patient_info = ConfigLoader.load_patient_profile(file_path)
            
            if patient_info is None:
                return {"error": f"Failed to load patient profile: {filename}"}
            
            # 提取基础文件名（不含扩展名）
            base_filename = os.path.splitext(filename)[0]
            
            # 运行会话
            session_results = self.run_single_session(
                patient_info=patient_info,
                filename=base_filename,
                is_first_session=is_first_session,
                conversation_mode=conversation_mode
            )
            
            # 标记文件为已处理
            with self._processing_lock:
                self.processing_log.mark_processed(filename)
            
            return session_results
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            return {"error": str(e)}
    
    def generate_cbt_models(self, 
                           dialogue_folder: str,
                           with_suggestion_path: str,
                           half_suggestion_path: str,
                           without_suggestion_path: str) -> Dict[str, Any]:
        """
        Generate CBT models from dialogue files.
        
        Args:
            dialogue_folder: Path to dialogue files
            with_suggestion_path: Path for CBT models with suggestions
            half_suggestion_path: Path for CBT models with partial suggestions
            without_suggestion_path: Path for CBT models without suggestions
            
        Returns:
            Dictionary containing generation results
        """
        try:
            logger.info("Starting CBT model generation")
            
            # Get existing files to avoid duplicates
            existing_files = set()
            for folder in [with_suggestion_path, half_suggestion_path, without_suggestion_path]:
                if os.path.exists(folder):
                    existing_files.update(os.listdir(folder))
            
            # Get dialogue files
            dialogue_files = self.file_manager.list_files(dialogue_folder, "json")
            
            results = {
                "total_files": len(dialogue_files),
                "processed": 0,
                "skipped": 0,
                "errors": 0
            }
            
            for filename in dialogue_files:
                try:
                    # Extract dialogue ID from filename
                    match = re.search(r'\d+', filename)
                    if not match:
                        logger.warning(f"Could not extract ID from filename: {filename}")
                        results["errors"] += 1
                        continue
                    
                    dialogue_id = match.group(0)
                    expected_file = f"{dialogue_id}.txt"
                    
                    # Check if already exists
                    if expected_file in existing_files:
                        logger.info(f"CBT model already exists for {dialogue_id}")
                        results["skipped"] += 1
                        continue
                    
                    # Generate CBT model
                    success = self._generate_single_cbt_model(
                        dialogue_folder, 
                        filename, 
                        dialogue_id,
                        with_suggestion_path,
                        half_suggestion_path,
                        without_suggestion_path
                    )
                    
                    if success:
                        results["processed"] += 1
                    else:
                        results["errors"] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing CBT model for {filename}: {e}")
                    results["errors"] += 1
            
            logger.info(f"CBT model generation complete. Processed: {results['processed']}, "
                       f"Skipped: {results['skipped']}, Errors: {results['errors']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error generating CBT models: {e}")
            return {"error": str(e)}
    
    def _generate_single_cbt_model(self, 
                                  dialogue_folder: str,
                                  filename: str,
                                  dialogue_id: str,
                                  with_suggestion_path: str,
                                  half_suggestion_path: str,
                                  without_suggestion_path: str) -> bool:
        """Generate a single CBT model."""
        try:
            # Load dialogue data
            dialogue_path = os.path.join(dialogue_folder, filename)
            dialogue_data = self.file_manager.read_text_file(dialogue_path)
            
            if dialogue_data is None:
                logger.error(f"Failed to load dialogue data: {filename}")
                return False
            
            # Generate CBT model with suggestions
            cbt_prompt = self.prompt_manager.get_cbt_conceptualization_prompt(
                dialogue_data, 
                with_suggestion=True
            )
            cbt_model, _ = self.llm_client.generate_response(
                config.model.CONVERSATION_MODEL,
                cbt_prompt
            )
            
            # Generate events
            events_prompt = [
                {
                    "role": "system",
                    "content": "##任务：根据咨询师与求助则的对话内容，生成三个会出发用户负面情绪的场景。#格式：{\"场景一\":xxxx ,\"场景二\":xxxx,\"场景三\":xxx}.#注意事项：请严格按照格式输出，不要输出其他无关的解释。}"
                },
                {
                    "role": "user",
                    "content": f"对话内容如下：{dialogue_data}"
                }
            ]
            events_response, _ = self.llm_client.generate_response(
                config.model.CONVERSATION_MODEL,
                events_prompt
            )
            
            # Generate reactions based on dialogue_id
            dialogue_id_num = int(dialogue_id)
            
            if dialogue_id_num < config.system.CBT_WITH_SUGGESTION_THRESHOLD:
                # With suggestion
                reaction_prompt = [
                    {
                        "role": "system",
                        "content": """请你按照用户简历的认知模型以及简历中"你的成长方向（初步建议）"，生成用户"完全按照"你的成长方向（初步建议）"中的内容去应对事件时的情绪，想法和行为。#输出格式：{\"场景号\":{\"情绪\"：,\"想法\":,\"行为\":}}"""
                    },
                    {
                        "role": "user",
                        "content": f"简历信息：{cbt_model}。事件：{events_response}"
                    }
                ]
                output_path = with_suggestion_path
            elif dialogue_id_num < config.system.CBT_WITHOUT_SUGGESTION_THRESHOLD:
                # Partial suggestion
                reaction_prompt = [
                    {
                        "role": "system",
                        "content": """请你按照用户简历的认知模型，以第二人称的口吻生成用户"部分按照"你的成长方向（初步建议）"中的内容去应对事件时的情绪，想法和行为。#输出格式：{\"场景号\":{\"情绪\"：,\"想法\":,\"行为\":}}"""
                    },
                    {
                        "role": "user",
                        "content": f"简历信息：{cbt_model}。事件：{events_response}"
                    }
                ]
                output_path = half_suggestion_path
            else:
                # Without suggestion
                reaction_prompt = [
                    {
                        "role": "system",
                        "content": "请你按照用户简历的认知模型，以第二人称的口吻生成用户忽略'你的成长方向(初步建议)'中的内容去应对事件时的情绪，想法和行为。#输出格式：{\"场景号\":{\"情绪\"：,\"想法\":,\"行为\":}}"
                    },
                    {
                        "role": "user",
                        "content": f"简历信息：{cbt_model}。事件：{events_response}"
                    }
                ]
                output_path = without_suggestion_path
            
            # Generate reactions
            reactions, _ = self.llm_client.generate_response(
                config.model.CONVERSATION_MODEL,
                reaction_prompt
            )
            
            # Save CBT model
            success = self.session_data_manager.save_cbt_model(
                dialogue_id=dialogue_id,
                cbt_model=cbt_model,
                events=events_response,
                reactions=reactions
            )
            
            if success:
                logger.info(f"Successfully generated CBT model for {dialogue_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error generating CBT model for {dialogue_id}: {e}")
            return False
    
    def validate_system(self) -> Dict[str, Any]:
        """Validate system configuration and connections."""
        try:
            logger.info("Validating system configuration")
            
            # Validate configuration
            config_valid = config.validate_config()
            
            # Validate LLM connections
            llm_connections = self.llm_client.validate_connection()
            
            # Check required directories
            directories_ok = True
            required_dirs = [
                config.paths.DIALOGUE_FOLDER,
                config.paths.WITH_SUGGESTION_PATH,
                config.paths.HALF_SUGGESTION_PATH,
                config.paths.WITHOUT_SUGGESTION_PATH
            ]
            
            for directory in required_dirs:
                if not os.path.exists(directory):
                    logger.warning(f"Required directory does not exist: {directory}")
                    directories_ok = False
            
            validation_results = {
                "config_valid": config_valid,
                "llm_connections": llm_connections,
                "directories_ok": directories_ok,
                "overall_status": config_valid and any(llm_connections.values()) and directories_ok
            }
            
            logger.info(f"System validation complete. Overall status: {validation_results['overall_status']}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating system: {e}")
            return {"error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        try:
            # Get processing statistics
            processed_files = self.processing_log.get_processed_files()
            
            # Get session manager status
            active_sessions = self.session_manager.get_active_sessions()
            
            return {
                "processed_files_count": len(processed_files),
                "active_sessions_count": len(active_sessions),
                "config": {
                    "max_dialogue_length": config.system.MAX_DIALOGUE_LENGTH,
                    "max_modification_attempts": config.system.MAX_MODIFICATION_ATTEMPTS,
                    "conversation_model": config.model.CONVERSATION_MODEL,
                    "reasoning_model": config.model.REASONING_MODEL
                },
                "system_ready": True
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}


def main():
    """Main entry point for the application."""
    try:
        # Initialize the application
        app = CounselingSystemApp()
        
        # Validate system
        validation_results = app.validate_system()
        if not validation_results.get("overall_status", False):
            logger.error("System validation failed")
            return
        
        # Example usage - you can modify this based on your needs
        logger.info("Starting example processing")
        
        # Process a patient folder (example)
        # folder_path = "path/to/patient/profiles"
        # results = app.process_patient_folder(folder_path, is_first_session=True)
        # print(f"Processing results: {results}")
        
        # Generate CBT models (example)
        # cbt_results = app.generate_cbt_models(
        #     dialogue_folder="Adialogue_files",
        #     with_suggestion_path="Awith_suggestion",
        #     half_suggestion_path="Ahalf_suggestion",
        #     without_suggestion_path="Awithout_suggestion"
        # )
        # print(f"CBT generation results: {cbt_results}")
        
        logger.info("Application completed successfully")
        
    except Exception as e:
        logger.error(f"Application error: {e}")


if __name__ == "__main__":
    main() 