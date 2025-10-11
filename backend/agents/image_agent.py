# backend/agents/image_agent.py
import os
import torch
from diffusers import StableDiffusionPipeline
from backend.models.story_schema import Story
from typing import Dict, Tuple


class ImageAgent:
    """
    ImageAgent: generate images for each scene using a local .safetensors model.
    """

    def __init__(
        self,
        model_path: str = r"C:\Users\wahab\Downloads\FYP\stable-diffusion-webui\models\Stable-diffusion\realismByStableYogi_sd15V9.safetensors",
        device: str = None,
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[ImageAgent] Using device: {self.device}")
        dtype = torch.float16 if self.device == "cuda" else torch.float32

        # load pipeline
        self.pipe = StableDiffusionPipeline.from_single_file(
            model_path,
            torch_dtype=dtype,
            safety_checker=None,
        )
        self.pipe = self.pipe.to(self.device)

        # output dir
        self.output_dir = os.path.join("generated", "images")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_images(self, story_dict: Dict, first_only: bool = False) -> Tuple[Dict, str]:
        story = Story(**story_dict)
        scenes_to_process = [story.scenes[0]] if first_only and len(story.scenes) > 0 else list(story.scenes)

        for scene in scenes_to_process:
            description = scene.image_description or f"Illustration: {scene.text}"
            print(f"[ImageAgent] Generating image for scene {scene.scene_number}: {description}")
            result = self.pipe(description, num_inference_steps=25, height=512, width=512)
            image = result.images[0]
            filename = f"scene_{scene.scene_number}.png"
            filepath = os.path.join(self.output_dir, filename)
            image.save(filepath)
            scene.image_path = filepath
            if not scene.image_description:
                scene.image_description = description

        out = story.model_dump()
        for s in out.get("scenes", []):
            s.pop("image_description", None)
        return out, "Images generated ✅"
