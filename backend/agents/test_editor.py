# test_editor_agent.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from editor_agent import EditorAgent

def test_editor_agent():
    editor = EditorAgent()

    # ✅ The editor expects a story dict, not a string
    story = {
        "title": "The Forest Adventure",
        "setting": "Magical forest",
        "characters": ["Boy", "Girl"],
        "scenes": [
            {"scene_number": 1, "text": "The boy and girl went to the forest and saw magical lights."}
        ],
        "meta": {"author": "AI"}
    }

    edited_story, msg = editor.edit_story(story)
    print("\n✏️ Edited Story:\n", edited_story)
    print("\n📋 Message:", msg)


if __name__ == "__main__":
    test_editor_agent()

