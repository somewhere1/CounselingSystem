"""
LLM client management module for the counseling system.
Handles all AI service interactions with proper error handling and retry logic.
"""

import time
from typing import Dict, List, Any, Tuple, Optional
from .config import config
import logging

# Optional AI client imports with fallback
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None

try:
    from zhipuai import ZhipuAI
    HAS_ZHIPUAI = True
except ImportError:
    HAS_ZHIPUAI = False
    ZhipuAI = None

# Additional AI services (optional)
try:
    import dashscope
    HAS_DASHSCOPE = True
except ImportError:
    HAS_DASHSCOPE = False
    dashscope = None

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass


class LLMClient:
    """Manages all LLM client interactions."""
    
    def __init__(self):
        """Initialize all LLM clients."""
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all AI service clients."""
        self.available_clients = []
        
        # Initialize OpenAI-compatible clients
        if HAS_OPENAI:
            try:
                # Initialize Qwen client
                self.qwen_client = OpenAI(
                    api_key=config.api.QWEN_API_KEY,
                    base_url=config.api.QWEN_BASE_URL
                )
                self.available_clients.append("qwen")
                
                # Initialize Moonshot client
                self.moonshot_client = OpenAI(
                    api_key=config.api.MOONSHOT_API_KEY,
                    base_url=config.api.MOONSHOT_BASE_URL
                )
                self.available_clients.append("moonshot")
                
                # Initialize OpenAI proxy client
                self.openai_proxy_client = OpenAI(
                    api_key=config.api.OPENAI_PROXY_API_KEY,
                    base_url=config.api.OPENAI_PROXY_BASE_URL
                )
                self.available_clients.append("openai_proxy")
                
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI clients: {e}")
        else:
            logger.warning("OpenAI package not available. Skipping OpenAI-compatible clients.")
        
        # Initialize ZhipuAI client
        if HAS_ZHIPUAI:
            try:
                self.zhipu_client = ZhipuAI(
                    api_key=config.api.ZHIPU_API_KEY
                )
                self.available_clients.append("zhipu")
            except Exception as e:
                logger.warning(f"Failed to initialize ZhipuAI client: {e}")
        else:
            logger.warning("ZhipuAI package not available. Skipping ZhipuAI client.")
        
        # Initialize DeepSeek client (uses requests)
        if HAS_REQUESTS:
            try:
                self.deepseek_client = OpenAI(
                    api_key=config.api.QWEN_API_KEY,
                    base_url=config.api.QWEN_BASE_URL
                )  # Initialize as needed
                self.available_clients.append("deepseek")
            except Exception as e:
                logger.warning(f"Failed to initialize DeepSeek client: {e}")
        
        logger.info(f"LLM clients initialized successfully. Available clients: {self.available_clients}")
    
    def is_client_available(self, model_name: str) -> bool:
        """Check if a client is available for the given model."""
        if model_name.startswith("qwen"):
            return "qwen" in self.available_clients
        elif model_name.startswith("moonshot"):
            return "moonshot" in self.available_clients
        elif model_name.startswith("deepseek"):
            return "deepseek" in self.available_clients or "qwen" in self.available_clients
        elif model_name.startswith("gpt"):
            return "openai_proxy" in self.available_clients
        elif model_name.startswith("zhipu"):
            return "zhipu" in self.available_clients
        else:
            return len(self.available_clients) > 0

    def _get_client_by_model(self, model_name: str) -> OpenAI:
        """Get appropriate client based on model name."""
        if not self.is_client_available(model_name):
            raise LLMClientError(f"No client available for model: {model_name}")
            
        if model_name.startswith("qwen") and "qwen" in self.available_clients:
            return self.qwen_client
        elif model_name.startswith("moonshot") and "moonshot" in self.available_clients:
            return self.moonshot_client
        elif model_name.startswith("deepseek"):
            # DeepSeek models: prioritize deepseek_client, fallback to qwen if needed
            if "deepseek" in self.available_clients and self.deepseek_client is not None:
                return self.deepseek_client
            elif "qwen" in self.available_clients:
                return self.qwen_client  # fallback to qwen for deepseek models
        elif model_name.startswith("gpt") and "openai_proxy" in self.available_clients:
            return self.openai_proxy_client
        elif model_name.startswith("zhipu") and "zhipu" in self.available_clients:
            return self.zhipu_client
        else:
            # Default to first available client
            if self.available_clients:
                if "qwen" in self.available_clients:
                    return self.qwen_client
                elif "moonshot" in self.available_clients:
                    return self.moonshot_client
                elif "openai_proxy" in self.available_clients:
                    return self.openai_proxy_client
            raise LLMClientError(f"No suitable client available for model: {model_name}")
    
    def _make_request_with_retry(self, 
                                 client: OpenAI, 
                                 model: str, 
                                 messages: List[Dict], 
                                 **kwargs) -> Any:
        """Make API request with retry logic."""
        max_retries = config.model.MAX_RETRIES
        retry_delay = config.model.RETRY_DELAY
        
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message
                
            except Exception as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise LLMClientError(f"Request failed after {max_retries} attempts: {e}")
    
    def generate_response(self, 
                         model: str, 
                         messages: List[Dict], 
                         temperature: Optional[float] = None,
                         return_reasoning: bool = False) -> Tuple[str, str]:
        """
        Generate response from LLM.
        
        Args:
            model: Model name to use
            messages: List of message dictionaries
            temperature: Temperature parameter (optional)
            return_reasoning: Whether to return reasoning content (for R1 models)
            
        Returns:
            Tuple of (content, reasoning_content)
        """
        try:
            client = self._get_client_by_model(model)
            
            # Set temperature if not provided
            if temperature is None:
                if "r1" in model.lower():
                    temperature = config.model.REASONING_TEMPERATURE
                else:
                    temperature = config.model.DEFAULT_TEMPERATURE
            
            # Handle special case for deepseek-r1 timeout handling
            if model == config.model.REASONING_MODEL and return_reasoning:
                return self._handle_reasoning_request(client, model, messages, temperature)
            
            # Regular request
            response = self._make_request_with_retry(
                client, model, messages, temperature=temperature
            )
            
            return response.content, ""
            
        except Exception as e:
            logger.error(f"Error generating response with model {model}: {e}")
            raise LLMClientError(f"Response generation failed: {e}")
    
    def _handle_reasoning_request(self, 
                                 client: OpenAI, 
                                 model: str, 
                                 messages: List[Dict], 
                                 temperature: float) -> Tuple[str, str]:
        """Handle reasoning request with special timeout handling."""
        timeout_response = "Model service timeout. Please try again later."
        completion = None
        
        while completion is None or (hasattr(completion, 'content') and completion.content == timeout_response):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
                completion = response.choices[0].message
                
                # Check if response has reasoning content
                if hasattr(completion, 'reasoning_content'):
                    return completion.content, completion.reasoning_content
                else:
                    return completion.content, ""
                    
            except Exception as e:
                logger.warning(f"Reasoning request failed, retrying: {e}")
                completion = type('obj', (object,), {'content': timeout_response})()
                time.sleep(1)
        
        return completion.content, getattr(completion, 'reasoning_content', "")
    
    def generate_conversation_response(self, 
                                     messages: List[Dict], 
                                     temperature: Optional[float] = None) -> str:
        """Generate conversation response using the default conversation model."""
        content, _ = self.generate_response(
            config.model.CONVERSATION_MODEL,
            messages,
            temperature
        )
        return content
    
    def generate_summary(self, messages: List[Dict]) -> str:
        """Generate summary using the summary model."""
        content, _ = self.generate_response(
            config.model.SUMMARY_MODEL,
            messages
        )
        return content
    
    def generate_reasoning(self, messages: List[Dict]) -> Tuple[str, str]:
        """Generate reasoning using the reasoning model."""
        return self.generate_response(
            config.model.REASONING_MODEL,
            messages,
            return_reasoning=True
        )
    
    def validate_connection(self) -> Dict[str, bool]:
        """Validate all client connections."""
        results = {}
        
        test_messages = [{"role": "user", "content": "Hello, this is a test."}]
        
        # Test Qwen client
        try:
            self.qwen_client.chat.completions.create(
                model="qwen-turbo",
                messages=test_messages,
                max_tokens=10
            )
            results["qwen"] = True
        except Exception as e:
            logger.warning(f"Qwen client validation failed: {e}")
            results["qwen"] = False
        
        # Test Moonshot client
        try:
            self.moonshot_client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=test_messages,
                max_tokens=10
            )
            results["moonshot"] = True
        except Exception as e:
            logger.warning(f"Moonshot client validation failed: {e}")
            results["moonshot"] = False
        
        # Test OpenAI proxy client
        try:
            self.openai_proxy_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=test_messages,
                max_tokens=10
            )
            results["openai_proxy"] = True
        except Exception as e:
            logger.warning(f"OpenAI proxy client validation failed: {e}")
            results["openai_proxy"] = False
        
        return results


class LLMClientManager:
    """Singleton manager for LLM clients."""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._client = LLMClient()
        return cls._instance
    
    @property
    def client(self) -> LLMClient:
        """Get the LLM client instance."""
        return self._client
    
    def reinitialize(self):
        """Reinitialize the client (useful for config changes)."""
        self._client = LLMClient()


# Global client manager instance
client_manager = LLMClientManager()


def get_llm_client() -> LLMClient:
    """Get the global LLM client instance."""
    return client_manager.client


# Convenience functions for backward compatibility
def generate_response(model: str, messages: List[Dict], temperature: Optional[float] = None) -> Tuple[str, str]:
    """Generate response using the global client."""
    return get_llm_client().generate_response(model, messages, temperature)


def generate_conversation_response(messages: List[Dict], temperature: Optional[float] = None) -> str:
    """Generate conversation response using the global client."""
    return get_llm_client().generate_conversation_response(messages, temperature)


def generate_summary(messages: List[Dict]) -> str:
    """Generate summary using the global client."""
    return get_llm_client().generate_summary(messages)


def generate_reasoning(messages: List[Dict]) -> Tuple[str, str]:
    """Generate reasoning using the global client."""
    return get_llm_client().generate_reasoning(messages) 