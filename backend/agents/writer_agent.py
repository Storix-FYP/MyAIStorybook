# backend/agents/writer_agent.py
import json
import subprocess
from typing import Dict, Any, Tuple, Optional

from backend.models.story_schema import Story


class WriterAgent:
    """
    WriterAgent
    - Calls Ollama (dolphin3) to produce a structured story JSON.
    - Validates with Story pydantic model.
    """

    def __init__(self, llm_model: str = "dolphin3", max_retries: int = 2, max_scenes: Optional[int] = 3):
        self.llm_model = llm_model
        self.max_retries = max_retries
        self.max_scenes = max_scenes

    def _ask_ollama(self, prompt: str) -> str:
        """Run `ollama run <model>` and return stdout as text."""
        # Using subprocess for local Ollama CLI. You may swap to ollama python bindings if installed.
        proc = subprocess.run(
            ["ollama", "run", self.llm_model],
            input=prompt.encode("utf-8"),
            capture_output=True,
            check=False,
        )
        return proc.stdout.decode("utf-8").strip()

    def _build_system_prompt(self, max_scenes: int) -> str:
        return f"""
You are a children's story writer and MUST output VALID JSON matching this schema:

{{
  "title": "<string>",
  "setting": "<string>",
  "characters": ["name1","name2"],
  "scenes": [
    {{
      "scene_number": 1,
      "text": "<string - paragraph>",
      "image_description": "<short visual prompt>"
    }}
  ]
}}

Rules:
- Limit scenes to at most {max_scenes}.
- Each scene's text should be coherent, child-friendly, and about 5-8 sentences (if possible).
- Do NOT output markdown or commentary. ONLY output the JSON object.
- Use simple language suitable for ages 7-10.
- Keep JSON valid.
"""

    def generate_story(self, enhanced_prompt: str) -> Tuple[Dict[str, Any], str]:
        """Generate story JSON using Ollama and validate via Story model."""
        last_raw = ""
        for attempt in range(1, self.max_retries + 1):
            try:
                system_prompt = self._build_system_prompt(self.max_scenes or 3)
                full_prompt = f"{system_prompt}\nUser prompt: {enhanced_prompt}\n\nRespond with JSON only."
                raw = self._ask_ollama(full_prompt)
                last_raw = raw

                # Clean common backticks if present
                if raw.startswith("```"):
                    # try to extract inner content
                    parts = raw.split("```")
                    for p in parts:
                        if p.strip().startswith("{"):
                            raw = p.strip()
                            break
                    else:
                        raw = raw.replace("```", "")

                # Attempt to parse
                story_dict = json.loads(raw)

                # If max_scenes set, truncate scenes
                if self.max_scenes and "scenes" in story_dict:
                    if len(story_dict["scenes"]) > self.max_scenes:
                        story_dict["scenes"] = story_dict["scenes"][: self.max_scenes]

                # Validate using pydantic Story model (raises if invalid)
                _ = Story(**story_dict)

                return story_dict, f"Story generated ✅ ({len(story_dict.get('scenes', []))} scenes)"

            except Exception as e:
                # Retry on failure
                if attempt >= self.max_retries:
                    # include last_raw for debugging in the exception
                    raise ValueError(f"WriterAgent failed after {self.max_retries} attempts. Last raw output:\n{last_raw}\n\nError: {e}")
                # else retry

        return {}, "Failed to generate story"
