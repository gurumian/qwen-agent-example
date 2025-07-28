from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class TaskType(str, Enum):
    """Enumeration of supported task types."""
    GENERAL_CHAT = "general_chat"
    CODE_EXECUTION = "code_execution"
    DOCUMENT_ANALYSIS = "document_analysis"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    WEB_SEARCH = "web_search"
    MATH_SOLVING = "math_solving"
    TEXT_SUMMARIZATION = "text_summarization"
    TRANSLATION = "translation"
    DATA_ANALYSIS = "data_analysis"


@dataclass
class TaskConfiguration:
    """Configuration for a specific task type."""
    task_type: TaskType
    name: str
    description: str
    system_message: str
    tools: List[str]
    model_config: Optional[Dict[str, Any]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    tags: List[str] = None


class TaskManager:
    """Manages task configurations and provides task-specific setups."""
    
    def __init__(self):
        self.task_configs: Dict[TaskType, TaskConfiguration] = self._initialize_task_configs()
    
    def _initialize_task_configs(self) -> Dict[TaskType, TaskConfiguration]:
        """Initialize default task configurations."""
        configs = {}
        
        # General Chat Task
        configs[TaskType.GENERAL_CHAT] = TaskConfiguration(
            task_type=TaskType.GENERAL_CHAT,
            name="General Chat",
            description="General conversation and Q&A",
            system_message="""You are a helpful AI assistant powered by Qwen-Agent. 
You can help users with various tasks including answering questions, providing information, and engaging in general conversation.

Please be helpful, accurate, and follow the user's instructions carefully.""",
            tools=[],
            temperature=0.7,
            tags=["conversation", "qa", "general"]
        )
        
        # Code Execution Task
        configs[TaskType.CODE_EXECUTION] = TaskConfiguration(
            task_type=TaskType.CODE_EXECUTION,
            name="Code Execution",
            description="Execute and analyze code",
            system_message="""You are a code execution assistant. You can write, execute, and analyze code in various programming languages.

When asked to write or execute code:
1. Write clear, well-documented code
2. Execute the code safely
3. Explain the results and any errors
4. Suggest improvements when appropriate

Always prioritize code safety and best practices.""",
            tools=["code_interpreter"],
            temperature=0.3,
            tags=["code", "programming", "execution"]
        )
        
        # Document Analysis Task
        configs[TaskType.DOCUMENT_ANALYSIS] = TaskConfiguration(
            task_type=TaskType.DOCUMENT_ANALYSIS,
            name="Document Analysis",
            description="Analyze and process documents",
            system_message="""You are a document analysis assistant. You can read, analyze, and extract information from various document types including PDFs, text files, and more.

When analyzing documents:
1. Read the document carefully
2. Extract key information and insights
3. Provide summaries and analysis
4. Answer questions about the document content
5. Identify important patterns or themes""",
            tools=["file_reader", "code_interpreter"],
            temperature=0.5,
            tags=["document", "analysis", "pdf", "text"]
        )
        
        # Image Generation Task
        configs[TaskType.IMAGE_GENERATION] = TaskConfiguration(
            task_type=TaskType.IMAGE_GENERATION,
            name="Image Generation",
            description="Generate images from text descriptions",
            system_message="""You are an image generation assistant. You can create images based on text descriptions provided by users.

When generating images:
1. Understand the user's requirements clearly
2. Create detailed, descriptive prompts
3. Generate high-quality images
4. Provide the image URLs or files
5. Suggest improvements if needed""",
            tools=["image_gen"],
            temperature=0.8,
            tags=["image", "generation", "art", "creative"]
        )
        
        # Image Analysis Task
        configs[TaskType.IMAGE_ANALYSIS] = TaskConfiguration(
            task_type=TaskType.IMAGE_ANALYSIS,
            name="Image Analysis",
            description="Analyze and describe images",
            system_message="""You are an image analysis assistant. You can analyze images and provide detailed descriptions, insights, and information about their content.

When analyzing images:
1. Provide detailed descriptions of what you see
2. Identify objects, people, scenes, and actions
3. Analyze visual elements like colors, composition, and style
4. Answer questions about the image content
5. Provide insights and interpretations""",
            tools=["image_analysis"],
            temperature=0.5,
            tags=["image", "analysis", "vision", "description"]
        )
        
        # Web Search Task
        configs[TaskType.WEB_SEARCH] = TaskConfiguration(
            task_type=TaskType.WEB_SEARCH,
            name="Web Search",
            description="Search the web for information",
            system_message="""You are a web search assistant. You can search the internet for current information and provide up-to-date answers.

When searching the web:
1. Understand the user's query clearly
2. Perform relevant searches
3. Gather and synthesize information from multiple sources
4. Provide accurate, current information
5. Cite sources when appropriate""",
            tools=["web_search"],
            temperature=0.5,
            tags=["web", "search", "information", "current"]
        )
        
        # Math Solving Task
        configs[TaskType.MATH_SOLVING] = TaskConfiguration(
            task_type=TaskType.MATH_SOLVING,
            name="Math Solving",
            description="Solve mathematical problems",
            system_message="""You are a mathematics assistant. You can solve various types of mathematical problems including algebra, calculus, statistics, and more.

When solving math problems:
1. Understand the problem clearly
2. Show your work step by step
3. Use appropriate mathematical notation
4. Verify your solutions
5. Explain the reasoning behind your approach""",
            tools=["code_interpreter"],
            temperature=0.2,
            tags=["math", "mathematics", "calculation", "problem-solving"]
        )
        
        # Text Summarization Task
        configs[TaskType.TEXT_SUMMARIZATION] = TaskConfiguration(
            task_type=TaskType.TEXT_SUMMARIZATION,
            name="Text Summarization",
            description="Summarize and condense text",
            system_message="""You are a text summarization assistant. You can create concise, accurate summaries of longer texts while preserving key information.

When summarizing text:
1. Identify the main points and key information
2. Create concise, well-structured summaries
3. Maintain accuracy and avoid distortion
4. Adapt summary length to user requirements
5. Highlight important insights and conclusions""",
            tools=[],
            temperature=0.4,
            tags=["text", "summarization", "condensation", "analysis"]
        )
        
        # Translation Task
        configs[TaskType.TRANSLATION] = TaskConfiguration(
            task_type=TaskType.TRANSLATION,
            name="Translation",
            description="Translate text between languages",
            system_message="""You are a translation assistant. You can translate text between various languages while preserving meaning, tone, and context.

When translating:
1. Maintain the original meaning and intent
2. Preserve the tone and style when appropriate
3. Consider cultural context and nuances
4. Provide accurate, natural-sounding translations
5. Explain any cultural or linguistic considerations""",
            tools=[],
            temperature=0.3,
            tags=["translation", "language", "multilingual", "communication"]
        )
        
        # Data Analysis Task
        configs[TaskType.DATA_ANALYSIS] = TaskConfiguration(
            task_type=TaskType.DATA_ANALYSIS,
            name="Data Analysis",
            description="Analyze and visualize data",
            system_message="""You are a data analysis assistant. You can analyze datasets, create visualizations, and provide insights from data.

When analyzing data:
1. Load and examine the data structure
2. Perform exploratory data analysis
3. Create appropriate visualizations
4. Identify patterns, trends, and insights
5. Provide clear explanations of findings
6. Suggest further analysis when appropriate""",
            tools=["code_interpreter"],
            temperature=0.4,
            tags=["data", "analysis", "visualization", "statistics"]
        )
        
        return configs
    
    def get_task_config(self, task_type: TaskType) -> Optional[TaskConfiguration]:
        """Get configuration for a specific task type."""
        return self.task_configs.get(task_type)
    
    def list_task_types(self) -> List[TaskType]:
        """List all available task types."""
        return list(self.task_configs.keys())
    
    def get_task_by_tags(self, tags: List[str]) -> List[TaskType]:
        """Get task types that match the given tags."""
        matching_tasks = []
        for task_type, config in self.task_configs.items():
            if any(tag in config.tags for tag in tags):
                matching_tasks.append(task_type)
        return matching_tasks
    
    def create_custom_task(
        self,
        name: str,
        description: str,
        system_message: str,
        tools: List[str],
        **kwargs
    ) -> TaskConfiguration:
        """Create a custom task configuration."""
        return TaskConfiguration(
            task_type=TaskType.GENERAL_CHAT,  # Default type for custom tasks
            name=name,
            description=description,
            system_message=system_message,
            tools=tools,
            **kwargs
        )


# Global task manager instance
task_manager = TaskManager() 