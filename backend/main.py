# backend/main.py
import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import traceback

# Import agents (assumes these modules exist as created earlier)
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

app = FastAPI(title="Storybook FYP - Iteration 1 Preview")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure generated images dir exists
GENERATED_DIR = os.path.join(os.path.dirname(__file__), "..", "generated")
IMAGES_DIR = os.path.join(GENERATED_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Serve generated images as static files
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
    """
    Trigger a pipeline run with a JSON body:
    { "prompt": "User prompt text" }
    Returns final story JSON (with image paths).
    """
    body = await request.json()
    prompt = body.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in request body.")

    # Step 1: StoryAgent
    story_agent = StoryAgent(max_retries=2)
    try:
        story_dict, story_status = story_agent.generate_story(prompt)  # unpack tuple
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"StoryAgent failed: {e}")

    # Step 2: ImageAgent
    image_agent = ImageAgent()
    try:
        story_with_images, image_status = image_agent.generate_images(story_dict)  # unpack tuple
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ImageAgent failed: {e}")
    
    # Step 3: ReviewAgent
    review_agent = ReviewAgent(max_retries=1)
    final_story, review_status = review_agent.review_story(story_with_images)
    
    # Pick which status to return (prefer review, then image, then story)
    status = review_status or image_status or story_status


    # Convert local image paths to URLs served by FastAPI
    for scene in final_story.get("scenes", []):
        path = scene.get("image_path")
        if path:
            fname = os.path.basename(path)
            scene["image_url"] = f"/generated/images/{fname}"
        else:
            scene["image_url"] = None

    return JSONResponse({"status": status, "story": final_story})


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
