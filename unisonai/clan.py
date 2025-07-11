from typing import Any, List, Optional
from pathlib import Path
import time
import re
import os
import colorama

from unisonai.prompts.plan import PLAN_PROMPT
from unisonai.agent import Agent
from unisonai.types import ClanConfig, TaskResult

colorama.init(autoreset=True)


def create_members(members: List[Agent]) -> str:
    """Create formatted member descriptions for prompt inclusion"""
    formatted_members = ""
    for idx, member in enumerate(members, 1):
        formatted_members += f"-{idx}: \n"
        formatted_members += f"  ROLE: {member.identity}\n"
        formatted_members += f"  DESCRIPTION: {member.description}\n"
        formatted_members += f"  GOAL: {member.task}\n"
    return formatted_members


class Clan:
    """Enhanced Clan class with strong typing and better configuration management"""
    
    def __init__(self, 
                 clan_name: str, 
                 manager: Agent, 
                 members: List[Agent], 
                 shared_instruction: str, 
                 goal: str, 
                 history_folder: str = "history", 
                 output_file: Optional[str] = None):
        """
        Initialize a Clan with comprehensive configuration validation
        
        Args:
            clan_name: Name of the clan
            manager: Manager/CEO agent for coordination
            members: List of clan member agents (including manager)
            shared_instruction: Instructions shared by all agents
            goal: Unified clan objective
            history_folder: Directory for storing clan history
            output_file: Optional file for final output
        """
        # Validate configuration using Pydantic model
        self.config = ClanConfig(
            clan_name=clan_name,
            shared_instruction=shared_instruction,
            goal=goal,
            history_folder=history_folder,
            output_file=output_file
        )
        
        # Core attributes
        self.clan_name = self.config.clan_name
        self.goal = self.config.goal
        self.shared_instruction = self.config.shared_instruction
        self.history_folder = Path(self.config.history_folder)
        self.output_file = self.config.output_file
        self.max_rounds = self.config.max_rounds
        
        # Agent management
        self.manager = manager
        self.members = members
        self.formatted_members = ""
        
        # State tracking
        self.current_round = 0
        self.execution_history: List[dict] = []
        self.plan: Optional[str] = None
        
        # Initialize clan structure
        self._initialize_clan()
    
    def _initialize_clan(self) -> None:
        """Initialize clan structure and configure agents"""
        # Create history directory
        self.history_folder.mkdir(parents=True, exist_ok=True)
        
        # Initialize output file if specified
        if self.output_file:
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.touch(exist_ok=True)
        
        # Configure manager for user interaction
        self.manager.ask_user = True
        
        # Format member information for prompts
        self.formatted_members = self._create_formatted_members()
        
        # Configure all agents with clan information
        for member in self.members:
            self._configure_agent(member)
    
    def _create_formatted_members(self) -> str:
        """Create formatted member descriptions including manager designation"""
        formatted_members = ""
        
        for member in self.members:
            if member == self.manager:
                formatted_members += f"-MEMBER {member.identity} Post: (Manager/CEO): \n"
            else:
                formatted_members += f"-MEMBER {member.identity}: \n"
                
            formatted_members += f"  NAME: {member.identity}\n"
            formatted_members += f"  DESCRIPTION: {member.description}\n"
            formatted_members += f"  GOAL: {member.task}\n"
        
        return formatted_members
    
    def _configure_agent(self, agent: Agent) -> None:
        """Configure an individual agent with clan information"""
        agent.history_folder = self.history_folder
        agent.shared_instruction = self.shared_instruction
        agent.user_task = self.goal
        agent.output_file = self.output_file
        agent.clan_name = self.clan_name
        agent.members = self.formatted_members
        agent.rawmembers = self.members

    def unleash(self) -> TaskResult:
        """
        Execute the clan's mission with enhanced planning and coordination
        
        Returns:
            TaskResult: Comprehensive execution results
        """
        start_time = time.time()
        
        try:
            # Generate strategic plan
            if self.config.verbose:
                print(f"{colorama.Fore.LIGHTCYAN_EX}Status: Generating strategic plan...{colorama.Style.RESET_ALL}")
            
            self.plan = self._generate_plan()
            
            if self.config.verbose:
                print(f"{colorama.Fore.LIGHTYELLOW_EX}Strategic Plan:{colorama.Style.RESET_ALL}\n{self.plan}")
            
            # Distribute plan to all agents
            self._distribute_plan()
            
            # Execute the mission
            if self.config.verbose:
                print(f"{colorama.Fore.LIGHTCYAN_EX}Status: Executing mission...{colorama.Style.RESET_ALL}")
            
            result = self.manager.unleash(self.goal)
            
            execution_time = time.time() - start_time
            
            return TaskResult(
                success=True,
                result=f"Clan '{self.clan_name}' successfully completed goal: {self.goal}",
                agent_identity=f"Clan-{self.clan_name}",
                execution_time=execution_time,
                iterations_used=self.current_round
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Clan execution failed: {str(e)}"
            
            return TaskResult(
                success=False,
                result="Clan mission failed due to error",
                agent_identity=f"Clan-{self.clan_name}",
                execution_time=execution_time,
                iterations_used=self.current_round,
                error=error_msg
            )
    
    def _generate_plan(self) -> str:
        """Generate strategic plan using the manager agent"""
        self.manager.llm.reset()
        
        # Generate plan using planning prompt
        plan_response = self.manager.llm.run(
            PLAN_PROMPT.format(
                members=self.formatted_members,
                client_task=self.goal
            ) + f"\n\nCreate a detailed plan to accomplish this task: {self.goal}"
        )
        
        # Clean up plan response - remove <think> tags
        cleaned_plan = re.sub(r"<think>(.*?)</think>", "", plan_response, flags=re.DOTALL)
        
        return cleaned_plan.strip()
    
    def _distribute_plan(self) -> None:
        """Distribute the strategic plan to all clan members"""
        self.manager.llm.reset()
        
        for member in self.members:
            member.plan = self.plan
