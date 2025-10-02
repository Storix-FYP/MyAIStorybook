# backend/agents/review_agent.py
import json
import time
from typing import Tuple, Dict
from backend.models.story_schema import Story


class ReviewAgent:
    """
    Review Agent:
    - Validates generated story against schema
    - Ensures each scene has both text + image (image_path or image_description)
    - Provides retry mechanism for fixes
    """

    def __init__(self, max_retries=2, delay=1.0):
        self.max_retries = max_retries
        self.delay = delay

    def validate_story(self, story_dict: Dict) -> Tuple[bool, str]:
        """Check if story matches schema requirements and extra checks."""
        try:
            story = Story(**story_dict)
        except Exception as e:
            return False, f"Schema validation failed: {str(e)}"

        # Extra check: every scene must have text + (image_path or image_description)
        for i, scene in enumerate(story.scenes):
            if not scene.text or (not scene.image_description and not scene.image_path):
                return False, f"Scene {i+1} missing text or image description/path."

        return True, "Story validation successful."

    def _auto_fix(self, story_dict: Dict) -> Dict:
        """
        Very simple auto-fix:
        - If missing text: add placeholder
        - If missing image_description: add fallback description
        """
        for i, scene in enumerate(story_dict.get("scenes", [])):
            if not scene.get("text"):
                scene["text"] = f"Auto-fixed placeholder text for scene {i+1}."
            if not scene.get("image_description") and not scene.get("image_path"):
                scene["image_description"] = f"Auto-fixed placeholder image description for scene {i+1}."
        return story_dict

    def review_story(self, story_dict: Dict) -> Tuple[Dict, str]:
        """
        Review a generated story with retries if validation fails.
        Returns (story_dict, status_msg)
        """
        attempt = 0
        while attempt <= self.max_retries:
            is_valid, message = self.validate_story(story_dict)
            if is_valid:
                return story_dict, "Story approved by ReviewAgent ✅"

            # If invalid, attempt auto-fix
            print(f"[ReviewAgent] Validation failed: {message}")
            if attempt < self.max_retries:
                print(f"[ReviewAgent] Attempting auto-fix (retry {attempt+1}/{self.max_retries})...")
                story_dict = self._auto_fix(story_dict)
                time.sleep(self.delay)
            attempt += 1

        return story_dict, "Story failed review ❌ after retries."

# Debug/Test Run
if __name__ == "__main__":
    sample_story = {
        "title": "The Lonely Star",
        "setting": "Night Sky",
        "characters": ["Lonely Star"],
        "scenes": [
            {"scene_number": 1, "text": "Once upon a time, a star lived alone in the sky.", "image_description": "A single glowing star in a dark sky"},
            {"scene_number": 2, "text": "", "image_description": ""},  # Broken scene to test auto-fix
        ]
    }

    reviewer = ReviewAgent(max_retries=2)
    final_story, status = reviewer.review_story(sample_story)

    print("\n--- Final Review Output ---")
    print(json.dumps(final_story, indent=2, ensure_ascii=False))
    print("Status:", status)
