import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration management for the Qwen-Agent chatbot system."""
    
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8002"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Model configuration
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen3:14b")
    DEFAULT_MODEL_TYPE: str = os.getenv("DEFAULT_MODEL_TYPE", "oai")
    
    # API Keys
    DASHSCOPE_API_KEY: Optional[str] = os.getenv("DASHSCOPE_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Model server configuration
    MODEL_SERVER_URL: Optional[str] = os.getenv("MODEL_SERVER_URL", "http://localhost:11434/v1")
    MODEL_SERVER_API_KEY: Optional[str] = os.getenv("MODEL_SERVER_API_KEY", "EMPTY")
    
    # Default tools
    DEFAULT_TOOLS: list = [
        "code_interpreter",
        "web_search",
        "image_gen"
    ]
    
    # System message
    DEFAULT_SYSTEM_MESSAGE: str = """You are a helpful AI assistant powered by Qwen-Agent. 
You can help users with various tasks including:
- Answering questions
- Writing and executing code
- Searching the web
- Generating images
- Analyzing documents

Please be helpful, accurate, and follow the user's instructions carefully."""
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get the default model configuration."""
        config = {
            'model': cls.DEFAULT_MODEL,
            'model_type': cls.DEFAULT_MODEL_TYPE,
        }
        
        # Add API key if available
        if cls.DEFAULT_MODEL_TYPE == "qwen_dashscope" and cls.DASHSCOPE_API_KEY:
            config['api_key'] = cls.DASHSCOPE_API_KEY
        elif cls.DEFAULT_MODEL_TYPE in ["openai", "oai"] and cls.OPENAI_API_KEY:
            config['api_key'] = cls.OPENAI_API_KEY
        
        # Add model server configuration if available
        if cls.MODEL_SERVER_URL:
            config['model_server'] = cls.MODEL_SERVER_URL
            config['api_key'] = cls.MODEL_SERVER_API_KEY
        
        return config 