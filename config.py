"""
Configuration management module for the counseling system.
Centralizes all API keys, model configurations, and system settings.
"""

import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class APIConfig:
    """Configuration for API clients."""
    # API Keys - should be moved to environment variables in production
    ZHIPU_API_KEY: str = "fcd304020e694f57a7fb12e931f74604.U7fhzViGNy1e7duY"
    QWEN_API_KEY: str = "sk-e869309a727b40a99eac3c179089eaee"
    MOONSHOT_API_KEY: str = "sk-TVMdFv24q3FCZMobyEndcCpcOl3Z7hNBSim0lAPX5HbIyjGp"
    OPENAI_PROXY_API_KEY: str = "sk-ygdY7On6HHOlmy3mCw56bi7QNPaWvvQ5XlZ3C2LfbsiOx5OL"
    
    # Base URLs
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    MOONSHOT_BASE_URL: str = "https://api.moonshot.cn/v1"
    OPENAI_PROXY_BASE_URL: str = "https://api.openai-proxy.org/v1"


@dataclass
class ModelConfig:
    """Configuration for different AI models."""
    # Primary models
    REASONING_MODEL: str = "deepseek-r1"
    CONVERSATION_MODEL: str = "qwen-plus"
    SUMMARY_MODEL: str = "qwen-max"
    
    # Model parameters
    DEFAULT_TEMPERATURE: float = 0.8
    REASONING_TEMPERATURE: float = 0.9
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1


@dataclass
class SystemConfig:
    """Configuration for system behavior."""
    # Dialogue limits
    MAX_DIALOGUE_LENGTH: int = 4
    DOCTOR_PATIENT_MAX_LENGTH: int = 50
    
    # Summary settings
    SUMMARY_START_SIZE: int = 13
    SUMMARY_BUFFER_SIZE: int = 6
    SUMMARY_RECENT_TURNS: int = 8
    
    # Modification limits
    MAX_MODIFICATION_ATTEMPTS: int = 3
    
    # File processing
    LOG_FILE: str = "processed_file.log"
    
    # CBT model age thresholds
    CBT_WITH_SUGGESTION_THRESHOLD: int = 400
    CBT_WITHOUT_SUGGESTION_THRESHOLD: int = 700


@dataclass
class PathConfig:
    """Configuration for file paths."""
    # Default directories
    DIALOGUE_FOLDER: str = "Adialogue_files"
    WITH_SUGGESTION_PATH: str = "Awith_suggestion"
    HALF_SUGGESTION_PATH: str = "Ahalf_suggestion"
    WITHOUT_SUGGESTION_PATH: str = "Awithout_suggestion"
    
    # File extensions
    JSON_EXT: str = ".json"
    TXT_EXT: str = ".txt"


class ConfigManager:
    """Manages all configuration settings."""
    
    def __init__(self):
        self.api = APIConfig()
        self.model = ModelConfig()
        self.system = SystemConfig()
        self.paths = PathConfig()
        
    def load_from_env(self):
        """Load configuration from environment variables."""
        # Load API keys from environment variables if available
        self.api.ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", self.api.ZHIPU_API_KEY)
        self.api.QWEN_API_KEY = os.getenv("QWEN_API_KEY", self.api.QWEN_API_KEY)
        self.api.MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", self.api.MOONSHOT_API_KEY)
        self.api.OPENAI_PROXY_API_KEY = os.getenv("OPENAI_PROXY_API_KEY", self.api.OPENAI_PROXY_API_KEY)
        
        # Load other configurations
        self.system.MAX_DIALOGUE_LENGTH = int(os.getenv("MAX_DIALOGUE_LENGTH", self.system.MAX_DIALOGUE_LENGTH))
        self.model.DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", self.model.DEFAULT_TEMPERATURE))
        
    def validate_config(self) -> bool:
        """Validate that all required configurations are present."""
        required_keys = [
            self.api.ZHIPU_API_KEY,
            self.api.QWEN_API_KEY,
            self.api.MOONSHOT_API_KEY
        ]
        
        for key in required_keys:
            if not key or key == "":
                return False
        
        return True
    
    def get_model_params(self, model_type: str = "default") -> Dict[str, Any]:
        """Get model parameters based on model type."""
        base_params = {
            "temperature": self.model.DEFAULT_TEMPERATURE,
            "max_retries": self.model.MAX_RETRIES,
            "retry_delay": self.model.RETRY_DELAY
        }
        
        if model_type == "reasoning":
            base_params["temperature"] = self.model.REASONING_TEMPERATURE
        
        return base_params


# Global configuration instance
config = ConfigManager()

# Load configuration from environment on import
config.load_from_env() 