# backend/agents/story_agent.py
import json
from typing import Dict, Any, Tuple
from ollama import chat
from backend.models.story_schema import Story


class StoryAgent:
    """
    Story Agent: Generates a simple structured story (Iteration 1).
    Uses an LLM via Ollama (chat).
    """

    def __init__(self, model: str = "dolphin3:8b", max_retries: int = 3):
        self.model = model
        self.max_retries = max_retries

    def _clean_json_output(self, raw_text: str) -> str:
        """
        Remove surrounding markdown fences (``` or ```json) and leading/trailing whitespace.
        Ollama / models sometimes return fenced markdown - strip it.
        """
        if not raw_text:
            return raw_text
        text = raw_text.strip()
        # If the model wrapped output in triple backticks, remove them.
        if text.startswith("```") and "```" in text[3:]:
            # split and take middle content
            parts = text.split("```")
            # parts example: ['', 'json\n{...}', '']
            # find the first non-empty chunk that looks like JSON or contains '{'
            for p in parts:
                if "{" in p:
                    # remove a leading 'json' word if present
                    p_clean = p.lstrip()
                    if p_clean.lower().startswith("json"):
                        p_clean = p_clean[4:].lstrip()
                    return p_clean.strip()
            # fallback: join and strip backticks
            text = text.replace("```", "")
        # remove any leading "json\n" if present
        if text.lower().startswith("json\n"):
            text = text[len("json\n"):].lstrip()
        return text.strip()

    def generate_story(self, prompt: str) -> Tuple[Dict[str, Any], str]:
        """
        Generate a structured story validated against the Story schema.
        Retries if the model output is invalid.

        Returns:
            (story_dict, status_message)
        """
        system_prompt = (
            "You are a story generator agent. "
            "Generate a children's story as valid JSON that strictly follows this schema:\n\n"
            "Story(title: str, setting: str, characters: [str], "
            "scenes: List[Scene(scene_number: int, text: str, image_description: Optional[str])]).\n\n"
            "Rules:\n"
            "1. Output JSON only. No markdown, no explanations.\n"
            "2. Scenes must be numbered in order.\n"
            "3. Each scene must have at least 'text'.\n"
        )

        raw_text = ""
        for attempt in range(1, self.max_retries + 1):
            try:
                response = chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                )
                
                # Extract message text safely
                raw_text = getattr(response.message, "content", None) if hasattr(response, "message") else None
                if not raw_text and isinstance(response, dict):
                    raw_text = response.get("message", {}).get("content")
                if not raw_text:
                    raw_text = str(response)
                
                cleaned = self._clean_json_output(raw_text)
                story_dict = json.loads(cleaned)


                # Validate against schema
                story = Story(**story_dict)
                return story.model_dump(), "Story generated ✅"

            except Exception as e:
                print(f"[Retry {attempt}/{self.max_retries}] Invalid output: {e}")
                if attempt == self.max_retries:
                    # include last raw_text for debugging
                    raise ValueError(f"Failed after {self.max_retries} retries. Last raw output:\n{raw_text}")

        # unreachable, but for typing:
        return {}, "Failed to generate story"

# Example test (safe to import; only runs when executed directly)
if __name__ == "__main__":
    agent = StoryAgent()
    example_prompt = "Write a short story about a cat exploring a forest."
    story_dict, status = agent.generate_story(example_prompt)
    print("Status:", status)
    print(json.dumps(story_dict, indent=2, ensure_ascii=False))
