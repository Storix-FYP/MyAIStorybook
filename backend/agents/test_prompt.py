# test_prompt_agent.py
from prompt_agent import PromptAgent

def test_prompt_agent():
    agent = PromptAgent()

    prompts = [
        "john and jack were playing cricket",
        "boy and girl",
        "98217398",
        "notes",
        "A long story about a village where everyone speaks in colors instead of words, and a child who wants to learn both.",
        "https://google.com"
    ]

    for p in prompts:
        enhanced, ptype = agent.process_prompt(p)
        print(f"\n🧠 Prompt: {p}\n➡️ Type: {ptype}\n✨ Enhanced: {enhanced}")

if __name__ == "__main__":
    test_prompt_agent()
