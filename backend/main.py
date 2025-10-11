# backend/main.py
import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.agents.prompt_agent import PromptAgent
from backend.agents.story_agent import StoryAgent

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
    body = await request.json()
    prompt = body.get("prompt")
    generate_images = body.get("generate_images", True)

    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in request body.")

    # Prompt agent (for metadata only here — Director/Writer will also use/enforce)
    prompt_agent = PromptAgent()
    processed_prompt, prompt_type = prompt_agent.process_prompt(prompt)

    # If prompt is invalid/nonsense, reply 400 with clear message (PromptAgent must set those types)
    if prompt_type in ["invalid", "nonsense"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Your prompt appears invalid or meaningless. Please enter a more meaningful idea."},
        )

    # Use StoryAgent (facade) to run the multi-agent pipeline
    story_agent = StoryAgent(writer_max_scenes=3)
    try:
        story, status_msg = story_agent.generate_story(processed_prompt, generate_images=generate_images)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    # Ensure each scene has image_url keys even if images not generated
    for scene in story.get("scenes", []):
        path = scene.get("image_path")
        if generate_images and path:
            scene["image_url"] = f"/generated/images/{os.path.basename(path)}"
        else:
            scene["image_url"] = None

    # Attach prompt metadata
    story.setdefault("meta", {})
    story["meta"].update({"prompt_type": prompt_type, "enhanced_prompt": processed_prompt})

    return JSONResponse({"status": status_msg, "story": story})

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
