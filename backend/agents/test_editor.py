# backend/agents/test_editor.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '..', '..')))

import os
from editor_agent import EditorAgent

# Optional: switch between dummy image mode and image generation mode
USE_IMAGE_AGENT = False

# Optional import (only used if USE_IMAGE_AGENT = True)
if USE_IMAGE_AGENT:
    from image_agent import ImageAgent


def test_editor_agent_with_images():
    editor = EditorAgent()

    # Create dummy image folder if not exist
    sample_img_dir = os.path.join(os.path.dirname(_file_), "..", "tests", "sample_images")
    os.makedirs(sample_img_dir, exist_ok=True)

    # Prepare dummy image files (optional placeholders)
    # For local CPU testing, you can place any small .jpg/.png here manually
    scene1_img = os.path.join(sample_img_dir, "scene_1.png")
    scene2_img = os.path.join(sample_img_dir, "scene_2.png")

    # --- If GPU/ImageAgent available, generate images dynamically ---
    if USE_IMAGE_AGENT:
        image_agent = ImageAgent()
        story_prompts = [
            "A boy and girl in a magical forest filled with glowing trees",
            "A shining pond surrounded by sparkling stars and fireflies"
        ]
        generated_paths = []
        for i, prompt in enumerate(story_prompts):
            img_path = image_agent.generate_image(prompt, output_name=f"scene{i+1}")
            generated_paths.append(img_path)

        scene1_img, scene2_img = generated_paths

    # --- Story structure with image paths ---
    story = {
        "title": "The Forest Adventure",
        "characters": ["Boy", "Girl"],
        "scenes": [
            {
                "scene_number": 1,
                "text": "The boy and girl went to the forest and saw magical lights.",
                "image_path": scene1_img if os.path.exists(scene1_img) else None
            },
            {
                "scene_number": 2,
                "text": "They discovered a hidden pond that shimmered like stars.",
                "image_path": scene2_img if os.path.exists(scene2_img) else None
            }
        ]
    }

    # Run the editor
    edited_story, message = editor.edit_story(story)

    print("\n✏ Edited Story:\n", edited_story)
    print("\n📋 Message:", message)


if _name_ == "_main_":
    test_editor_agent_with_images()