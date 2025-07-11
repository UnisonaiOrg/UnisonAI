import sys  # Added for exiting the process smoothly
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import time
import json
import os
import re
import yaml
import inspect
import colorama
from colorama import Fore, Style

from unisonai.llms.Basellm import BaseLLM
from unisonai.prompts.individual import INDIVIDUAL_PROMPT
from unisonai.async_helper import run_async_from_sync, run_sync_in_executor
from unisonai.types import SingleAgentConfig, TaskResult, ToolExecutionResult
from unisonai.tools.tool import BaseTool

colorama.init(autoreset=True)


def create_tools(tools: List[Union[BaseTool, type]]) -> Optional[str]:
    """Create formatted tool descriptions for prompt inclusion with improved typing"""
    if not tools:
        return None
        
    formatted_tools = ""
    for idx, tool in enumerate(tools, 1):
        # Instantiate the tool if it is provided as a class
        tool_instance = tool() if isinstance(tool, type) else tool
        
        formatted_tools += f"-TOOL{idx}: \n"
        formatted_tools += f"  NAME: {tool_instance.name}\n"
        formatted_tools += f"  DESCRIPTION: {tool_instance.description}\n"
        formatted_tools += "  PARAMS: "
        
        # Handle both new and legacy parameter formats
        if hasattr(tool_instance, 'parameters') and tool_instance.parameters:
            for param in tool_instance.parameters:
                formatted_tools += f"""
     {param.name}:
       - description: {param.description}
       - type: {param.param_type.value}
       - default_value: {param.default_value}
       - required: {param.required}
        """
        elif hasattr(tool_instance, 'params') and tool_instance.params:
            for field in tool_instance.params:
                # Escape curly braces to prevent format string conflicts
                field_format = field.format().replace("{", "{{").replace("}", "}}")
                formatted_tools += field_format
    
    return formatted_tools


