# # backend/agents/image_agent.py
# import os
# import json
# import torch
# from diffusers import StableDiffusionPipeline
# from backend.models.story_schema import Story
# from typing import Dict, Tuple


# class ImageAgent:
#     """
#     Image Agent: Generates illustrations for each scene in the story using diffusers.
#     Returns (updated_story_dict, status_message).
#     """

#     def __init__(self, model_id: str = "runwayml/stable-diffusion-v1-5", device: str = None):
#         # allow explicit device override; else choose cuda if available
#         if device:
#             self.device = device
#         else:
#             self.device = "cuda" if torch.cuda.is_available() else "cpu"
#         print(f"[ImageAgent] Using device: {self.device}")

#         # try to load pipeline (note: may be heavy; if you don't want to load on init, you can lazy-load)
#         dtype = torch.float16 if self.device == "cuda" else torch.float32
#         self.pipe = StableDiffusionPipeline.from_pretrained(
#             model_id,
#             torch_dtype=dtype,
#             safety_checker=None,  # optional: remove if you want safety checks
#         )
#         # move to device
#         self.pipe = self.pipe.to(self.device)

#         # Create output folder
#         self.output_dir = os.path.join("generated", "images")
#         os.makedirs(self.output_dir, exist_ok=True)

#     def generate_images(self, story_dict: Dict, first_only: bool = False) -> Tuple[Dict, str]:
#         """
#         Generate one image per scene in the story (or only first if first_only=True).

#         Args:
#             story_dict: Dict matching Story schema
#             first_only: If True, only create image for the first scene

#         Returns:
#             (updated_story_dict, status_message)
#         """
#         story = Story(**story_dict)

#         scenes_to_process = [story.scenes[0]] if first_only and len(story.scenes) > 0 else list(story.scenes)

#         for scene in scenes_to_process:
#             description = (
#                 scene.image_description
#                 if scene.image_description
#                 else f"Illustration of: {scene.text}"
#             )
#             print(f"[ImageAgent] Generating image for scene {scene.scene_number}: {description}")

#             # generate (the pipeline accepts text prompt first argument)
#             result = self.pipe(description, num_inference_steps=25, height=512, width=512)
#             image = result.images[0]

#             # Save image
#             filename = f"scene_{scene.scene_number}.png"
#             filepath = os.path.join(self.output_dir, filename)
#             image.save(filepath)

#             # Update schema with image path
#             scene.image_path = filepath
#             # ensure image_description remains set
#             if not scene.image_description:
#                 scene.image_description = description

#         # Convert back to dict
#         return story.model_dump(), "Images generated ✅"

# # Example test (only run as script)
# if __name__ == "__main__":
#     from backend.agents.story_agent import StoryAgent

#     story_agent = StoryAgent()
#     story_dict, s_status = story_agent.generate_story("A brave dog explores space with a robot friend.")
#     print("Story status:", s_status)

#     # test only first image so we avoid long runs
#     image_agent = ImageAgent()
#     updated, img_status = image_agent.generate_images(story_dict, first_only=True)
#     print("Image status:", img_status)
#     print(json.dumps(updated, indent=2, ensure_ascii=False))
#     print("✅ Images saved in generated/images/")


# backend/agents/image_agent.py
import os
import json
import torch
from diffusers import StableDiffusionPipeline
from backend.models.story_schema import Story
from typing import Dict, Tuple


class ImageAgent:
    """
    Image Agent: Generates illustrations for each scene in the story using diffusers.
    Returns (updated_story_dict, status_message).
    """

    def __init__(
        self,
        model_path: str = r"C:\Users\wahab\Downloads\FYP\stable-diffusion-webui\models\Stable-diffusion\realismByStableYogi_sd15V9.safetensors",
        device: str = None,
    ):
        # allow explicit device override; else choose cuda if available
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[ImageAgent] Using device: {self.device}")

        # choose dtype
        dtype = torch.float16 if self.device == "cuda" else torch.float32

        # load pipeline from single .safetensors file
        self.pipe = StableDiffusionPipeline.from_single_file(
            model_path,
            torch_dtype=dtype,
            safety_checker=None,  # optional: remove if you want safety checks
        )
        self.pipe = self.pipe.to(self.device)

        # Create output folder
        self.output_dir = os.path.join("generated", "images")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_images(self, story_dict: Dict, first_only: bool = False) -> Tuple[Dict, str]:
        """
        Generate one image per scene in the story (or only first if first_only=True).
        """
        story = Story(**story_dict)

        scenes_to_process = [story.scenes[0]] if first_only and len(story.scenes) > 0 else list(story.scenes)

        for scene in scenes_to_process:
            description = (
                scene.image_description
                if scene.image_description
                else f"Illustration of: {scene.text}"
            )
            print(f"[ImageAgent] Generating image for scene {scene.scene_number}: {description}")

            # generate
            result = self.pipe(description, num_inference_steps=25, height=512, width=512)
            image = result.images[0]

            # Save image
            filename = f"scene_{scene.scene_number}.png"
            filepath = os.path.join(self.output_dir, filename)
            image.save(filepath)

            # Update schema with image path
            scene.image_path = filepath
            if not scene.image_description:
                scene.image_description = description

        # Convert back to dict
        story_out = story.model_dump()
        
        # Remove image_description so frontend only sees text + image
        for scene in story_out["scenes"]:
            scene.pop("image_description", None)
        
        return story_out, "Images generated ✅"



# Example test (only run as script)
if __name__ == "__main__":
    from backend.agents.story_agent import StoryAgent

    story_agent = StoryAgent()
    story_dict, s_status = story_agent.generate_story("A brave dog explores space with a robot friend.")
    print("Story status:", s_status)

    # test only first image so we avoid long runs
    image_agent = ImageAgent()
    updated, img_status = image_agent.generate_images(story_dict, first_only=True)
    print("Image status:", img_status)
    print(json.dumps(updated, indent=2, ensure_ascii=False))
    print("✅ Images saved in generated/images/")
