import sys  # Added for exiting the process smoothly
from .llms import Gemini
from .prompts.agent import AGENT_PROMPT
from .prompts.manager import MANAGER_PROMPT
from .prompts.individual import INDIVIDUAL_PROMPT
from .async_helper import run_async_from_sync, run_sync_in_executor
import inspect
import re
import colorama
from colorama import Fore, Style
from typing import Any
import json
import difflib  # For fuzzy string matching
import os  # For directory operations
import hashlib  # For cache keys
from datetime import datetime, timedelta
colorama.init(autoreset=True)


def create_tools(tools: list):
    formatted_tools = ""
    if tools:
        for tool in tools:
            # Instantiate the tool if it is provided as a class
            tool_instance = tool if not isinstance(tool, type) else tool()
            formatted_tools += f"-TOOL{tools.index(tool)+1}: \n"
            formatted_tools += "  NAME: " + tool_instance.name + "\n"
            formatted_tools += "  DESCRIPTION: " + tool_instance.description + "\n"
            formatted_tools += "  PARAMS: "
            fields = tool_instance.params
            for field in fields:
                formatted_tools += field.format()
    else:
        formatted_tools = None

    return formatted_tools


class Agent:
    def __init__(self,
                 llm: Gemini,
                 identity: str,  # Name of the agent
                 description: str,  # Description of the agent
                 task: str = "",  # A Base Example Task According to agent's work (optional for single agents)
                 verbose: bool = True,
                 tools: list[Any] = [],
                 output_file: str = None,  # For single agent mode
                 history_folder: str = None,  # For both modes, defaults to "." for clan, "history" for single
                 enable_cache: bool = True,  # Enable result caching
                 cache_ttl_minutes: int = 30):  # Cache time-to-live
        self.llm = llm
        self.identity = identity
        self.description = description
        self.task = task
        self.plan = None
        self.output_file = output_file
        self.clan_connected = False  # Default: standalone mode
        
        # Set history folder based on mode
        if history_folder is None:
            self.history_folder = "."  # Will be overridden by clan or used as "history" in single mode
        else:
            self.history_folder = history_folder
            
        self.rawtools = tools
        self.tools = create_tools(tools)
        self.ask_user = False  # Will be set to True by clan for manager
        self.user_task = None
        self.shared_instruction = None
        self.rawmembers = []
        self.members = ""
        self.clan_name = ""
        self.verbose = verbose
        
        # Result caching
        self.enable_cache = enable_cache
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self._tool_cache = {}  # Format: {cache_key: (result, timestamp)}
        
        # Create history folder for single agent mode
        if not self.clan_connected and self.history_folder != ".":
            os.makedirs(self.history_folder, exist_ok=True)
    
    def _get_cache_key(self, tool_name: str, params: dict) -> str:
        """Generate unique cache key for tool+params combination."""
        # Sort params for consistent hashing
        param_str = json.dumps(params, sort_keys=True)
        key_str = f"{tool_name}:{param_str}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached_result(self, tool_name: str, params: dict) -> tuple[bool, Any]:
        """Check cache for existing result.
        
        Returns:
            (cache_hit: bool, result: Any)
        """
        if not self.enable_cache:
            return False, None
        
        cache_key = self._get_cache_key(tool_name, params)
        if cache_key in self._tool_cache:
            result, timestamp = self._tool_cache[cache_key]
            
            # Check if cache is still valid
            if datetime.now() - timestamp < self.cache_ttl:
                return True, result
            else:
                # Expired, remove from cache
                del self._tool_cache[cache_key]
        
        return False, None
    
    def _cache_result(self, tool_name: str, params: dict, result: Any) -> None:
        """Store tool result in cache."""
        if not self.enable_cache:
            return
        
        cache_key = self._get_cache_key(tool_name, params)
        self._tool_cache[cache_key] = (result, datetime.now())

    def _parse_and_fix_json(self, json_str: str):
        """Parses JSON string and attempts to fix common errors."""
        json_str = json_str.strip()
        if not json_str.startswith("{") or not json_str.endswith("}"):
            json_str = json_str[json_str.find("{"): json_str.rfind("}") + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}JSON parsing error: {e}{Style.RESET_ALL}")
            json_str = json_str.replace("'", '"')
            json_str = re.sub(r",\s*}", "}", json_str)
            json_str = re.sub(r"{\s*,", "{", json_str)
            json_str = re.sub(r"\s*,\s*", ",", json_str)
            try:
                return [json_str]
            except json.JSONDecodeError as e:
                return f"Error: Could not parse JSON - {e}"

    def _get_agent_by_name(self, agent_name: str):
        """Find the closest matching agent from rawmembers based on fuzzy name matching."""
        ceo_manager_variations = ["ceo", "manager",
                                  "ceo/manager", "ceo-manager", "ceo manager"]
        agent_name_clean = agent_name.lower().strip()
        for prefix in ["agent ", " agent", "the "]:
            agent_name_clean = agent_name_clean.replace(prefix, "")
        if agent_name_clean in ceo_manager_variations:
            return "CEO/Manager"
        available_agents = [member.identity for member in self.rawmembers]
        available_agents_lower = [agent.lower() for agent in available_agents]
        if agent_name_clean in available_agents_lower:
            index = available_agents_lower.index(agent_name_clean)
            return available_agents[index]
        matches = difflib.get_close_matches(
            agent_name_clean, available_agents_lower, n=1, cutoff=0.6)
        if matches:
            index = available_agents_lower.index(matches[0])
            return available_agents[index]
        return agent_name

    def send_message(self, agent_name: str, message: str, additional_resource: str = None, sender: str = None):
        matched_agent_name = self._get_agent_by_name(agent_name)
        if matched_agent_name != agent_name and self.verbose:
            print(f"{Fore.LIGHTYELLOW_EX}Note: '{agent_name}' matched to '{matched_agent_name}'{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}Sending message -> {Style.BRIGHT}{Fore.WHITE}{matched_agent_name}{Style.RESET_ALL}")
        
        # Optimized message format: compact without redundant headers (saves ~50 tokens per message)
        msg = f"FROM: {sender} | {message}"
        if additional_resource:
            msg += f"\\nRESOURCE: {additional_resource}"
        
        is_manager_message = matched_agent_name in [
            "CEO/Manager", "Manager", "CEO"]
        for member in self.rawmembers:
            if is_manager_message:
                if member.ask_user:
                    member.unleash(msg)
                else:
                    continue
            elif member.identity == matched_agent_name:
                member.unleash(msg)

    def _ensure_dict_params(self, params_data):
        """Ensures params is a dictionary by parsing it if it's a string."""
        if isinstance(params_data, str):
            params_data = params_data.strip()
            try:
                return json.loads(params_data)
            except json.JSONDecodeError as e:
                print(f"{Fore.YELLOW}JSON parsing error: {e}")
                return {"raw_input": params_data}
        elif params_data is None:
            return {}
        return params_data

    def unleash(self, task: str):
        self.user_task = task
        
        # Determine folder based on mode
        if self.clan_connected:
            # Clan mode: use history_folder or default to "."
            folder = self.history_folder if self.history_folder is not None else "."
        else:
            # Single agent mode: use history_folder or default to "history"
            if self.history_folder == ".":
                self.history_folder = "history"
                os.makedirs(self.history_folder, exist_ok=True)
            folder = self.history_folder
            
        try:
            with open(f"{folder}/{self.identity}.json", "r", encoding="utf-8") as f:
                history = f.read()
                self.messages = json.loads(history) if history else []
        except FileNotFoundError:
            open(f"{folder}/{self.identity}.json",
                 "w", encoding="utf-8").close()
            self.messages = []
            
        self.llm.reset()
        
        # Choose prompt based on mode
        if self.clan_connected:
            # Clan mode: use AGENT_PROMPT or MANAGER_PROMPT
            if self.tools:
                if self.ask_user:
                    self.llm.__init__(
                        messages=self.messages,
                        system_prompt=MANAGER_PROMPT.format(
                            members=self.members,
                            shared_instruction=self.shared_instruction,
                            identity=self.identity,
                            description=self.description,
                            task=self.task,
                            user_task=task,
                            tools=self.tools,
                            plan=self.plan,
                            clan_name=self.clan_name
                        )
                    )
                else:
                    self.llm.__init__(
                        messages=self.messages,
                        system_prompt=AGENT_PROMPT.format(
                            identity=self.identity,
                            description=self.description,
                            task=self.task,
                            tools=self.tools,
                            user_task=task,
                            shared_instruction=self.shared_instruction,
                            members=self.members,
                            plan=self.plan,
                            clan_name=self.clan_name
                        )
                    )
            else:
                if self.ask_user:
                    self.llm.__init__(
                        messages=self.messages,
                        system_prompt=MANAGER_PROMPT.format(
                            members=self.members,
                            shared_instruction=self.shared_instruction,
                            identity=self.identity,
                            description=self.description,
                            task=self.task,
                            user_task=task,
                            plan=self.plan,
                            tools="No Provided Tools",
                            clan_name=self.clan_name
                        )
                    )
                else:
                    self.llm.__init__(
                        messages=self.messages,
                        system_prompt=AGENT_PROMPT.format(
                            identity=self.identity,
                            description=self.description,
                            task=self.task,
                            tools="No Provided Tools",
                            plan=self.plan,
                            user_task=task,
                            shared_instruction=self.shared_instruction,
                            members=self.members,
                            clan_name=self.clan_name
                        )
                    )
        else:
            # Single agent mode: use INDIVIDUAL_PROMPT
            if self.tools:
                self.llm.__init__(
                    messages=self.messages,
                    model=self.llm.model,  # Preserve the model
                    temperature=self.llm.temperature,  # Preserve temperature
                    system_prompt=INDIVIDUAL_PROMPT.format(
                        identity=self.identity,
                        description=self.description,
                        user_task=self.user_task,
                        tools=self.tools,
                    ),
                    max_tokens=self.llm.max_tokens,  # Preserve max_tokens
                    verbose=self.llm.verbose,  # Preserve verbose
                    api_key=self.llm.client.api_key if hasattr(self.llm, 'client') and hasattr(self.llm.client, 'api_key') else None
                )
            else:
                self.llm.__init__(
                    messages=self.messages,
                    model=self.llm.model,  # Preserve the model
                    temperature=self.llm.temperature,  # Preserve temperature
                    system_prompt=INDIVIDUAL_PROMPT.format(
                        identity=self.identity,
                        description=self.description,
                        user_task=self.user_task,
                        tools="No Provided Tools",
                    ),
                    max_tokens=self.llm.max_tokens,  # Preserve max_tokens
                    verbose=self.llm.verbose,  # Preserve verbose
                    api_key=self.llm.client.api_key if hasattr(self.llm, 'client') and hasattr(self.llm.client, 'api_key') else None
                )
                
        print(f"\n{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}Evaluating Task...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}\n")
        
        response = self.llm.run(task, save_messages=True)
        try:
            with open(f"{folder}/{self.identity}.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(self.llm.messages, indent=4))
        except Exception as e:
            print(f"{Fore.RED}Error saving history: {e}{Style.RESET_ALL}")
        
        if self.verbose:
            print(f"{Fore.LIGHTBLACK_EX}{'─' * 70}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}Model Response:{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}{response}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}{'─' * 70}{Style.RESET_ALL}\n")
        
        # Extract JSON blocks from response
        json_blocks = re.findall(r"```json(.*?)```", response, flags=re.DOTALL)
        if not json_blocks:
            return response
        
        json_content = json_blocks[0].strip()
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"\n{Fore.RED}{'═' * 70}{Style.RESET_ALL}")
            print(f"{Fore.RED}JSON Parsing Error{Style.RESET_ALL}")
            print(f"{Fore.RED}{'═' * 70}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}Details: {e}{Style.RESET_ALL}\n")
            return response

        # Handle new JSON structure: {"reasoning": "...", "action": {"tool": "...", "params": {...}}}
        if "reasoning" in data and "action" in data:
            reasoning = data["reasoning"]
            action = data["action"]
            
            # Extract tool name and parameters from action
            name = action.get("tool", "")
            params = action.get("params", {})
            
            # Display in a clean, professional format
            print(f"\n{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTCYAN_EX}Agent: {Style.BRIGHT}{Fore.WHITE}{self.identity}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}")
            
            # Display reasoning
            print(f"\n{Fore.LIGHTYELLOW_EX}Reasoning:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}   {reasoning}{Style.RESET_ALL}")
            
            # Display action
            print(f"\n{Fore.LIGHTGREEN_EX}Action:{Style.RESET_ALL}")
            print(f"{Fore.LIGHTCYAN_EX}   └─ Tool:{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{name}{Style.RESET_ALL}")
            if params:
                print(f"{Fore.LIGHTMAGENTA_EX}   └─ Parameters:{Style.RESET_ALL}")
                for key, value in params.items():
                    # Truncate long values
                    str_value = str(value)
                    if len(str_value) > 100:
                        str_value = str_value[:97] + "..."
                    print(f"{Fore.LIGHTBLACK_EX}      • {Fore.LIGHTWHITE_EX}{key}:{Style.RESET_ALL} {Fore.WHITE}{str_value}{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}\n")
            
            if name == "send_message":
                if isinstance(params, dict) and "agent_name" in params and "message" in params:
                    self.send_message(params["agent_name"], params["message"], params.get(
                        "additional_resource"), sender=self.identity)
                else:
                    print(f"\n{Fore.RED}{'─' * 70}{Style.RESET_ALL}")
                    print(f"{Fore.RED}Error: Missing required parameters{Style.RESET_ALL}")
                    print(f"{Fore.LIGHTYELLOW_EX}   send_message requires: 'agent_name' and 'message'{Style.RESET_ALL}")
                    print(f"{Fore.RED}{'─' * 70}{Style.RESET_ALL}\n")
            elif name == "ask_user":
                if isinstance(params, dict) and "question" in params:
                    print(f"\n{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}")
                    print(f"{Fore.LIGHTYELLOW_EX}Question:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}   {params['question']}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}")
                    self.unleash(input(f"{Fore.LIGHTCYAN_EX}You:{Style.RESET_ALL} "))
                else:
                    question = str(params) if params else "What would you like to say?"
                    print(f"\n{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}")
                    print(f"{Fore.LIGHTYELLOW_EX}Question:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}   {question}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{'─' * 70}{Style.RESET_ALL}")
                    self.unleash(input(f"{Fore.LIGHTCYAN_EX}You:{Style.RESET_ALL} "))
            elif name == "pass_result":
                result_text = params.get("result", str(params)) if isinstance(params, dict) else str(params)
                print(f"\n{Fore.GREEN}{'═' * 70}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTGREEN_EX}{Style.BRIGHT}FINAL RESULT{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{'═' * 70}{Style.RESET_ALL}")
                print(f"\n{Fore.LIGHTWHITE_EX}{result_text}{Style.RESET_ALL}\n")
                print(f"{Fore.GREEN}{'═' * 70}{Style.RESET_ALL}\n")
                
                decision = input(f"{Fore.LIGHTCYAN_EX}Accept this result? (y/n):{Style.RESET_ALL} ")
                if decision.lower() == "y":
                    print(f"\n{Fore.GREEN}{'═' * 70}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}{Style.BRIGHT}Result Accepted Successfully{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}{'═' * 70}{Style.RESET_ALL}\n")
                    if self.output_file:
                        with open(self.output_file, "w", encoding="utf-8") as file:
                            file.write(result_text)
                    sys.exit(0)
                elif decision.lower() == "n":
                    tweaks = input(f"{Fore.LIGHTWHITE_EX}What changes would you like?{Style.RESET_ALL} ")
                    self.unleash(tweaks)
            else:
                # Execute the tool by first ensuring we have an instance.
                for tool in self.rawtools:
                    tool_instance = tool if not isinstance(tool, type) else tool()
                    if tool_instance.name.lower() == name.lower():
                        # Check cache first
                        cache_hit, cached_result = self._get_cached_result(name, params)
                        if cache_hit:
                            print(f"\n{Fore.LIGHTMAGENTA_EX}{'─' * 70}{Style.RESET_ALL}")
                            print(f"{Fore.LIGHTCYAN_EX}Cache Hit: {Style.BRIGHT}{Fore.WHITE}{name}{Style.RESET_ALL} (saved API call)")
                            print(f"{Fore.LIGHTMAGENTA_EX}{'─' * 70}{Style.RESET_ALL}\n")
                            print(f"{Fore.LIGHTMAGENTA_EX}{'─' * 70}{Style.RESET_ALL}")
                            print(f"{Fore.LIGHTGREEN_EX}Tool Response:{Style.RESET_ALL}")
                            print(f"{Fore.LIGHTMAGENTA_EX}{'─' * 70}{Style.RESET_ALL}")
                            print(f"{Fore.WHITE}{cached_result}{Style.RESET_ALL}")
                            print(f"{Fore.LIGHTMAGENTA_EX}{'─' * 70}{Style.RESET_ALL}\n")
                            self.unleash("Tool response:\n\n" + str(cached_result))
                            break
                        
                        try:
                            # --- Primary execution path (bound method) ---
                            bound_run_method = tool_instance._run
                            is_async = inspect.iscoroutinefunction(bound_run_method)
                            
                            print(f"\n{Fore.LIGHTMAGENTA_EX}{'─' * 70}{Style.RESET_ALL}")
                            print(f"{Fore.LIGHTMAGENTA_EX}Executing Tool: {Style.BRIGHT}{Fore.WHITE}{name}{Style.RESET_ALL} ...{Style.RESET_ALL}")
                            print(f"{Fore.LIGHTMAGENTA_EX}{'─' * 70}{Style.RESET_ALL}\n")
                            
                            if is_async:
                                if isinstance(params, dict):
                                    tool_response = run_async_from_sync(bound_run_method(**params))
                                else:
                                    tool_response = run_async_from_sync(bound_run_method(params))
                            else: # Is a synchronous tool
                                if isinstance(params, dict):
                                    tool_response = bound_run_method(**params)
                                else:
                                    tool_response = bound_run_method(params)

                            # Cache the result
                            self._cache_result(name, params, tool_response)
                            
                            print(f"{Fore.LIGHTMAGENTA_EX}{'─' * 70}{Style.RESET_ALL}")
                            print(f"{Fore.LIGHTGREEN_EX}Tool Response:{Style.RESET_ALL}")
                            print(f"{Fore.LIGHTMAGENTA_EX}{'─' * 70}{Style.RESET_ALL}")
                            print(f"{Fore.WHITE}{tool_response}{Style.RESET_ALL}")
                            print(f"{Fore.LIGHTMAGENTA_EX}{'─' * 70}{Style.RESET_ALL}\n")
                            self.unleash("Tool response:\n\n" + str(tool_response))
                            break
                        
                        except TypeError as e:
                            if ("missing 1 required positional argument: 'self'" in str(e) or
                                    "got multiple values for argument" in str(e) or
                                    "takes 0 positional arguments but 1 was given" in str(e)):
                            
                                try:
                                    # --- Fallback execution path (unbound method) ---
                                    unbound_run_method = tool_instance.__class__._run
                                    is_async_unbound = inspect.iscoroutinefunction(unbound_run_method)

                                    print(f"\n{Fore.LIGHTYELLOW_EX}{'─' * 70}{Style.RESET_ALL}")
                                    print(f"{Fore.LIGHTYELLOW_EX}Executing Tool (fallback): {Style.BRIGHT}{Fore.WHITE}{name}{Style.RESET_ALL} ...{Style.RESET_ALL}")
                                    print(f"{Fore.LIGHTYELLOW_EX}{'─' * 70}{Style.RESET_ALL}\n")

                                    if is_async_unbound:
                                        if isinstance(params, dict):
                                            tool_response = run_async_from_sync(unbound_run_method(**params))
                                        else:
                                            tool_response = run_async_from_sync(unbound_run_method(params))
                                    else: 
                                        if isinstance(params, dict):
                                            tool_response = run_sync_in_executor(unbound_run_method, **params)
                                        else:
                                            tool_response = run_sync_in_executor(unbound_run_method, params)
                                    
                                    print(f"{Fore.LIGHTYELLOW_EX}{'─' * 70}{Style.RESET_ALL}")
                                    print(f"{Fore.LIGHTGREEN_EX}Tool Response:{Style.RESET_ALL}")
                                    print(f"{Fore.LIGHTYELLOW_EX}{'─' * 70}{Style.RESET_ALL}")
                                    print(f"{Fore.WHITE}{tool_response}{Style.RESET_ALL}")
                                    print(f"{Fore.LIGHTYELLOW_EX}{'─' * 70}{Style.RESET_ALL}\n")
                                    self.unleash("Tool response:\n\n" + str(tool_response))
                                    break
                                except Exception as inner_e:
                                    print(f"\n{Fore.RED}{'─' * 70}{Style.RESET_ALL}")
                                    print(f"{Fore.RED}Error executing tool '{name}'{Style.RESET_ALL}")
                                    print(f"{Fore.LIGHTYELLOW_EX}   {inner_e}{Style.RESET_ALL}")
                                    print(f"{Fore.RED}{'─' * 70}{Style.RESET_ALL}\n")
                            else:
                                print(f"\n{Fore.RED}{'─' * 70}{Style.RESET_ALL}")
                                print(f"{Fore.RED}Error executing tool '{name}'{Style.RESET_ALL}")
                                print(f"{Fore.LIGHTYELLOW_EX}   {e}{Style.RESET_ALL}")
                                print(f"{Fore.RED}{'─' * 70}{Style.RESET_ALL}\n")

                        except Exception as e:
                            print(f"\n{Fore.RED}{'─' * 70}{Style.RESET_ALL}")
                            print(f"{Fore.RED}Error executing tool '{name}'{Style.RESET_ALL}")
                            print(f"{Fore.LIGHTYELLOW_EX}   {e}{Style.RESET_ALL}")
                            print(f"{Fore.RED}{'─' * 70}{Style.RESET_ALL}\n")
        else:
            print(f"\n{Fore.RED}{'═' * 70}{Style.RESET_ALL}")
            print(f"{Fore.RED}Invalid JSON Format{Style.RESET_ALL}")
            print(f"{Fore.RED}{'═' * 70}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}Expected: {{'reasoning': '...', 'action': {{'tool': '...', 'params': {{}}}}}}{Style.RESET_ALL}\n")
            return response
