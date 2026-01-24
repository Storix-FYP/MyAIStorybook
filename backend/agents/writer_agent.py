import json
import subprocess
from typing import Dict, Any, Tuple, Optional

from backend.models.story_schema import Story


class WriterAgent:
    """
    WriterAgent
    - Calls Ollama (mistral-nemo:12b) to produce a structured story JSON.
    - Ensures short, visual `image_description` prompts for compatibility with CLIP (≤77 tokens).
    - Validates with Story pydantic model.
    """

    def __init__(
        self,
        llm_model: str = "mistral-nemo:12b",
        max_retries: int = 2,
        max_scenes: Optional[int] = 3,
        genre: str = "Fantasy",
    ):
        self.llm_model = llm_model
        self.max_retries = max_retries
        self.max_scenes = max_scenes
        self.genre = genre

    def _ask_ollama(self, prompt: str) -> str:
        """Run `ollama run <model>` and return stdout as text."""
        proc = subprocess.run(
            ["ollama", "run", self.llm_model],
            input=prompt.encode("utf-8"),
            capture_output=True,
            check=False,
        )
        return proc.stdout.decode("utf-8").strip()

    def _build_system_prompt(self, max_scenes: int, genre: str) -> str:
        return f"""
You are a professional children's story writer and illustrator prompt designer.

Your task:
Generate a COMPLETE story as a **VALID JSON object** using the following schema:

{{
  "title": "<string>",
  "setting": "<string>",
  "characters": ["name1","name2"],
  "scenes": [
    {{
      "scene_number": 1,
      "text": "<string - full page paragraph>",
      "image_description": "<short, vivid visual prompt for AI image generation>"
    }}
  ]
}}

Rules:
- **GENRE**: Write the story in the **{genre}** genre. Make sure the tone, themes, and style match this genre.
- Limit scenes to EXACTLY {max_scenes} scenes (one scene per page).
- **IMPORTANT**: Each scene's "text" MUST be a FULL PAGE of content - at least 8-12 sentences long (150-200 words per scene). Include rich descriptions, character emotions, dialogue, and engaging storytelling. Make each page feel complete and immersive for children ages 7-10.
- Each scene's "image_description" must be a **single short descriptive phrase (max 15 words)** focusing on visual elements only:
  ✅ Describe what should appear visually (characters, actions, setting, emotions, colors).
  🚫 Do NOT include inner thoughts, dialogue, or long storytelling.
  🚫 Do NOT exceed one concise sentence.
- Example of a good image_description:
  - "Two boys building a small treehouse under bright sunlight, surrounded by green leaves and laughter"
  - "A happy dog and a child playing hide and seek behind a large oak tree"
- Output ONLY valid JSON. No markdown, no commentary, no backticks.
"""

    def generate_story(self, enhanced_prompt: str) -> Tuple[Dict[str, Any], str]:
        """Generate story JSON using Ollama and validate via Story model."""
        last_raw = ""
        for attempt in range(1, self.max_retries + 1):
            try:
                system_prompt = self._build_system_prompt(self.max_scenes or 3, self.genre)
                full_prompt = (
                    f"{system_prompt}\nUser prompt: {enhanced_prompt}\n\nRespond with JSON only."
                )
                raw = self._ask_ollama(full_prompt)
                last_raw = raw

                # Remove accidental markdown
                if raw.startswith("```"):
                    parts = raw.split("```")
                    for p in parts:
                        if p.strip().startswith("{"):
                            raw = p.strip()
                            break
                    else:
                        raw = raw.replace("```", "")

                story_dict = json.loads(raw)

                # Truncate excessive scenes if needed
                if self.max_scenes and "scenes" in story_dict:
                    story_dict["scenes"] = story_dict["scenes"][: self.max_scenes]

                # Safety filter: truncate overly long image prompts
                for scene in story_dict.get("scenes", []):
                    if "image_description" in scene and isinstance(scene["image_description"], str):
                        words = scene["image_description"].split()
                        if len(words) > 20:
                            scene["image_description"] = " ".join(words[:20])

                # Validate schema
                _ = Story(**story_dict)

                return story_dict, f"Story generated ✅ ({len(story_dict.get('scenes', []))} scenes)"

            except Exception as e:
                if attempt >= self.max_retries:
                    raise ValueError(
                        f"WriterAgent failed after {self.max_retries} attempts. "
                        f"Last raw output:\n{last_raw}\n\nError: {e}"
                    )
                # Retry if first attempt fails

        return {}, "Failed to generate story"
