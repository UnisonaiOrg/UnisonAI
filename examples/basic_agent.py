"""
Basic Single Agent Example

This example demonstrates how to create and use a simple UnisonAI agent
for basic tasks like answering questions and providing explanations.
"""

from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai import config

def main():
    # Configure API key
    config.set_api_key("gemini", "your-gemini-api-key")

    # Create a basic agent
    agent = Single_Agent(
        llm=Gemini(model="gemini-2.0-flash"),
        identity="Basic Assistant",
        description="A helpful AI assistant for general questions and explanations",
        verbose=True
    )

    # Example tasks
    tasks = [
        "Explain how photosynthesis works in simple terms",
        "What are the benefits of renewable energy?",
        "How do I bake chocolate chip cookies?",
        "Explain the concept of machine learning"
    ]

    print("🤖 Basic Agent Examples")
    print("=" * 50)

    for i, task in enumerate(tasks, 1):
        print(f"\n📋 Task {i}: {task}")
        print("-" * 30)

        try:
            result = agent.unleash(task=task)
            print(f"✅ Response: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")

        print()

if __name__ == "__main__":
    main()
