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
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.agents.editor_agent import export_pdf

# --- Import Agents ---
from backend.agents.prompt_agent import PromptAgent
from backend.agents.story_agent import StoryAgent
from backend.agents.image_agent import ImageAgent
from backend.agents.chatbot_agent import ChatbotAgent
from backend.agents.idea_workshop_agent import IdeaWorkshopAgent
# ReviewerAgent is now only called inside DirectorAgent
# from backend.agents.reviewer_agent import ReviewerAgent

# --- Import Auth ---
from backend.auth.routes import router as auth_router
from backend.auth.database import engine, Base, get_db
from backend.auth.dependencies import get_current_user_optional
from backend.auth.models import User
from backend.auth.db_models import Story, ChatConversation, ChatMessage, WorkshopSession, WorkshopMessage, WorkshopStory
from sqlalchemy.orm import Session

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

# Initialize database tables (lazy initialization with error handling)
def init_database():
    """Initialize database tables if connection is available"""
    try:
        # Import all models to ensure they're registered
        from backend.auth.db_models import Story, ChatConversation, ChatMessage, WorkshopSession, WorkshopMessage, WorkshopStory
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables initialized successfully (including Story, Chat, and Workshop tables)")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize database: {e}")
        print("⚠️ Authentication features will not be available until database is configured.")
        print("⚠️ To fix: Set DATABASE_URL environment variable or configure PostgreSQL connection.")

# Try to initialize database, but don't fail if it's not available
init_database()

# Include auth routes
app.include_router(auth_router)

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
async def api_generate(
    request: Request, 
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    body = await request.json()
    prompt = body.get("prompt")
    generate_images = body.get("generate_images", True)
    mode = body.get("mode", "simple")  # 'simple' or 'personalized'
    timestamp = int(time.time())

    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in request body.")
    
    # Check if user is authenticated for image generation
    if generate_images and current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login to generate images. Guest users can only create text stories."
        )

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

    # --- Save story to database ---
    story_id = None
    try:
        db_story = Story(
            user_id=current_user.id if current_user else None,
            title=story_title,
            mode=mode,
            story_data=final_story
        )
        db.add(db_story)
        db.commit()
        db.refresh(db_story)
        story_id = db_story.id
        print(f"✅ Story saved to database with ID: {story_id}")
    except Exception as e:
        print(f"⚠️ Warning: Failed to save story to database: {e}")
        db.rollback()
        # Continue even if database save fails (for backward compatibility)

    # --- Final combined status ---
    status_msg = image_status or story_status

    return JSONResponse({
        "status": status_msg, 
        "story": final_story,
        "story_id": story_id  # Return story ID for chat reference
    })


