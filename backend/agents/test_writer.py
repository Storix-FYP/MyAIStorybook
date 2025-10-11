import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.agents.writer_agent import WriterAgent

def test_writer_agent():
    writer = WriterAgent()
    prompt = "A brave cat saves its village from a giant storm."
    story = writer.generate_story(prompt)
    print("\n📝 Generated Story:\n", story)

if __name__ == "__main__":
    test_writer_agent()
