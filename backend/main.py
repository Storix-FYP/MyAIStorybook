import os
import uvicorn
import json # Added for saving the story
import re   # Added for cleaning the filename
import time # Added for unique filenames
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import traceback

# Import agents
from backend.agents.story_agent import StoryAgent
from backend.agents.image_agent import ImageAgent
from backend.agents.review_agent import ReviewAgent

# Utility: device info
import torch

def get_device_info():
    if torch.cuda.is_available():
        return {"device": "cuda", "name": torch.cuda.get_device_name(0)}
    else:
        return {"device": "cpu"}

# --- NEW HELPER FUNCTION ---
# To create a safe filename from the story title
def sanitize_filename(name: str) -> str:
    # Remove special characters
    name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    # Replace spaces with underscores
    name = re.sub(r'[-\s]+', '_', name)
    return name

app = FastAPI(title="Storybook FYP - Iteration 1 Preview")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure generated directories exist
GENERATED_DIR = os.path.join(os.path.dirname(__file__), "..", "generated")
IMAGES_DIR = os.path.join(GENERATED_DIR, "images")
STORIES_DIR = os.path.join(GENERATED_DIR, "stories") # New directory for JSON files
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(STORIES_DIR, exist_ok=True) # Create the stories directory

# Serve generated files as static files
app.mount("/generated", StaticFiles(directory=GENERATED_DIR), name="generated")


@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse("<h2>Index page not found. Please ensure backend/static/index.html exists.</h2>")
    return FileResponse(index_path)


@app.get("/device")
async def device():
    return get_device_info()


@app.post("/api/generate")
async def api_generate(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    generate_images = body.get("generate_images", True)

    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in request body.")

    # Step 1: StoryAgent
    story_agent = StoryAgent(max_retries=2, max_scenes=3)
    story_dict, story_status = story_agent.generate_story(prompt)

    story_with_images = story_dict
    image_status = "No images generated."

    # Step 2: ImageAgent
    if generate_images:
        print("Starting image generation process...")
        image_agent = ImageAgent()
        
        for scene in story_with_images.get("scenes", []):
            # This logic now correctly prioritizes the new `image_description`
            description = scene.get("image_description") or scene.get("text")
            scene_number = scene.get("scene_number")
            filename = f"scene_{scene_number}.png"
            
            print(f"Generating image for scene {scene_number}...")
            image_path = image_agent.generate_image(
                prompt_text=description,
                filename=filename
            )
            scene["image_path"] = image_path
        
        image_status = "Images generated successfully. ✅"

    # Step 3: ReviewAgent
    review_agent = ReviewAgent(max_retries=1)
    final_story, review_status = review_agent.review_story(story_with_images)
    status = review_status or image_status or story_status

    # Convert image paths to URLs
    if generate_images:
        for scene in final_story.get("scenes", []):
            path = scene.get("image_path")
            if path:
                fname = os.path.basename(path)
                scene["image_url"] = f"/generated/images/{fname}"
            else:
                scene["image_url"] = None
    else:
        for scene in final_story.get("scenes", []):
            scene["image_url"] = None

    # --- NEW CODE BLOCK TO SAVE THE STORY JSON ---
    try:
        title = final_story.get("title", "untitled_story")
        timestamp = int(time.time())
        safe_title = sanitize_filename(title)
        json_filename = f"{safe_title}_{timestamp}.json"
        json_filepath = os.path.join(STORIES_DIR, json_filename)
        
        with open(json_filepath, "w", encoding="utf-8") as f:
            json.dump(final_story, f, indent=2, ensure_ascii=False)
        print(f"✅ Story saved successfully as {json_filepath}")
    except Exception as e:
        print(f"❌ Failed to save story JSON: {e}")
        
    return JSONResponse({"status": status, "story": final_story})


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)