# -------------------------
# Chatbot endpoints
# -------------------------
@app.post("/api/chat")
async def api_chat(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Handle character chatbot conversations (STATELESS - no conversation history saved)
    Request body: {story_id, character_name, user_message}
    """
    try:
        body = await request.json()
        story_id = body.get("story_id")
        character_name = body.get("character_name")
        user_message = body.get("user_message")
        
        # Validation
        if not story_id or not character_name or not user_message:
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: story_id, character_name, user_message"
            )
        
        # Load story from database
        db_story = db.query(Story).filter(Story.id == story_id).first()
        if not db_story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        story_data = db_story.story_data
        
        # Validate character exists in story
        characters = story_data.get("characters", [])
        if character_name not in characters:
            raise HTTPException(
                status_code=400,
                detail=f"Character '{character_name}' not found in story. Available: {characters}"
            )
        
        # Generate response using ChatbotAgent (no conversation history)
        chatbot = ChatbotAgent(story_data, character_name)
        character_response = chatbot.chat(user_message)
        
        # Return response without saving anything to database
        return JSONResponse({
            "response": character_response,
            "character": character_name
        })
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")




# -------------------------
# Idea Workshop endpoints
# -------------------------
@app.post("/api/workshop/start")
async def start_workshop(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Start a new workshop session
    Request body: {mode: 'improvement' | 'new_idea'}
    """
    try:
        body = await request.json()
        mode = body.get("mode")
        
        if mode not in ['improvement', 'new_idea']:
            raise HTTPException(status_code=400, detail="Mode must be 'improvement' or 'new_idea'")
        
        # Create new session
        session = WorkshopSession(
            user_id=current_user.id if current_user else None,
            mode=mode,
            status='active'
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Generate initial message based on mode
        if mode == 'improvement':
            initial_message = "Welcome to Story Improvement Mode! Please paste your story below (maximum 300 words)."
        else:
            initial_message = "Welcome to New Idea Mode! Tell me about your story idea, and I'll help you build it!"
        
        # Save initial assistant message
        initial_msg = WorkshopMessage(
            session_id=session.id,
            role='assistant',
            message=initial_message
        )
        db.add(initial_msg)
        db.commit()
        
        return JSONResponse({
            "session_id": session.id,
            "mode": mode,
            "initial_message": initial_message
        })
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error starting workshop: {str(e)}")


@app.post("/api/workshop/chat")
async def workshop_chat(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Handle workshop conversation
    Request body: {session_id, user_message}
    """
    try:
        body = await request.json()
        session_id = body.get("session_id")
        user_message = body.get("user_message")
        
        if not session_id or not user_message:
            raise HTTPException(status_code=400, detail="Missing session_id or user_message")
        
        # Load session
        session = db.query(WorkshopSession).filter(WorkshopSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Load conversation history
        messages = db.query(WorkshopMessage).filter(
            WorkshopMessage.session_id == session_id
        ).order_by(WorkshopMessage.created_at).all()
        
        history = [{
            "role": msg.role,
            "message": msg.message,
            "metadata": msg.message_metadata or {}
        } for msg in messages]
        
        # Create agent and process message
        agent = IdeaWorkshopAgent(session.mode, history)
        response, metadata = agent.process_message(user_message)
        
        # CRITICAL FIX: Save metadata on USER message too (not just assistant)
        # This allows the next agent instance to find requirements from history
        user_msg = WorkshopMessage(
            session_id=session_id,
            role='user',
            message=user_message,
            message_metadata=metadata  # Save extracted requirements
        )
        db.add(user_msg)
        db.commit()
        
        # Save assistant response
        assistant_msg = WorkshopMessage(
            session_id=session_id,
            role='assistant',
            message=response,
            message_metadata=metadata
        )
        db.add(assistant_msg)
        db.commit()
        
        # Check if ready to generate
        ready_to_generate = agent.should_generate_story(user_message)
        
        return JSONResponse({
            "response": response,
            "ready_to_generate": ready_to_generate,
            "metadata": metadata
        })
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Workshop chat error: {str(e)}")


@app.get("/api/workshop/history/{session_id}")
async def get_workshop_history(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Load full workshop conversation history
    """
    try:
        # Load session
        session = db.query(WorkshopSession).filter(WorkshopSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Load messages
        messages = db.query(WorkshopMessage).filter(
            WorkshopMessage.session_id == session_id
        ).order_by(WorkshopMessage.created_at).all()
        
        # Load stories if any
        stories = db.query(WorkshopStory).filter(
            WorkshopStory.session_id == session_id
        ).order_by(WorkshopStory.version).all()
        
        return JSONResponse({
            "session_id": session_id,
            "mode": session.mode,
            "status": session.status,
            "messages": [{
                "role": msg.role,
                "message": msg.message,
                "metadata": msg.message_metadata,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            } for msg in messages],
            "stories": [{
                "version": story.version,
                "story_text": story.story_text,
                "created_at": story.created_at.isoformat() if story.created_at else None
            } for story in stories]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading history: {str(e)}")


@app.post("/api/workshop/generate")
async def generate_workshop_story(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Generate story from workshop session
    Request body: {session_id}
    """
    try:
        body = await request.json()
        session_id = body.get("session_id")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Missing session_id")
        
        # Load session
        session = db.query(WorkshopSession).filter(WorkshopSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Load conversation history
        messages = db.query(WorkshopMessage).filter(
            WorkshopMessage.session_id == session_id
        ).order_by(WorkshopMessage.created_at).all()
        
        history = [{
            "role": msg.role,
            "message": msg.message,
            "metadata": msg.message_metadata or {}
        } for msg in messages]
        
        # Create agent and generate story
        agent = IdeaWorkshopAgent(session.mode, history)
        story_text = agent.generate_story()
        
        # Get current version
        existing_stories = db.query(WorkshopStory).filter(
            WorkshopStory.session_id == session_id
        ).order_by(WorkshopStory.version.desc()).first()
        
        next_version = (existing_stories.version + 1) if existing_stories else 1
        
        # Save generated story
        workshop_story = WorkshopStory(
            session_id=session_id,
            version=next_version,
            story_text=story_text,
            user_story_text=agent.user_story  # For improvement mode
        )
        db.add(workshop_story)
        db.commit()
        db.refresh(workshop_story)
        
        return JSONResponse({
            "story_text": story_text,
            "version": next_version,
            "story_id": workshop_story.id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Story generation error: {str(e)}")


# -------------------------
# Run server
# -------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
