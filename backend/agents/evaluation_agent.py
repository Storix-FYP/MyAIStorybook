# backend/agents/evaluation_agent.py
import sys
import os
import json
import ollama
import textwrap
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
#MODEL_NAME = 'dolphin-mistral:8b'
MODEL_NAME = "mistral-nemo:12b"
# Ensure the path is relative from the project root where main.py runs
EVALUATIONS_DIR = os.path.join("generated", "evaluations")

def read_story_from_json(file_path: str) -> tuple[str | None, str | None]:
    """Reads a story from the specified JSON file and concatenates its scenes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        story_parts = [scene['text'] for scene in data.get('scenes', []) if 'text' in scene]
        if not story_parts:
            print(f"[EvaluationAgent] Error: No scenes with 'text' found in '{file_path}'.")
            return None, None
        
        full_story = " ".join(story_parts)
        title = data.get('title', 'Untitled Story')
        return title, full_story
    except Exception as e:
        print(f"[EvaluationAgent] Error reading or parsing JSON file '{file_path}': {e}")
        return None, None

def build_evaluation_prompt(story_text: str) -> str:
    """Builds the detailed prompt for the LLM to evaluate the story."""
    rubric = """
    1.  **Coherence & Plot (1-10):** Is the plot well-structured with a clear beginning, middle, and end?
    2.  **Character Development (1-10):** Are characters believable with clear motivations? Is there any growth?
    3.  **Setting & Atmosphere (1-10):** Is the setting described effectively? Does it create a mood?
    4.  **Pacing & Flow (1-10):** Does the story move at a good pace? Are transitions smooth?
    5.  **Creativity & Originality (1-10):** How original is the story's concept?
    6.  **Emotional Impact (1-10):** Does the story evoke emotions? Is it engaging?
    """

    prompt = f"""
    You are a literary critic for children's stories. Evaluate the following story based on the provided rubric.
    Provide a score from 1 to 10 for each criterion, with concise reasoning.
    Calculate an average overall score and write a final summary.

    **STORY TO EVALUATE:**
    ---
    {story_text}
    ---

    **EVALUATION RUBRIC:**
    {rubric}

    **IMPORTANT INSTRUCTIONS:**
    Respond ONLY with a valid JSON object. Do not include any text or markdown formatting before or after the JSON.
    Your JSON response must follow this exact structure:
    {{
      "evaluation": {{
        "coherence_and_plot": {{"score": <integer>, "reasoning": "<reasoning>"}},
        "character_development": {{"score": <integer>, "reasoning": "<reasoning>"}},
        "setting_and_atmosphere": {{"score": <integer>, "reasoning": "<reasoning>"}},
        "pacing_and_flow": {{"score": <integer>, "reasoning": "<reasoning>"}},
        "creativity_and_originality": {{"score": <integer>, "reasoning": "<reasoning>"}},
        "emotional_impact": {{"score": <integer>, "reasoning": "<reasoning>"}}
      }},
      "overall_score": <float>,
      "final_summary": "<summary>"
    }}
    """
    return prompt

def evaluate_story(story_text: str) -> dict | None:
    """Sends the story to the Ollama LLM for evaluation."""
    prompt = build_evaluation_prompt(story_text)
    try:
        print(f"\n[EvaluationAgent] Contacting Ollama model '{MODEL_NAME}'...")
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.1},
            format='json'
        )
        evaluation_content = response['message']['content']
        return json.loads(evaluation_content)
    except Exception as e:
        print(f"\n[EvaluationAgent] Error communicating with Ollama: {e}")
        return None

def save_evaluation_as_image(evaluation_data: dict, title: str, output_path: str):
    """Saves the evaluation results as a PNG image."""
    width, margin = 800, 40
    bg_color, text_color, heading_color, score_color = (255, 255, 255), (10, 10, 10), (0, 0, 0), (0, 100, 0)
    
    try:
        font_regular = ImageFont.truetype("arial.ttf", 16)
        font_bold = ImageFont.truetype("arialbd.ttf", 20)
    except IOError:
        font_regular = font_bold = ImageFont.load_default()

    lines = []
    lines.append((f"Literary Evaluation: '{title}'", font_bold, heading_color))
    lines.append(("-"*80, font_regular, (200, 200, 200)))
    for criterion, details in evaluation_data.get('evaluation', {}).items():
        name = criterion.replace('_', ' ').title()
        score = details.get('score', 'N/A')
        reasoning = details.get('reasoning', 'N/A')
        lines.append((f"-> {name}:", font_bold, heading_color, f"{score}/10"))
        for line in textwrap.wrap(f"   Reasoning: {reasoning}", width=80):
            lines.append((line, font_regular, text_color))
        lines.append((" ", font_regular, text_color))
    
    lines.append(("-"*80, font_regular, (200, 200, 200)))
    overall_score = evaluation_data.get('overall_score', 'N/A')
    summary = evaluation_data.get('final_summary', 'N/A')
    lines.append((f"OVERALL SCORE: {overall_score}/10", font_bold, heading_color))
    lines.append(("\nFINAL SUMMARY:", font_bold, heading_color))
    for line in textwrap.wrap(summary, width=85):
        lines.append((line, font_regular, text_color))

    height = sum(font.getbbox("A")[3] + 5 for text, font, *rest in lines) + 2 * margin
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    y_pos = margin

    for text, font, color, *rest in lines:
        draw.text((margin, y_pos), text, font=font, fill=color)
        if rest:
            score_text = rest[0]
            score_width = draw.textlength(score_text, font=font_bold)
            draw.text((width - margin - score_width, y_pos), score_text, font=font_bold, fill=score_color)
        y_pos += font.getbbox(text)[3] + 5

    img.save(output_path)
    print(f"[EvaluationAgent] Evaluation saved as image to: '{output_path}'")

def main():
    """Main execution block, called when the script is run directly."""
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path_to_story_json_file>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    
    title, story_text = read_story_from_json(json_file_path)
    if not story_text:
        sys.exit(1)

    evaluation = evaluate_story(story_text)
    if not evaluation:
        sys.exit(1)

    os.makedirs(EVALUATIONS_DIR, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(json_file_path))[0]
    output_image_path = os.path.join(EVALUATIONS_DIR, f"{base_name}_evaluation.png")
    
    save_evaluation_as_image(evaluation, title, output_image_path)
    
    # Clear GPU cache after evaluation completes
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            print("[EvaluationAgent] 🧹 GPU cache cleared after evaluation")
    except Exception as e:
        print(f"[EvaluationAgent] ⚠️ Could not clear GPU cache: {e}")

if __name__ == "__main__":
    main()