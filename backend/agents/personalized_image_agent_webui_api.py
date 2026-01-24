# backend/agents/personalized_image_agent_webui_api.py
import os
import base64
import requests
from io import BytesIO
from PIL import Image
from pathlib import Path

class PersonalizedImageAgentWebUIAPI:
    """
    Personalized image generation using Stable Diffusion WebUI Local API
    with IP-Adapter FaceID Plus v2 for facial likeness
    """
    
    def __init__(
        self,
        webui_url: str = "http://127.0.0.1:7861",  # Changed to 7861
        sd_model_path: str = None,
        lora_path: str = None,
        **kwargs
    ):
        """
        Initialize with WebUI API
        
        Args:
            webui_url: WebUI server URL (default: localhost:7860)
            sd_model_path: Not used (WebUI manages models)
            lora_path: LoRA name (just the filename without extension)
        """
        self.webui_url = webui_url.rstrip('/')
        self.user_photo = None
        self.output_dir = Path("generated/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # LoRA name
        if lora_path:
            self.lora_name = Path(lora_path).stem
        else:
            self.lora_name = "ip-adapter-faceid-plusv2_sd15_lora"
        
        # Test connection
        try:
            response = requests.get(f"{self.webui_url}/sdapi/v1/sd-models", timeout=2)
            if response.status_code == 200:
                print(f"[WebUI API] ✅ Connected to WebUI at {self.webui_url}")
            else:
                print(f"[WebUI API] ⚠️ WebUI responded with status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[WebUI API] ❌ Cannot connect to WebUI: {e}")
            print(f"[WebUI API] Make sure WebUI is running at {self.webui_url}")
            raise RuntimeError(f"WebUI not available at {self.webui_url}")
    
    def set_user_photo(self, photo_path_or_image):
        """Set user's reference photo"""
        if isinstance(photo_path_or_image, str):
            if not os.path.exists(photo_path_or_image):
                raise FileNotFoundError(f"Photo not found: {photo_path_or_image}")
            self.user_photo = Image.open(photo_path_or_image).convert("RGB")
            print(f"[WebUI API] ✅ User photo loaded")
        elif isinstance(photo_path_or_image, Image.Image):
            self.user_photo = photo_path_or_image.convert("RGB")
            print("[WebUI API] ✅ User photo set")
        else:
            raise ValueError("photo_path_or_image must be a file path or PIL Image")
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def _load_lora(self):
        """Load LoRA via WebUI API options endpoint"""
        try:
            # Set LoRA via API
            response = requests.post(
                f"{self.webui_url}/sdapi/v1/options",
                json={"sd_lora": f"{self.lora_name}"},
                timeout=5
            )
            if response.status_code == 200:
                print(f"[WebUI API] ✅ LoRA loaded via API: {self.lora_name}")
                return True
            else:
                print(f"[WebUI API] ⚠️ Failed to load LoRA via API (status {response.status_code})")
                return False
        except Exception as e:
            print(f"[WebUI API] ⚠️ Could not load LoRA via API: {e}")
            return False
    
    def generate_personalized_image(
        self,
        prompt_text: str,
        filename: str = "personalized_output.png",
        scale: float = 1.0,  # Increased from 1.0 for stronger facial likeness without LoRA
        num_inference_steps: int = 30,
        guidance_scale: float = 5.0,  # Match WebUI settings exactly
        control_start: float = 0.2,  # Start from beginning for maximum facial influence
        control_end: float = 0.8  # Apply through entire generation
    ):
        """
        Generate personalized image using WebUI API
        
        Args:
            prompt_text: Text description
            filename: Output filename
            scale: IP-Adapter weight (1.0 default)
            num_inference_steps: Steps (30 default)
            guidance_scale: CFG scale (1.5 default, matches WebUI)
            control_start: Start control at % (0.2 default)
            control_end: End control at % (0.8 default)
            
        Returns:
            Path to generated image
        """
        if self.user_photo is None:
            raise ValueError("User photo not set. Call set_user_photo() first.")
        
        print(f"[WebUI API] Generating: '{prompt_text}'...")
        
        # Load LoRA via API before generation
        self._load_lora()
        
        # Prepare prompt with LoRA - keep it simple for better facial likeness
        positive_prompt = f"<lora:{self.lora_name}:1.0> {prompt_text}, best quality, high quality"
        
        # Simple negative prompt for quality
        negative_prompt = "bad quality, worst quality, blurry, deformed, disfigured"
        
        print(f"[WebUI API] ✅ Prompt prepared")
        
        # Convert image to base64
        image_b64 = self._image_to_base64(self.user_photo)
        
        # Create ControlNet unit
        controlnet_unit = {
            "enabled": True,
            "module": "ip-adapter_face_id_plus",
            "model": "ip-adapter-faceid-plusv2_sd15",
            "weight": scale,
            "image": image_b64,
            "resize_mode": "Crop and Resize",  # String, not int
            "control_mode": "Balanced",  # String enum value
            "guidance_start": control_start,
            "guidance_end": control_end,
        }
        
        # Create txt2img payload with explicit LoRA loading
        payload = {
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "steps": num_inference_steps,
            "cfg_scale": guidance_scale,
            "width": 512,
            "height": 512,
            "sampler_name": "DPM++ 2M Karras",
            "batch_size": 1,
            "n_iter": 1,
            "override_settings": {
                "CLIP_stop_at_last_layers": 1,  # Better for IP-Adapter
            },
            "extra_generation_params": {
                f"Lora hashes": f"{self.lora_name}: 1.0",
            },
            "alwayson_scripts": {
                "controlnet": {
                    "args": [controlnet_unit]
                }
            }
        }
        
        print(f"[WebUI API] Calling WebUI txt2img...")
        print(f"  - Steps: {num_inference_steps}, CFG: {guidance_scale}")
        print(f"  - Control: {control_start:.1%} to {control_end:.1%}, Weight: {scale}")
        print(f"  - Prompt: {positive_prompt[:100]}...")  # Show first 100 chars
        print(f"  - LoRA: {self.lora_name} (via prompt tag + extra_generation_params)")
        
        try:
            # Call WebUI API
            response = requests.post(
                f"{self.webui_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            
            # Decode image
            image_data = base64.b64decode(result['images'][0])
            image = Image.open(BytesIO(image_data))
            
            # Save image
            output_path = self.output_dir / filename
            image.save(output_path)
            print(f"✅ Image saved: {output_path}")
            
            return str(output_path)
            
        except requests.exceptions.RequestException as e:
            print(f"[WebUI API] ❌ Request failed: {e}")
            raise
        except Exception as e:
            print(f"[WebUI API] ❌ Error: {e}")
            raise
