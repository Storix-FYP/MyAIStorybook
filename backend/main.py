import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.agents.prompt_agent import PromptAgent
from backend.agents.story_agent import StoryAgent
from backend.agents.image_agent import ImageAgent
from backend.agents.review_agent import ReviewAgent

import torch

# ------------------------------------------------------
# DEVICE INFORMATION
# ------------------------------------------------------
def get_device_info():
    """Return current compute device info."""
    if torch.cuda.is_available():
        return {"device": "cuda", "name": torch.cuda.get_device_name(0)}
    else:
        return {"device": "cpu"}


# ------------------------------------------------------
# FASTAPI APP CONFIGURATION
# ------------------------------------------------------
app = FastAPI(title="Storybook FYP - AI Enhanced Version (Ollama Dolphin 3)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------
# FILESYSTEM SETUP
# ------------------------------------------------------
GENERATED_DIR = os.path.join(os.path.dirname(__file__), "..", "generated")
IMAGES_DIR = os.path.join(GENERATED_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Serve generated images as static files
app.mount("/generated", StaticFiles(directory=GENERATED_DIR), name="generated")


# ------------------------------------------------------
# ROUTES
# ------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve simple index page."""
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse("<h2>Index page not found. Please ensure backend/static/index.html exists.</h2>")
    return FileResponse(index_path)


@app.get("/device")
async def device():
    """Return CUDA or CPU device info."""
    return get_device_info()


# ------------------------------------------------------
# MAIN API ENDPOINT
# ------------------------------------------------------
@app.post("/api/generate")
async def api_generate(request: Request):
    """Main endpoint to handle prompt → story → image → review pipeline."""
    body = await request.json()
    prompt = body.get("prompt")
    generate_images = body.get("generate_images", True)

    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in request body.")

    # --------------------------------------------------
    # Step 0: PROMPT AGENT → Ask Ollama Dolphin 3
    # --------------------------------------------------
    prompt_agent = PromptAgent(model="dolphin3")  # You can change model name here
    processed_prompt, prompt_type = prompt_agent.process_prompt(prompt)

    print(f"\n[PromptAgent] Type: {prompt_type}")
    print(f"[PromptAgent] Enhanced prompt: {processed_prompt}\n")

    # --------------------------------------------------
    # Handle nonsense or invalid prompts (reject)
    # --------------------------------------------------
    if prompt_type in ["nonsense", "invalid"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Your prompt appears invalid or meaningless. Please enter a more meaningful idea."},
        )

    # --------------------------------------------------
    # Step 1: STORY AGENT → Generate Story
    # --------------------------------------------------
    story_agent = StoryAgent(max_retries=2, max_scenes=3)
    try:
        story_dict, story_status = story_agent.generate_story(processed_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"StoryAgent failed: {e}")

    story_with_images = story_dict
    image_status = None

    # --------------------------------------------------
    # Step 2: IMAGE AGENT → Generate Illustrations
    # --------------------------------------------------
    if generate_images:
        image_agent = ImageAgent()
        try:
            story_with_images, image_status = image_agent.generate_images(story_dict)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ImageAgent failed: {e}")

    # --------------------------------------------------
    # Step 3: REVIEW AGENT → Refine Story
    # --------------------------------------------------
    review_agent = ReviewAgent(max_retries=1)
    final_story, review_status = review_agent.review_story(story_with_images)

    # Combine possible status messages
    status_msg = review_status or image_status or story_status

    # --------------------------------------------------
    # Step 4: Add Metadata
    # --------------------------------------------------
    final_story["meta"] = {"prompt_type": prompt_type, "enhanced_prompt": processed_prompt}

    # Convert image paths to URLs
    for scene in final_story.get("scenes", []):
        path = scene.get("image_path")
        if generate_images and path:
            scene["image_url"] = f"/generated/images/{os.path.basename(path)}"
        else:
            scene["image_url"] = None

    # --------------------------------------------------
    # Return Final Response
    # --------------------------------------------------
    return JSONResponse({"status": status_msg, "story": final_story})


# ------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
