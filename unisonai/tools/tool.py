from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field as PydanticField, validator
import time
import traceback

from ..types import ToolParameter, ToolExecutionResult, ParameterDict


class Field:
    """Legacy Field class for backward compatibility"""
    def __init__(self, name: str, description: str, default_value=None, required: bool = True):
        self.name = name
        self.description = description
        self.default_value = default_value
        self.required = required

    def format(self):  # Method to convert Field to dictionary
        return f"""
     {self.name}:
       - description: {self.description}
       - default_value: {self.default_value}
       - required: {self.required}
        """

    def to_tool_parameter(self) -> ToolParameter:
        """Convert legacy Field to new ToolParameter"""
        # Try to infer type from default value if available
        param_type = ToolParameterType.STRING  # Default
        
        if self.default_value is not None:
            if isinstance(self.default_value, bool):
                param_type = ToolParameterType.BOOLEAN
            elif isinstance(self.default_value, int):
                param_type = ToolParameterType.INTEGER
            elif isinstance(self.default_value, float):
                param_type = ToolParameterType.FLOAT
            elif isinstance(self.default_value, list):
                param_type = ToolParameterType.LIST
            elif isinstance(self.default_value, dict):
                param_type = ToolParameterType.DICT
        
        return ToolParameter(
            name=self.name,
            description=self.description,
            default_value=self.default_value,
            required=self.required,
            param_type=param_type  # Use inferred or default type
        )


class ToolMetadata(BaseModel):
    """Metadata for tool registration and discovery"""
    name: str = PydanticField(..., description="Tool name")
    description: str = PydanticField(..., description="Tool description")
    version: str = PydanticField(default="1.0.0", description="Tool version")
    author: Optional[str] = PydanticField(default=None, description="Tool author")
    tags: List[str] = PydanticField(default_factory=list, description="Tool tags for categorization")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Tool name cannot be empty")
        return v.strip()


class BaseTool(ABC):
    """Enhanced base class for tools with strong typing and validation"""
    
    def __init__(self):
        self._metadata: Optional[ToolMetadata] = None
        self._parameters: List[ToolParameter] = []
        self._legacy_params: List[Field] = []  # For backward compatibility
        self._name: str = ""
        self._description: str = ""
        
    @property
    def name(self) -> str:
        """Tool name"""
        return self._name
    
    @name.setter  
    def name(self, value: str):
        """Set tool name"""
        self._name = value
    
    @property
    def description(self) -> str:
        """Tool description"""
        return self._description
    
    @description.setter
    def description(self, value: str):
        """Set tool description"""
        self._description = value
    
    @property
    def params(self) -> List[Field]:
        """Legacy params property for backward compatibility"""
        return self._legacy_params
    
    @params.setter
    def params(self, value: List[Field]):
        """Set legacy params and convert to new format"""
        self._legacy_params = value
        self._parameters = [field.to_tool_parameter() for field in value]
    
    @property
    def parameters(self) -> List[ToolParameter]:
        """Get tool parameters with strong typing"""
        return self._parameters
    
    @parameters.setter
    def parameters(self, value: List[ToolParameter]):
        """Set tool parameters"""
        self._parameters = value
        # Update legacy params for backward compatibility
        self._legacy_params = [
            Field(
                name=param.name,
                description=param.description,
                default_value=param.default_value,
                required=param.required
            ) for param in value
        ]
    
    @property
    def metadata(self) -> Optional[ToolMetadata]:
        """Get tool metadata"""
        return self._metadata
    
    @metadata.setter
    def metadata(self, value: ToolMetadata):
        """Set tool metadata"""
        self._metadata = value
    
    def validate_parameters(self, kwargs: ParameterDict) -> Dict[str, Any]:
        """Validate input parameters against tool parameter definitions"""
        validated_params = {}
        errors = []
        
        for param in self._parameters:
            value = kwargs.get(param.name)
            
            # Handle default values
            if value is None and param.default_value is not None:
                value = param.default_value
            
            # Validate parameter
            if not param.validate_value(value):
                if param.required:
                    errors.append(f"Invalid or missing required parameter '{param.name}'")
                continue
                
            validated_params[param.name] = value
        
        if errors:
            raise ValueError(f"Parameter validation failed: {'; '.join(errors)}")
            
        return validated_params
    
    def execute(self, **kwargs) -> ToolExecutionResult:
        """Execute the tool with validation and error handling"""
        start_time = time.time()
        
        try:
            # Validate parameters
            validated_params = self.validate_parameters(kwargs)
            
            # Execute tool logic
            result = self._run(**validated_params)
            
            execution_time = time.time() - start_time
            
            return ToolExecutionResult(
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tool execution failed: {str(e)}"
            
            return ToolExecutionResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
    
    @abstractmethod
    def _run(self, **kwargs) -> Any:
        """Tool implementation logic - must be implemented by subclasses"""
        raise NotImplementedError("Please implement the logic in _run function")
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """Get parameter schema for documentation or UI generation"""
        schema = {
            "tool_name": self.name,
            "description": self.description,
            "parameters": []
        }
        
        for param in self._parameters:
            param_schema = {
                "name": param.name,
                "description": param.description,
                "type": param.param_type.value,
                "required": param.required,
                "default": param.default_value
            }
            
            if param.min_value is not None:
                param_schema["min_value"] = param.min_value
            if param.max_value is not None:
                param_schema["max_value"] = param.max_value
            if param.choices is not None:
                param_schema["choices"] = param.choices
                
            schema["parameters"].append(param_schema)
        
        return schema