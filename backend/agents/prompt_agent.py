import re
import json
import subprocess

class PromptAgent:
    def __init__(self, model="dolphin3"):
        self.model = model

    def _ask_ollama(self, prompt: str) -> str:
        """Send a message to Ollama model and return its text output."""
        result = subprocess.run(
            ["ollama", "run", self.model],
            input=prompt.encode("utf-8"),
            capture_output=True,
        )
        return result.stdout.decode("utf-8").strip()

    def process_prompt(self, user_prompt: str):
        """Analyze and enhance user prompt intelligently."""
        # 🧩 Guard against empty input
        if not user_prompt or not user_prompt.strip():
            return None, "nonsense"

        # 🧩 Check obvious nonsense: only symbols, numbers, or URLs
        if re.fullmatch(r"[\d\W_]+", user_prompt.strip()) or "http" in user_prompt.lower():
            return None, "invalid"
        
        # ✅ NEW: Sanitize dangerous characters to avoid breaking prompt structure
        user_prompt = user_prompt.replace('"', "'")       # Replace double quotes
        user_prompt = user_prompt.replace("{", "[")       # Replace curly braces
        user_prompt = user_prompt.replace("}", "]")       # Replace curly braces

        # 🧠 Step 1 — Build few-shot instruction for Ollama
        system_instruction = """
You are a highly intelligent text classifier and enhancer for a children's story generator.

Your task: classify the user's prompt into one of the following categories:
- "short" → meaningful, very brief idea or phrase (3+ words) suitable for story.
- "normal" → one or two clear sentences describing a story idea.
- "long" → more than 50 words, detailed description.
- "invalid" → URLs, gibberish, only numbers/symbols/special characters.
- "nonsense" → very short or meaningless phrases (<3 words) with no clear context (like "notes", "asdf", "boy", etc).

Then, based on your classification, you must return a JSON object:
{
  "type": "short|normal|long|invalid|nonsense",
  "enhanced": "<meaningful rewritten prompt for story generation>"
}

Enhancement rules:
- If "short" and meaningful → expand into a vivid story idea.
- If "long" → summarize to ~50 words keeping original meaning.
- If "nonsense" → return generic story theme prompt about kindness and imagination.
- If "invalid" → leave "enhanced" empty ("").
- Do not generate full stories, only improved prompts.

Examples:

User: "boy and girl"
Response: {"type": "short", "enhanced": "A heartwarming story about a boy and girl learning friendship in a magical forest."}

User: "book on a"
Response: {"type": "short", "enhanced": "A mysterious book left on a bench leads a child into a magical world of secrets."}

User: "cat cat cat"
Response: {"type": "short", "enhanced": "A silly cat who thinks he's a tiger goes on a jungle adventure in the backyard."}

User: "98217398"
Response: {"type": "invalid", "enhanced": ""}

User: "()/@343,,,"
Response: {"type": "invalid", "enhanced": ""}

User: "(+=||\po,"
Response: {"type": "invalid", "enhanced": ""}

User: "https://google.com"
Response: {"type": "invalid", "enhanced": ""}

User: "notes"
Response: {"type": "nonsense", "enhanced": ""}

User: "A lonely astronaut exploring a forgotten planet with strange life forms."
Response: {"type": "normal", "enhanced": "A curious astronaut explores a forgotten planet full of mysterious life, discovering hope and wonder."}

User: "A detailed 200-word prompt with long story details..."
Response: {"type": "long", "enhanced": "A summarized 50-word version keeping key story context."}
"""

        ollama_prompt = f"""{system_instruction}

User prompt: "{user_prompt}"

Respond ONLY with valid JSON.
"""

        # 🧠 Step 2 — Query Ollama Dolphin
        raw_response = self._ask_ollama(ollama_prompt)

        # 🧠 Step 3 — Parse JSON safely
        try:
            result = json.loads(raw_response)
            prompt_type = result.get("type", "normal").lower()
            enhanced_prompt = result.get("enhanced", "").strip()

            # Fallback safety
            if not enhanced_prompt and prompt_type not in ["invalid", "nonsense"]:
                enhanced_prompt = user_prompt

            return enhanced_prompt, prompt_type

        except Exception as e:
            print(f"[PromptAgent Error] Failed to parse Ollama output: {raw_response}")
            return user_prompt, "normal"
