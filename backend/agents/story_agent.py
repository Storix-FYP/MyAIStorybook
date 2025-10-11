# backend/agents/story_agent.py
from typing import Dict, Any, Tuple
from backend.agents.director_agent import DirectorAgent


class StoryAgent:
    """
    StoryAgent facade kept for backward compatibility.
    It delegates to DirectorAgent (multi-agent pipeline).
    """

    def __init__(self, llm_model: str = "llama3.1:8b-instruct-q4_K_M", writer_max_scenes: int = 3, max_retries: int = 2):
        self.director = DirectorAgent(llm_model=llm_model, writer_max_scenes=writer_max_scenes)
        self.max_retries = max_retries

    def generate_story(self, prompt: str, generate_images: bool = False) -> Tuple[Dict[str, Any], str]:
        # Single attempt (Director handles inner retries). Could wrap in our own retries if desired.
        result = self.director.create_story(prompt, generate_images=generate_images)
        # Director returns {"status": {...}, "story": {...}}
        status = result.get("status", {})
        story = result.get("story", {})
        # format a friendly status string
        if isinstance(status, dict):
            status_str = " | ".join(f"{k}:{v}" for k, v in status.items())
        else:
            status_str = str(status)
        return story, status_str
