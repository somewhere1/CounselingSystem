"""
File utilities module for the counseling system.
Handles file operations, logging, and data persistence.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from datetime import datetime
from .config import config

logger = logging.getLogger(__name__)


class FileManager:
    """Handles file operations for the counseling system."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.base_dir / config.paths.DIALOGUE_FOLDER,
            self.base_dir / config.paths.WITH_SUGGESTION_PATH,
            self.base_dir / config.paths.HALF_SUGGESTION_PATH,
            self.base_dir / config.paths.WITHOUT_SUGGESTION_PATH
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def read_json_file(self, file_path: str) -> Any:
        """Read and parse a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None
    
    def write_json_file(self, file_path: str, data: Any, indent: int = 4) -> bool:
        """Write data to a JSON file."""
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=indent)
            
            logger.debug(f"Successfully wrote JSON file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing JSON file {file_path}: {e}")
            return False
    
    def read_text_file(self, file_path: str) -> Optional[str]:
        """Read a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return None
    
    def write_text_file(self, file_path: str, content: str) -> bool:
        """Write content to a text file."""
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            logger.debug(f"Successfully wrote text file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing text file {file_path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        return Path(file_path).exists()
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """Get file size in bytes."""
        try:
            return Path(file_path).stat().st_size
        except FileNotFoundError:
            return None
    
    def list_files(self, directory: str, extension: str = "") -> List[str]:
        """List files in a directory with optional extension filter."""
        try:
            directory_path = Path(directory)
            if not directory_path.exists():
                return []
            
            if extension:
                if not extension.startswith('.'):
                    extension = '.' + extension
                return [f.name for f in directory_path.glob(f'*{extension}')]
            else:
                return [f.name for f in directory_path.iterdir() if f.is_file()]
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return []
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        try:
            Path(file_path).unlink()
            logger.debug(f"Successfully deleted file: {file_path}")
            return True
        except FileNotFoundError:
            logger.warning(f"File not found for deletion: {file_path}")
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False


class ProcessingLog:
    """Manages processing logs to track which files have been processed."""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file or config.system.LOG_FILE
        self.processed_files: Set[str] = set()
        self.load_log()
    
    def load_log(self):
        """Load the processed files log."""
        if not os.path.exists(self.log_file):
            # Create empty log file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                pass
            logger.info(f"Created new log file: {self.log_file}")
        else:
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.processed_files = set(f.read().splitlines())
                logger.info(f"Loaded {len(self.processed_files)} processed files from log")
            except Exception as e:
                logger.error(f"Error loading log file: {e}")
                self.processed_files = set()
    
    def is_processed(self, filename: str) -> bool:
        """Check if a file has been processed."""
        return filename in self.processed_files
    
    def mark_processed(self, filename: str):
        """Mark a file as processed."""
        if filename not in self.processed_files:
            self.processed_files.add(filename)
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(filename + '\n')
                logger.debug(f"Marked file as processed: {filename}")
            except Exception as e:
                logger.error(f"Error updating log file: {e}")
    
    def get_processed_files(self) -> Set[str]:
        """Get set of processed files."""
        return self.processed_files.copy()
    
    def clear_log(self):
        """Clear the processing log."""
        self.processed_files.clear()
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                pass
            logger.info("Cleared processing log")
        except Exception as e:
            logger.error(f"Error clearing log file: {e}")


class SessionDataManager:
    """Manages session data saving and loading."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.file_manager = FileManager(base_dir)
    
    def save_session_results(self, 
                           filename: str, 
                           dialogue_history: List[Dict],
                           reasoning_history: List[Dict],
                           summary_history: List[str],
                           modification_history: List[Dict],
                           original_history: List[Dict],
                           reasoning_history_by_round: Optional[List[Dict]] = None) -> bool:
        """
        Save session results to multiple files in different folders.
        
        Args:
            filename: Base filename (without extension)
            dialogue_history: Conversation history
            reasoning_history: R1 reasoning history (flat structure)
            summary_history: Summary history
            modification_history: Modification history
            original_history: Original history without R1 modifications
            reasoning_history_by_round: R1 reasoning history grouped by round (list format)
            
        Returns:
            True if all files were saved successfully
        """
        try:
            # Define folder structure
            folders = {
                "dialogue": "dialogue_files",
                "reasoning": "reasoning_files", 
                "summary": "summary_files",
                "modification": "modification_files",
                "original": "original_files"
            }
            
            # Create folders if they don't exist
            for folder_name, folder_path in folders.items():
                folder_dir = Path(folder_path)
                folder_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Ensured folder exists: {folder_path}")
            
            # Define file paths with folders
            dialogue_file = f"dialogue_files/{filename}_dialogue.json"
            reasoning_file = f"reasoning_files/{filename}_reasoning.json"
            summary_file = f"summary_files/{filename}_dialogue_summary.json"
            modification_file = f"modification_files/{filename}_comment.json"
            original_file = f"original_files/{filename}_original_dialogue.json"
            
            # Save all files
            success = True
            success &= self.file_manager.write_json_file(dialogue_file, dialogue_history)
            
            # Use grouped reasoning history if available, otherwise use flat structure
            if reasoning_history_by_round:
                success &= self.file_manager.write_json_file(reasoning_file, reasoning_history_by_round)
                logger.info(f"💾 Saved reasoning results grouped by rounds: {len(reasoning_history_by_round)} rounds")
            else:
                success &= self.file_manager.write_json_file(reasoning_file, reasoning_history)
                logger.info(f"💾 Saved reasoning results (flat structure): {len(reasoning_history)} evaluations")
            
            success &= self.file_manager.write_json_file(summary_file, summary_history)
            success &= self.file_manager.write_json_file(modification_file, modification_history)
            success &= self.file_manager.write_json_file(original_file, original_history)
            
            if success:
                logger.info(f"Successfully saved session results for {filename}")
                logger.info(f"Files saved to folders:")
                logger.info(f"  - dialogue_files/{filename}_dialogue.json")
                logger.info(f"  - reasoning_files/{filename}_reasoning.json")
                logger.info(f"  - summary_files/{filename}_dialogue_summary.json")
                logger.info(f"  - modification_files/{filename}_comment.json")
                logger.info(f"  - original_files/{filename}_original_dialogue.json")
            else:
                logger.error(f"Failed to save some session results for {filename}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving session results for {filename}: {e}")
            return False
    
    def load_session_results(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load session results from files in different folders."""
        try:
            # Define file paths with folders
            dialogue_file = f"dialogue_files/{filename}_dialogue.json"
            reasoning_file = f"reasoning_files/{filename}_reasoning.json"
            summary_file = f"summary_files/{filename}_dialogue_summary.json"
            modification_file = f"modification_files/{filename}_comment.json"
            original_file = f"original_files/{filename}_original_dialogue.json"
            
            # Load all files
            dialogue_history = self.file_manager.read_json_file(dialogue_file)
            reasoning_history = self.file_manager.read_json_file(reasoning_file)
            summary_history = self.file_manager.read_json_file(summary_file)
            modification_history = self.file_manager.read_json_file(modification_file)
            original_history = self.file_manager.read_json_file(original_file)
            
            # Check if all files were loaded
            if all(data is not None for data in [dialogue_history, reasoning_history, 
                                               summary_history, modification_history, 
                                               original_history]):
                return {
                    "dialogue_history": dialogue_history,
                    "reasoning_history": reasoning_history,
                    "summary_history": summary_history,
                    "modification_history": modification_history,
                    "original_history": original_history
                }
            else:
                logger.warning(f"Some session files missing for {filename}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading session results for {filename}: {e}")
            return None
    
    def save_cbt_model(self, 
                      dialogue_id: str, 
                      cbt_model: str,
                      events: str,
                      reactions: str) -> bool:
        """Save CBT model results."""
        try:
            # Determine output path based on dialogue_id
            id_num = int(dialogue_id)
            
            if id_num < config.system.CBT_WITH_SUGGESTION_THRESHOLD:
                output_path = self.base_dir / config.paths.WITH_SUGGESTION_PATH
            elif id_num < config.system.CBT_WITHOUT_SUGGESTION_THRESHOLD:
                output_path = self.base_dir / config.paths.HALF_SUGGESTION_PATH
            else:
                output_path = self.base_dir / config.paths.WITHOUT_SUGGESTION_PATH
            
            # Create content
            content = f"{cbt_model}\n下面是你完成第一次咨询后遇到的一些事件\n{events}\n下面是你遇到这些事件之后对应的情绪，想法和行为\n{reactions}\n"
            
            # Save to file
            file_path = output_path / f"{dialogue_id}.txt"
            success = self.file_manager.write_text_file(str(file_path), content)
            
            if success:
                logger.info(f"Successfully saved CBT model for {dialogue_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving CBT model for {dialogue_id}: {e}")
            return False


class ConfigLoader:
    """Loads configuration from various sources."""
    
    @staticmethod
    def load_patient_profile(file_path: str) -> Optional[str]:
        """Load patient profile from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            logger.error(f"Patient profile not found: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error loading patient profile: {e}")
            return None
    
    @staticmethod
    def find_dialogue_files(folder_path: str, target_chars: List[str]) -> Optional[str]:
        """Find dialogue files based on target characters."""
        try:
            files = os.listdir(folder_path)
            matching_files = [
                file for file in files 
                if all(target in file for target in target_chars)
            ]
            
            if matching_files:
                return os.path.join(folder_path, matching_files[0])
            else:
                logger.warning(f"No matching files found in {folder_path} with targets {target_chars}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding dialogue files: {e}")
            return None


class BackupManager:
    """Manages backup operations for important data."""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.file_manager = FileManager()
    
    def create_backup(self, source_path: str, backup_name: str = None) -> bool:
        """Create a backup of a file or directory."""
        try:
            source = Path(source_path)
            if not source.exists():
                logger.error(f"Source path does not exist: {source_path}")
                return False
            
            # Generate backup name if not provided
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{source.name}_{timestamp}"
            
            backup_path = self.backup_dir / backup_name
            
            if source.is_file():
                # Copy file
                content = self.file_manager.read_text_file(str(source))
                if content is not None:
                    return self.file_manager.write_text_file(str(backup_path), content)
            
            logger.info(f"Created backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def list_backups(self) -> List[str]:
        """List available backups."""
        try:
            return [f.name for f in self.backup_dir.iterdir() if f.is_file()]
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def restore_backup(self, backup_name: str, restore_path: str) -> bool:
        """Restore a backup to a specified location."""
        try:
            backup_path = self.backup_dir / backup_name
            if not backup_path.exists():
                logger.error(f"Backup not found: {backup_name}")
                return False
            
            content = self.file_manager.read_text_file(str(backup_path))
            if content is not None:
                return self.file_manager.write_text_file(restore_path, content)
            
            return False
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False


# Global file manager instance
file_manager = FileManager()
session_data_manager = SessionDataManager()
processing_log = ProcessingLog()
backup_manager = BackupManager()


def get_file_manager() -> FileManager:
    """Get the global file manager instance."""
    return file_manager


def get_session_data_manager() -> SessionDataManager:
    """Get the global session data manager instance."""
    return session_data_manager


def get_processing_log() -> ProcessingLog:
    """Get the global processing log instance."""
    return processing_log


def get_backup_manager() -> BackupManager:
    """Get the global backup manager instance."""
    return backup_manager 