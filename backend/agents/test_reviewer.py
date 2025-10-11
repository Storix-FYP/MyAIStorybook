# test_reviewer_agent.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from reviewer_agent import ReviewerAgent

def test_reviewer_agent():
    reviewer = ReviewerAgent()
    sample_story = {
    "title": "Cricket Friends",
    "setting": "Village field",
    "characters": ["John", "Jack"],
    "scenes": [
        {
            "scene_number": 1,
            "text": "John and Jack play cricket and learn teamwork."
        }
    ]

    }
    
    feedback = reviewer.review_story(sample_story)
    print("\n🔍 Review Feedback:\n", feedback)

if __name__ == "__main__":
    test_reviewer_agent()
