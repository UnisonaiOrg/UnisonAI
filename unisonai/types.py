"""
Comprehensive type definitions for UnisonAI framework
Provides strong typing using Pydantic models for better validation and developer experience
"""

from typing import Any, Dict, List, Optional, Union, Callable, Literal
from pydantic import BaseModel, Field, validator
from abc import ABC, abstractmethod
from enum import Enum


class AgentRole(str, Enum):
    """Predefined agent roles for better typing"""
    MANAGER = "manager"
    RESEARCHER = "researcher"
    WRITER = "writer"
    ANALYST = "analyst"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    CUSTOM = "custom"


class ToolParameterType(str, Enum):
    """Supported parameter types for tools"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    ANY = "any"


class MessageRole(str, Enum):
    """Standard message roles for LLM conversations"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ToolParameter(BaseModel):
    """Strongly typed tool parameter definition"""
    name: str = Field(..., description="Parameter name")
    description: str = Field(..., description="Parameter description")
    param_type: ToolParameterType = Field(default=ToolParameterType.STRING, description="Parameter type")
    default_value: Optional[Any] = Field(default=None, description="Default value")
    required: bool = Field(default=True, description="Whether parameter is required")
    min_value: Optional[Union[int, float]] = Field(default=None, description="Minimum value for numeric types")
    max_value: Optional[Union[int, float]] = Field(default=None, description="Maximum value for numeric types")
    choices: Optional[List[Any]] = Field(default=None, description="Valid choices for the parameter")

    @validator('min_value', 'max_value')
    def validate_numeric_constraints(cls, v, values):
        if v is not None and values.get('param_type') not in [ToolParameterType.INTEGER, ToolParameterType.FLOAT]:
            raise ValueError("min_value and max_value only apply to numeric types")
        return v

    def validate_value(self, value: Any) -> bool:
        """Validate a value against this parameter's constraints"""
        if self.required and value is None:
            return False
            
        if value is None:
            return True
            
        # Type validation with more flexible numeric handling
        if self.param_type == ToolParameterType.STRING and not isinstance(value, str):
            return False
        elif self.param_type == ToolParameterType.INTEGER:
            if not isinstance(value, (int, float)):
                return False
            # Allow float that is actually an integer
            if isinstance(value, float) and not value.is_integer():
                return False
        elif self.param_type == ToolParameterType.FLOAT and not isinstance(value, (int, float)):
            return False
        elif self.param_type == ToolParameterType.BOOLEAN and not isinstance(value, bool):
            return False
        elif self.param_type == ToolParameterType.LIST and not isinstance(value, list):
            return False
        elif self.param_type == ToolParameterType.DICT and not isinstance(value, dict):
            return False
            
        # Range validation for numeric types
        if self.param_type in [ToolParameterType.INTEGER, ToolParameterType.FLOAT]:
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
                
        # Choices validation
        if self.choices is not None and value not in self.choices:
            return False
            
        return True


class LLMMessage(BaseModel):
    """Strongly typed message for LLM conversations"""
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(default=None, description="Message timestamp")


class AgentConfig(BaseModel):
    """Configuration for an Agent"""
    identity: str = Field(..., description="Agent's unique identity/name")
    description: str = Field(..., description="Agent's role description")
    task: Optional[str] = Field(default=None, description="Agent's primary task")
    role: AgentRole = Field(default=AgentRole.CUSTOM, description="Agent's role type")
    verbose: bool = Field(default=True, description="Enable verbose logging")
    max_iterations: int = Field(default=10, description="Maximum iterations for task execution")
    
    @validator('identity')
    def validate_identity(cls, v):
        if not v or not v.strip():
            raise ValueError("Identity cannot be empty")
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()


class SingleAgentConfig(BaseModel):
    """Configuration for a Single_Agent"""
    identity: str = Field(..., description="Agent's unique identity/name")
    description: str = Field(..., description="Agent's purpose description")
    verbose: bool = Field(default=True, description="Enable verbose logging")
    output_file: Optional[str] = Field(default=None, description="Output file path")
    history_folder: str = Field(default="history", description="History folder path")
    max_iterations: int = Field(default=10, description="Maximum iterations for task execution")
    
    @validator('identity')
    def validate_identity(cls, v):
        if not v or not v.strip():
            raise ValueError("Identity cannot be empty")
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()


class ClanConfig(BaseModel):
    """Configuration for a Clan"""
    clan_name: str = Field(..., description="Name of the clan")
    shared_instruction: str = Field(..., description="Shared instructions for all agents")
    goal: str = Field(..., description="Clan's unified objective")
    history_folder: str = Field(default="history", description="Log/history folder")
    output_file: Optional[str] = Field(default=None, description="Final output file")
    max_rounds: int = Field(default=5, description="Maximum communication rounds")
    verbose: bool = Field(default=True, description="Enable verbose logging")
    
    @validator('clan_name')
    def validate_clan_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Clan name cannot be empty")
        return v.strip()
    
    @validator('shared_instruction')
    def validate_shared_instruction(cls, v):
        if not v or not v.strip():
            raise ValueError("Shared instruction cannot be empty")
        return v.strip()
    
    @validator('goal')
    def validate_goal(cls, v):
        if not v or not v.strip():
            raise ValueError("Goal cannot be empty")
        return v.strip()


class ToolExecutionResult(BaseModel):
    """Result of tool execution"""
    success: bool = Field(..., description="Whether execution was successful")
    result: Any = Field(default=None, description="Tool execution result")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")


class AgentCommunication(BaseModel):
    """Message between agents in a clan"""
    sender: str = Field(..., description="Sender agent identity")
    recipient: str = Field(..., description="Recipient agent identity")
    message: str = Field(..., description="Message content")
    additional_resource: Optional[str] = Field(default=None, description="Additional resource reference")
    timestamp: str = Field(..., description="Message timestamp")
    priority: Literal["low", "medium", "high"] = Field(default="medium", description="Message priority")


class TaskResult(BaseModel):
    """Result of task execution"""
    success: bool = Field(..., description="Whether task was completed successfully")
    result: str = Field(..., description="Task execution result")
    agent_identity: str = Field(..., description="Identity of the executing agent")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    iterations_used: int = Field(default=0, description="Number of iterations used")
    error: Optional[str] = Field(default=None, description="Error message if task failed")


# Type aliases for better readability
ToolFunction = Callable[..., Any]
ParameterDict = Dict[str, Any]
ToolRegistry = Dict[str, "BaseTool"]
AgentRegistry = Dict[str, "Agent"]