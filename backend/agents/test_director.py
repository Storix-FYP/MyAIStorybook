# backend/agents/test_director.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from director_agent import DirectorAgent
import json

def test_director_agent():
    director = DirectorAgent()

    # Example prompt
    prompt = "Lily and Leo discovered a mysterious door in the forest. Beyond it was a world filled with glowing trees and friendly creatures."

    # Call the full story creation pipeline
    result = director.create_story(prompt)

    print("\n🎬 Director Output:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_director_agent()
