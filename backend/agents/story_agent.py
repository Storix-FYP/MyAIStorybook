# backend/agents/story_agent.py
import json
from typing import Dict, Any, Tuple
from ollama import chat
from backend.models.story_schema import Story


class StoryAgent:
    """
    Story Agent: Generates a structured story via Dolphin3 (Ollama).
    - Improved storytelling quality.
    - Configurable scene limit for CPU/GPU mode.
    """

    def __init__(self, model: str = "llama3.1:8b-instruct-q4_K_M", max_retries: int = 3, max_scenes: int = 3):
        self.model = model
        self.max_retries = max_retries
        self.max_scenes = max_scenes

    def _clean_json_output(self, raw_text: str) -> str:
        if not raw_text:
            return raw_text
        text = raw_text.strip()
        if text.startswith("```") and "```" in text[3:]:
            parts = text.split("```")
            for p in parts:
                if "{" in p:
                    p_clean = p.lstrip()
                    if p_clean.lower().startswith("json"):
                        p_clean = p_clean[4:].lstrip()
                    return p_clean.strip()
            text = text.replace("```", "")
        if text.lower().startswith("json\n"):
            text = text[len("json\n"):].lstrip()
        return text.strip()

    def generate_story(self, prompt: str) -> Tuple[Dict[str, Any], str]:
        """
        Generate a structured story (JSON) validated by Story schema.
        """
        # --- MODIFIED SYSTEM PROMPT ---
        # Added a rule to generate a concise `image_description` for each scene.
        system_prompt = (
                "You are a skilled children's story writer and JSON generator. "
                "You must create imaginative, emotionally engaging, and structured stories for children aged 7–10. "
                "Output only valid JSON matching this schema:\n\n"
                "Story(title: str, setting: str, characters: [str], "
                "scenes: List[Scene(scene_number: int, text: str, image_description: str)]).\n\n"
                "Rules:\n"
                f"1. Create a story with exactly {self.max_scenes} scenes.\n"
                "2. For each scene, write a `text` that is at least 7–8 sentences long and describes meaningful story progress.\n"
                "3. For each scene, ALSO write a short, visually-focused `image_description`. This description should be a concise prompt (under 50 words) for an image generation AI, focusing on keywords, the subject, and the setting. Do not use the full scene text.\n"
                "4. Maintain a smooth flow — each scene should build naturally from the previous one.\n"
                "5. Include emotional depth and vivid sensory details (what characters see, hear, feel).\n"
                "6. Ensure the story ends with a moral, message, or emotional resolution.\n"
                "7. Output JSON only — no markdown, no explanations, no comments."
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
                    options={
                         "temperature": 0.9,
                         "num_predict": 1024  # Increased token limit for better descriptions
                    }
                )

                raw_text = getattr(response.message, "content", None) if hasattr(response, "message") else None
                if not raw_text and isinstance(response, dict):
                    raw_text = response.get("message", {}).get("content")
                if not raw_text:
                    raw_text = str(response)

                cleaned = self._clean_json_output(raw_text)
                story_dict = json.loads(cleaned)

                story = Story(**story_dict)
                return story.model_dump(), f"Story generated ✅ ({len(story.scenes)} scenes)"

            except Exception as e:
                print(f"[Retry {attempt}/{self.max_retries}] Invalid output: {e}")
                if attempt == self.max_retries:
                    raise ValueError(f"Failed after {self.max_retries} retries. Last raw output:\n{raw_text}")

        return {}, "Failed to generate story"


if __name__ == "__main__":
    agent = StoryAgent(max_scenes=3)
    example_prompt = "Write a story about a shy turtle who learns to make friends at the lake."
    story_dict, status = agent.generate_story(example_prompt)
    print("Status:", status)
    print(json.dumps(story_dict, indent=2, ensure_ascii=False))