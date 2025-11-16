from typing import Any
from .prompts.plan import PLAN_PROMPT
from .agent import Agent
import re
import os
import colorama
colorama.init(autoreset=True)


def create_members(members: list[Any]):
    formatted_members = """"""
    for member in members:
        formatted_members += f"-{members.index(member)+1}: \n"
        formatted_members += "  ROLE: " + member.identity + "\n"
        formatted_members += "  DESCRIPTION: " + member.description + "\n"
        formatted_members += "  GOAL: " + member.task + "\n"
    return formatted_members


class Clan:
    def __init__(self, clan_name: str, manager: Agent, members: list[Agent], shared_instruction: str, goal: str, history_folder: str = "history", output_file: str = None):
        self.clan_name = clan_name
        self.goal = goal
        self.shared_instruction = shared_instruction
        self.manager = manager
        self.members = members
        self.output_file = output_file
        self.history_folder = history_folder
        self.manager.ask_user = True
        os.makedirs(self.history_folder, exist_ok=True)
        if self.output_file is not None:
            open(self.output_file, "w", encoding="utf-8").close()
        # Compact member formatting: "Name (Role): Desc"
        formatted_members = ""
        for member in self.members:
            member.clan_connected = True
            member.history_folder = self.history_folder
            member.shared_instruction = self.shared_instruction
            member.user_task = self.goal
            member.output_file = self.output_file
            member.clan_name = self.clan_name
            
            # Compact format: saves ~60% tokens vs verbose format
            if member == self.manager:
                formatted_members += f"{member.identity} (Manager): {member.description}\n"
            else:
                formatted_members += f"{member.identity}: {member.description}\n"

            member.members = formatted_members
            member.rawmembers = self.members
            self.formatted_members = formatted_members

    def unleash(self):
        self.manager.llm.reset()
        
        # Display planning initiation
        print(f"\n{colorama.Fore.CYAN}{colorama.Style.BRIGHT}{'═' * 70}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.LIGHTCYAN_EX}{colorama.Style.BRIGHT}CLAN PLANNING PHASE{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.CYAN}{'═' * 70}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.LIGHTWHITE_EX}Clan: {colorama.Style.BRIGHT}{self.clan_name}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.LIGHTWHITE_EX}Goal: {self.goal}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.CYAN}{'─' * 70}{colorama.Style.RESET_ALL}\n")
        
        response = self.manager.llm.run(PLAN_PROMPT.format(
            members=self.formatted_members,
            client_task=self.goal
        ) + "\n\n" + "Create a plan to accomplish this task: \n" + self.goal)
        
        # Extract reasoning and plan sections
        reasoning_match = re.search(r"\*\*REASONING:\*\*\s*(.+?)(?=\*\*PLAN:\*\*|$)", response, re.DOTALL)
        plan_match = re.search(r"\*\*PLAN:\*\*\s*(.+?)$", response, re.DOTALL)
        
        # Display formatted output
        print(f"{colorama.Fore.CYAN}{'═' * 70}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.LIGHTMAGENTA_EX}{colorama.Style.BRIGHT}PLANNING REASONING{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.CYAN}{'═' * 70}{colorama.Style.RESET_ALL}")
        
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
            print(f"{colorama.Fore.LIGHTWHITE_EX}{reasoning}{colorama.Style.RESET_ALL}\n")
        
        print(f"{colorama.Fore.GREEN}{'═' * 70}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.LIGHTGREEN_EX}{colorama.Style.BRIGHT}EXECUTION PLAN{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.GREEN}{'═' * 70}{colorama.Style.RESET_ALL}")
        
        if plan_match:
            plan = plan_match.group(1).strip()
            # Format each step with better styling
            steps = re.findall(r"(Step \d+:.+?)(?=Step \d+:|$)", plan, re.DOTALL)
            for i, step in enumerate(steps, 1):
                step_clean = step.strip()
                # Extract step number and content
                step_parts = step_clean.split(":", 1)
                if len(step_parts) == 2:
                    step_num = step_parts[0].strip()
                    step_content = step_parts[1].strip()
                    print(f"{colorama.Fore.LIGHTCYAN_EX}{colorama.Style.BRIGHT}{step_num}:{colorama.Style.RESET_ALL}")
                    print(f"{colorama.Fore.WHITE}   {step_content}{colorama.Style.RESET_ALL}\n")
                else:
                    print(f"{colorama.Fore.WHITE}{step_clean}{colorama.Style.RESET_ALL}\n")
        else:
            print(f"{colorama.Fore.LIGHTWHITE_EX}{response}{colorama.Style.RESET_ALL}\n")
        
        print(f"{colorama.Fore.GREEN}{'═' * 70}{colorama.Style.RESET_ALL}\n")
        
        # Remove any XML-style tags for clean plan text
        response = re.sub(r"<think>(.*?)</think>", "", response, flags=re.DOTALL)
        response = re.sub(r"<[^>]+>", "", response)
        
        self.manager.llm.reset()
        for member in self.members:
            member.plan = response
        
        # Display execution start
        print(f"{colorama.Fore.CYAN}{'═' * 70}{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.LIGHTGREEN_EX}{colorama.Style.BRIGHT}STARTING EXECUTION{colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.CYAN}{'═' * 70}{colorama.Style.RESET_ALL}\n")

        self.manager.unleash(self.goal)