class Single_Agent:
    """Enhanced Single Agent with strong typing and better configuration management"""
    
    def __init__(self,
                 llm: BaseLLM,
                 identity: str,
                 description: str,
                 verbose: bool = True,
                 tools: List[Union[BaseTool, type]] = None,
                 output_file: Optional[str] = None,
                 history_folder: str = "history",
                 max_iterations: int = 10):
        """
        Initialize a Single Agent with comprehensive configuration validation
        
        Args:
            llm: Language model instance for agent reasoning
            identity: Unique agent identifier/name
            description: Agent's purpose and capabilities description
            verbose: Enable detailed logging and output
            tools: List of tools available to the agent
            output_file: Optional file path for saving final results
            history_folder: Directory for storing conversation history
            max_iterations: Maximum number of reasoning iterations
        """
        # Validate configuration using Pydantic model
        self.config = SingleAgentConfig(
            identity=identity,
            description=description,
            verbose=verbose,
            output_file=output_file,
            history_folder=history_folder,
            max_iterations=max_iterations
        )
        
        # Core attributes
        self.llm = llm
        self.identity = self.config.identity
        self.description = self.config.description
        self.verbose = self.config.verbose
        self.output_file = self.config.output_file
        self.history_folder = Path(self.config.history_folder)
        self.max_iterations = self.config.max_iterations
        
        # Tool management
        self.rawtools = tools or []
        self.tools = create_tools(self.rawtools)
        self.tool_instances = self._initialize_tools()
        
        # State management
        self.ask_user = True
        self.current_iteration = 0
        self.execution_history: List[Dict[str, Any]] = []
        
        # Create history directory
        self.history_folder.mkdir(parents=True, exist_ok=True)
    
    def _initialize_tools(self) -> Dict[str, BaseTool]:
        """Initialize and validate tool instances"""
        tool_instances = {}
        
        for tool in self.rawtools:
            try:
                instance = tool() if isinstance(tool, type) else tool
                if not isinstance(instance, BaseTool):
                    if self.verbose:
                        print(f"{Fore.YELLOW}Warning: Tool {tool} does not inherit from BaseTool{Style.RESET_ALL}")
                tool_instances[instance.name] = instance
            except Exception as e:
                if self.verbose:
                    print(f"{Fore.RED}Error initializing tool {tool}: {e}{Style.RESET_ALL}")
        
        return tool_instances
    
    def _parse_and_fix_json(self, json_str: str) -> Union[Dict[str, Any], str]:
        """Parses JSON string and attempts to fix common errors with better error handling"""
        if not json_str or not isinstance(json_str, str):
            return "Error: Invalid JSON input"
            
        json_str = json_str.strip()
        if not json_str.startswith("{") or not json_str.endswith("}"):
            json_str = json_str[json_str.find("{"): json_str.rfind("}") + 1]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            if self.verbose:
                print(f"{Fore.RED}JSON Error:{Style.RESET_ALL} {e}")
            
            # Try common fixes
            json_str = json_str.replace("'", '"')
            json_str = re.sub(r",\s*}", "}", json_str)
            json_str = re.sub(r"{\s*,", "{", json_str)
            json_str = re.sub(r"\s*,\s*", ",", json_str)
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                return f"Error: Could not parse JSON - {e}"

    def _ensure_dict_params(self, params_data: Any) -> Dict[str, Any]:
        """Ensures params is a dictionary by parsing it if it's a string with improved typing"""
        if isinstance(params_data, str):
            params_data = params_data.strip()
            # Try to clean up escaped quotes first
            cleaned_params = params_data.replace('\\"', '"')
            try:
                return json.loads(cleaned_params)
            except json.JSONDecodeError as e:
                if self.verbose:
                    print(f"{Fore.YELLOW}JSON parsing error: {e}{Style.RESET_ALL}")
                try:
                    parsed = yaml.safe_load(cleaned_params)
                    if isinstance(parsed, dict):
                        return parsed
                    else:
                        return {"value": parsed}
                except yaml.YAMLError:
                    if self.verbose:
                        print(f"{Fore.RED}YAML parsing failed; returning raw text{Style.RESET_ALL}")
                    return {"raw_input": params_data}
        elif params_data is None:
            return {}
        return params_data if isinstance(params_data, dict) else {"value": params_data}

    def unleash(self, task: str) -> TaskResult:
        """
        Execute a task with enhanced error handling and result tracking
        
        Args:
            task: The task description to execute
            
        Returns:
            TaskResult with execution details and outcomes
        """
        start_time = time.time()
        self.current_iteration = 0
        
        try:
            return self._execute_task(task, start_time)
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Task execution failed: {str(e)}"
            
            if self.verbose:
                print(f"{Fore.RED}Critical Error: {error_msg}{Style.RESET_ALL}")
            
            return TaskResult(
                success=False,
                result="Task execution failed due to critical error",
                agent_identity=self.identity,
                execution_time=execution_time,
                iterations_used=self.current_iteration,
                error=error_msg
            )
    
    def _execute_task(self, task: str, start_time: float) -> TaskResult:
        """Internal task execution with iteration management"""
        self.user_task = task
        
        # Load or initialize conversation history
        self._load_history()
        
        # Initialize LLM with appropriate prompt
        self._initialize_llm()
        
        # Execute task with iteration limit
        response = self._run_task_loop()
        
        execution_time = time.time() - start_time
        
        # Save final results if output file is specified
        if self.output_file:
            self._save_results(response)
        
        return TaskResult(
            success=True,
            result=response,
            agent_identity=self.identity,
            execution_time=execution_time,
            iterations_used=self.current_iteration
        )
    
    def _load_history(self) -> None:
        """Load conversation history from file"""
        if self.history_folder:
            history_file = self.history_folder / f"{self.identity}.json"
            try:
                if history_file.exists():
                    with open(history_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        self.messages = json.loads(content) if content else []
                else:
                    history_file.touch()
                    self.messages = []
            except Exception as e:
                if self.verbose:
                    print(f"{Fore.YELLOW}Could not load history: {e}{Style.RESET_ALL}")
                self.messages = []
        else:
            self.messages = []
    
    def _initialize_llm(self) -> None:
        """Initialize LLM with proper system prompt"""
        self.llm.reset()
        
        tools_description = self.tools if self.tools else "No tools available"
        
        # Preserve LLM configuration while updating system prompt
        llm_config = {
            'messages': self.messages,
            'system_prompt': INDIVIDUAL_PROMPT.format(
                identity=self.identity,
                description=self.description,
                user_task=self.user_task,
                tools=tools_description,
            )
        }
        
        # Preserve existing LLM attributes
        if hasattr(self.llm, 'model'):
            llm_config['model'] = self.llm.model
        if hasattr(self.llm, 'temperature'):
            llm_config['temperature'] = self.llm.temperature
        if hasattr(self.llm, 'max_tokens'):
            llm_config['max_tokens'] = self.llm.max_tokens
        if hasattr(self.llm, 'verbose'):
            llm_config['verbose'] = self.llm.verbose
        if hasattr(self.llm, 'api_key'):
            llm_config['api_key'] = self.llm.api_key
        elif hasattr(self.llm, 'client') and hasattr(self.llm.client, 'api_key'):
            llm_config['api_key'] = self.llm.client.api_key
        
        self.llm.__init__(**llm_config)
    
    def _run_task_loop(self) -> str:
        """Execute the main task processing loop"""
        response = ""
        
        while self.current_iteration < self.max_iterations:
            self.current_iteration += 1
            
            if self.verbose:
                print(f"{Fore.CYAN}Iteration {self.current_iteration}/{self.max_iterations}{Style.RESET_ALL}")
            
            # Get LLM response
            if self.current_iteration == 1:
                response = self.llm.run(self.user_task)
            else:
                response = self.llm.run("Continue with the task based on the previous context.")
            
            if self.verbose:
                print(f"{Fore.GREEN}Response:{Style.RESET_ALL} {response}")
            
            # Process response and execute tools if needed
            tool_executed = self._process_response(response)
            
            # If no tools were executed and response looks complete, break
            if not tool_executed and self._is_task_complete(response):
                break
                
        return response
    
    def _is_task_complete(self, response: str) -> bool:
        """Check if the task appears to be complete based on response content"""
        # Simple heuristics to determine task completion
        completion_indicators = [
            "pass_result",
            "task complete",
            "final result",
            "conclusion",
            "summary"
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in completion_indicators)
    
    def _save_results(self, result: str) -> None:
        """Save final results to output file"""
        try:
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Agent: {self.identity}\n")
                f.write(f"Task: {self.user_task}\n")
                f.write(f"Result:\n{result}\n")
                
            if self.verbose:
                print(f"{Fore.GREEN}Results saved to: {self.output_file}{Style.RESET_ALL}")
                
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}Could not save results to {self.output_file}: {e}{Style.RESET_ALL}")

    def _process_response(self, response: str) -> bool:
        """
        Process LLM response for YAML blocks and execute tools
        
        Returns:
            bool: True if a tool was executed, False otherwise
        """
        if not response:
            return False
            
        # Extract YAML blocks from response
        yaml_blocks = self._extract_yaml_blocks(response)
        
        if not yaml_blocks:
            if self.verbose:
                print(f"{Fore.YELLOW}No YAML blocks found in response{Style.RESET_ALL}")
            return False
        
        tool_executed = False
        
        for yaml_block in yaml_blocks:
            try:
                parsed_yaml = yaml.safe_load(yaml_block)
                
                if not isinstance(parsed_yaml, dict):
                    if self.verbose:
                        print(f"{Fore.YELLOW}YAML block is not a dictionary{Style.RESET_ALL}")
                    continue
                
                # Execute tool based on parsed YAML
                if self._execute_tool_from_yaml(parsed_yaml):
                    tool_executed = True
                    
            except yaml.YAMLError as e:
                if self.verbose:
                    print(f"{Fore.RED}YAML parsing error: {e}{Style.RESET_ALL}")
                continue
                
        return tool_executed
    
    def _extract_yaml_blocks(self, response: str) -> List[str]:
        """Extract YAML code blocks from response"""
        yaml_blocks = []
        
        # Pattern for YAML code blocks
        yaml_pattern = r'```ya?ml\s*\n(.*?)\n```'
        matches = re.findall(yaml_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            yaml_blocks.append(match.strip())
        
        # If no explicit YAML blocks, try to find YAML-like structures
        if not yaml_blocks:
            # Look for structures that start with 'thoughts:', 'name:', etc.
            yaml_like_pattern = r'(thoughts:\s*>.*?(?=\n\S|\Z))'
            matches = re.findall(yaml_like_pattern, response, re.DOTALL)
            yaml_blocks.extend(matches)
        
        return yaml_blocks
    
    def _execute_tool_from_yaml(self, parsed_yaml: Dict[str, Any]) -> bool:
        """Execute tool based on parsed YAML structure"""
        if 'name' not in parsed_yaml:
            if self.verbose:
                print(f"{Fore.YELLOW}No 'name' field found in YAML{Style.RESET_ALL}")
            return False
        
        tool_name = parsed_yaml['name']
        params = parsed_yaml.get('params', {})
        thoughts = parsed_yaml.get('thoughts', '')
        
        if self.verbose and thoughts:
            print(f"{Fore.CYAN}Agent Thoughts:{Style.RESET_ALL} {thoughts}")
        
        # Handle built-in tools
        if tool_name == 'ask_user':
            return self._handle_ask_user(params)
        elif tool_name == 'pass_result':
            return self._handle_pass_result(params)
        else:
            return self._execute_custom_tool(tool_name, params)
    
    def _handle_ask_user(self, params: Dict[str, Any]) -> bool:
        """Handle ask_user tool execution"""
        if not self.ask_user:
            if self.verbose:
                print(f"{Fore.YELLOW}ask_user is disabled{Style.RESET_ALL}")
            return False
            
        question = params.get('question', 'Please provide more information.')
        
        if self.verbose:
            print(f"{Fore.BLUE}Agent Question:{Style.RESET_ALL} {question}")
        
        try:
            user_response = input(f"{Fore.GREEN}Your response: {Style.RESET_ALL}")
            self.unleash(user_response)
            return True
        except KeyboardInterrupt:
            if self.verbose:
                print(f"{Fore.YELLOW}User input cancelled{Style.RESET_ALL}")
            return False
    
    def _handle_pass_result(self, params: Dict[str, Any]) -> bool:
        """Handle pass_result tool execution"""
        result = params.get('result', 'Task completed.')
        
        if self.verbose:
            print(f"{Fore.GREEN}Final Result:{Style.RESET_ALL} {result}")
        
        # Save to output file if specified
        if self.output_file:
            self._save_results(result)
        
        return True
    
    def _execute_custom_tool(self, tool_name: str, params: Dict[str, Any]) -> bool:
        """Execute a custom tool with proper error handling"""
        if tool_name not in self.tool_instances:
            if self.verbose:
                print(f"{Fore.RED}Tool '{tool_name}' not found{Style.RESET_ALL}")
            return False
        
        tool = self.tool_instances[tool_name]
        
        try:
            # Use enhanced tool execution if available
            if hasattr(tool, 'execute'):
                result = tool.execute(**params)
                
                if result.success:
                    if self.verbose:
                        print(f"{Fore.GREEN}Tool '{tool_name}' executed successfully{Style.RESET_ALL}")
                        print(f"Result: {result.result}")
                    
                    # Continue with tool response
                    self.unleash(f"Tool response: {result.result}")
                    return True
                else:
                    if self.verbose:
                        print(f"{Fore.RED}Tool '{tool_name}' execution failed: {result.error}{Style.RESET_ALL}")
                    return False
            else:
                # Legacy tool execution
                tool_response = self._execute_legacy_tool(tool, params)
                
                if self.verbose:
                    print(f"{Fore.GREEN}Tool '{tool_name}' response:{Style.RESET_ALL} {tool_response}")
                
                self.unleash(f"Tool response: {tool_response}")
                return True
                
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}Error executing tool '{tool_name}': {e}{Style.RESET_ALL}")
            return False
    
    def _execute_legacy_tool(self, tool: BaseTool, params: Dict[str, Any]) -> Any:
        """Execute legacy tool implementation"""
        # Ensure params is properly formatted
        validated_params = self._ensure_dict_params(params)
        
        # Try different execution methods for compatibility
        try:
            if inspect.signature(tool._run).parameters:
                return tool._run(**validated_params)
            else:
                return tool._run(validated_params)
        except TypeError:
            # Try unbound method approach for older tool implementations
            unbound_run_method = tool.__class__._run
            if inspect.signature(unbound_run_method).parameters:
                return run_sync_in_executor(unbound_run_method, **validated_params)
            else:
                return run_sync_in_executor(unbound_run_method, validated_params)
