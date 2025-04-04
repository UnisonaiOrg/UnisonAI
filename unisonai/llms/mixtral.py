import os
from mistralai import Mistral
from dotenv import load_dotenv
from rich import print
from typing import Optional

load_dotenv()

class Mixtral:
    USER = "user"
    MODEL = "assistant"
    SYSTEM = "system"
    
    def __init__(
            self,
            messages: list[dict[str, str]] = [],
            model: str = "mistral-large-latest",
            temperature: Optional[float] = 0.7,
            system_prompt: Optional[str] = None,
            max_tokens: int = 2048,
            api_key: str | None = None
    ) -> None:
        self.api_key = api_key if api_key else os.getenv("MISTRAL_API_KEY")
        self.client = Mistral(api_key=self.api_key)
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens

        if self.system_prompt is not None:
            self.add_message(self.SYSTEM, self.system_prompt)

    def run(self, prompt: str, save_messages: bool = True) -> str:
        if save_messages:
            self.add_message(self.USER, prompt)
        
        response_content = ""
        response = self.client.chat.complete(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            stream=False,
            max_tokens=self.max_tokens,
        )
        
        response_content = response.choices[0].message.content
        # print(response_content)
        
        if save_messages:
            self.add_message(self.MODEL, response_content)
        
        return response_content

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def reset(self) -> None:
        self.messages = []
        self.system_prompt = None

if __name__ == "__main__":
    llm = Mixtral(model="mistral-large-latest")
    while True:
        q = input(">>> ")
        # llm.add_message(GroqLLM.USER, q)
        print("Final Response:")
        print(llm.run(q))
        print()
        # print(llm.messages)
        # llm.reset()  # Reset the instance
        # print(llm.messages)
