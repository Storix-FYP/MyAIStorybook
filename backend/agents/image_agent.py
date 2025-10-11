# backend/agents/image_agent.py
import os
import torch
from diffusers import StableDiffusionPipeline, AutoPipelineForImage2Image, DPMSolverMultistepScheduler
from PIL import Image

class ImageAgent:
    """
    Image Agent: Generates illustrations using a local Stable Diffusion model,
    including a high-resolution fix.
    """
    def __init__(
        self,
        model_path: str = r"C:\Users\wahab\Downloads\FYP\stable-diffusion-webui\models\Stable-diffusion\dreamshaper_8.safetensors"
    ):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model checkpoint not found at '{model_path}'. "
                "Please update the path in ImageAgent."
            )

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.generator = torch.Generator(device=self.device)
        print(f"[ImageAgent] Using device: {self.device}")

        # --- Model Loading ---
        print("[ImageAgent] Loading Stable Diffusion model... This may take a moment.")
        
        # 1. Use StableDiffusionPipeline to load the local .safetensors file
        self.pipeline = StableDiffusionPipeline.from_single_file(
            model_path,
            torch_dtype=torch.float16,
            use_safetensors=True,
        )

        # 2. Use a high-quality scheduler
        self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipeline.scheduler.config, use_karras_sigmas=True
        )

        # 3. Move pipeline to the GPU and create the img2img pipeline for the hires-fix
        self.pipeline.to(self.device)
        self.img2img_pipeline = AutoPipelineForImage2Image.from_pipe(self.pipeline)
        
        print("[ImageAgent] Model loaded successfully.")

        # output dir
        self.output_dir = os.path.join("generated", "images")
        os.makedirs(self.output_dir, exist_ok=True)


    def generate_image(self, prompt_text: str, filename: str = "output.png"):
        """
        Generates an image with a high-resolution fix pass.
        
        Args:
            prompt_text (str): The text prompt to generate an image from.
            filename (str): The filename to save the image as.
        """
        print(f"[ImageAgent] Generating image for prompt: '{prompt_text}'...")

        # Advanced prompting for higher quality
        positive_prompt = f"masterpiece, best quality, ultra-detailed, photorealistic illustration, {prompt_text}"
        negative_prompt = (
            "(deformed, distorted, disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, "
            "extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), "
            "disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation, "
            "BadDream, UnrealisticDream"
        )

        # --- High-Resolution Fix (Two-Pass Generation) ---
        
        # Pass 1: Generate a smaller image (txt2img)
        print("[ImageAgent] Running Pass 1 (txt2img)...")
        low_res_image = self.pipeline(
            prompt=positive_prompt,
            negative_prompt=negative_prompt,
            width=512,
            height=512,
            num_inference_steps=25,
            guidance_scale=7,
            generator=self.generator,
        ).images[0]
        
        # Pass 2: Upscale using image-to-image
        print("[ImageAgent] Running Pass 2 (img2img for Hires. fix)...")
        high_res_image = self.img2img_pipeline(
            prompt=positive_prompt,
            negative_prompt=negative_prompt,
            image=low_res_image,
            num_inference_steps=30,
            strength=0.5,  # Denoising strength
            guidance_scale=7,
            generator=self.generator,
        ).images[0]

        # Save the final image
        filepath = os.path.join(self.output_dir, filename)
        try:
            high_res_image.save(filepath)
            print(f"✅ Image saved successfully as {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ An unexpected error occurred while saving the image: {e}")
            return None

# --- Example of how to use the class ---
if __name__ == "__main__":
    try:
        image_agent = ImageAgent()
        image_agent.generate_image(
            prompt_text="A brave dog in a space suit exploring a vibrant alien planet",
            filename="space_dog.png"
        )
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
