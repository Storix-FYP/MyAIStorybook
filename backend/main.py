# main.py
import os
import uvicorn
import json
import re
import time
import traceback
import torch
import subprocess
import sys
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.agents.editor_agent import export_pdf

# --- Import Agents ---
from backend.agents.prompt_agent import PromptAgent
from backend.agents.story_agent import StoryAgent
from backend.agents.image_agent import ImageAgent
# ReviewerAgent is now only called inside DirectorAgent
# from backend.agents.reviewer_agent import ReviewerAgent

# -------------------
# Utility: Device info
# -------------------
def get_device_info():
    if torch.cuda.is_available():
        return {"device": "cuda", "name": torch.cuda.get_device_name(0)}
    else:
        return {"device": "cpu"}

# -------------------------
# Helper: Safe filename gen
# -------------------------
def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\s-]", "", name).strip().lower()
    name = re.sub(r"[-\s]+", "_", name)
    return name

# -------------------------
# Helper: Save agent output
# -------------------------
def save_agent_output(agent_name: str, title: str, timestamp: int, data: dict):
    safe_title = sanitize_filename(title or "untitled_story")
    dir_map = {
        "prompt": os.path.join(GENERATED_DIR, "prompts"),
        "writer": os.path.join(GENERATED_DIR, "drafts"),
        "reviewer": os.path.join(GENERATED_DIR, "reviews"),
        "editor": os.path.join(GENERATED_DIR, "edits"),
        "story": os.path.join(GENERATED_DIR, "stories")
    }
    out_dir = dir_map.get(agent_name)
    if not out_dir:
        print(f"⚠️ Unknown agent type: {agent_name}")
        return
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{safe_title}_{agent_name}_{timestamp}.json"
    filepath = os.path.join(out_dir, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {agent_name} output to {filepath}")
    except Exception as e:
        print(f"❌ Failed to save {agent_name} output: {e}")

# -------------------------
# FastAPI app setup
# -------------------------
app = FastAPI(title="Storybook FYP - Unified Pipeline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generated directories
BASE_DIR = os.path.dirname(__file__)
GENERATED_DIR = os.path.join(BASE_DIR, "..", "generated")
IMAGES_DIR = os.path.join(GENERATED_DIR, "images")
STORIES_DIR = os.path.join(GENERATED_DIR, "stories")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(STORIES_DIR, exist_ok=True)

# Serve generated static files
app.mount("/generated", StaticFiles(directory=GENERATED_DIR), name="generated")

# -------------------------
# Routes
# -------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse("<h2>Index page not found. Please ensure backend/static/index.html exists.</h2>")
    return FileResponse(index_path)

@app.get("/device")
async def device():
    return get_device_info()

# -------------------------
# Main generation endpoint
# -------------------------
@app.post("/api/generate")
async def api_generate(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    generate_images = body.get("generate_images", True)
    timestamp = int(time.time())

    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in request body.")

    # --- Step 1: PromptAgent ---
    prompt_agent = PromptAgent()
    processed_prompt, prompt_type = prompt_agent.process_prompt(prompt)
    prompt_data = {
        "original_prompt": prompt,
        "prompt_type": prompt_type,
        "enhanced_prompt": processed_prompt
    }
    save_agent_output("prompt", f"prompt_{timestamp}", timestamp, prompt_data)

    if prompt_type in ["invalid", "nonsense"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Your prompt appears invalid or meaningless. Please enter a more meaningful idea."},
        )

    # --- Step 2: StoryAgent (runs the full Writer -> Reviewer -> Editor pipeline) ---
    story_agent = StoryAgent(writer_max_scenes=3)
    try:
        # result now contains 'story', 'outputs', and 'status'
        result, story_status = story_agent.generate_story(processed_prompt, generate_images=False)
        final_story = result.get("story", {})
        agent_outputs = result.get("outputs", {})
        story_title = final_story.get("title", "untitled_story")

        # --- Save all intermediate agent outputs ---
        for agent_name, output_data in agent_outputs.items():
            save_agent_output(agent_name, story_title, timestamp, output_data)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Story generation failed: {e}")

    # --- Step 3: ImageAgent (if enabled) ---
    image_status = "Images not generated."
    if generate_images:
        try:
            print("🖼 Starting image generation...")
            image_agent = ImageAgent()
            for scene in final_story.get("scenes", []):
                description = scene.get("image_description") or scene.get("text", "")
                words = description.split()
                if len(words) > 70:
                    description = " ".join(words[:70])
                    print(f"[Safety] ⚠️ Truncated long image prompt for scene {scene.get('scene_number', '?')}")
                
                scene_number = scene.get("scene_number", 0)
                filename = f"{sanitize_filename(story_title)}_{timestamp}_scene_{scene_number}.png"
                
                print(f"Generating image for scene {scene_number}...")
                image_path = image_agent.generate_image(prompt_text=description, filename=filename)
                scene["image_path"] = image_path

            image_status = "Images generated successfully. ✅"
        except Exception as e:
            traceback.print_exc()
            image_status = f"❌ Image generation failed: {e}"

    # --- Step 4: PDF Export ---
    safe_title = sanitize_filename(final_story.get("title", "untitled_story"))
    pdf_filename = f"{safe_title}_{timestamp}.pdf"
    pdf_path = export_pdf(final_story, pdf_filename)
    print(f"📘 Final PDF available at: {pdf_path}")

    # --- Step 5: Add image URLs for frontend ---
    for scene in final_story.get("scenes", []):
        path = scene.get("image_path")
        if generate_images and path:
            fname = os.path.basename(path)
            scene["image_url"] = f"/generated/images/{fname}"
        else:
            scene["image_url"] = None

    # --- Step 6: Save final story JSON ---
    save_agent_output("story", story_title, timestamp, final_story)

    # --- Step 7: Save final story JSON ---
    STORIES_DIR = os.path.join(GENERATED_DIR, "stories")
    os.makedirs(STORIES_DIR, exist_ok=True)
    story_file = os.path.join(STORIES_DIR, f"{safe_title}_{timestamp}.json")
    with open(story_file, "w", encoding="utf-8") as f:
        json.dump(final_story, f, indent=2, ensure_ascii=False)
    print(f"✅ Story saved successfully at {story_file}")

    # -----------------------------------------------------------------
    # --- NEW: TRIGGER EVALUATION AGENT IN THE BACKGROUND ---
    # -----------------------------------------------------------------
    try:
        # Define the path to the new evaluation agent script
        evaluator_script_path = os.path.join(BASE_DIR, "agents", "evaluation_agent.py")
        
        if os.path.exists(evaluator_script_path):
            print(f"🚀 Kicking off background evaluation for {os.path.basename(story_file)}...")
            # Use sys.executable to run with the same Python interpreter
            command = [sys.executable, evaluator_script_path, story_file]
            # Use Popen for a non-blocking call, so the API can respond immediately
            subprocess.Popen(command)
        else:
            print(f"⚠ Warning: Evaluation agent script not found at {evaluator_script_path}")
    except Exception as e:
        print(f"❌ Failed to start evaluation agent process: {e}")
    # --- END OF NEW CODE ---

    # --- Final combined status ---
    status_msg = review_status or image_status or story_status

    return JSONResponse({"status": status_msg, "story":final_story})


# -------------------------
# Run server
# -------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
