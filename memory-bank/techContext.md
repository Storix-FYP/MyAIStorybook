# Technical Context: MyAIStorybook (Current Implementation - Iteration 1)

## Technology Stack

### Backend Technologies (Implemented)
- **FastAPI**: Python web framework for API
- **Python 3.11**: Primary language
- **Ollama**: Local LLM serving (llama3.1:8b-instruct-q4_K_M)
- **Diffusers + PyTorch**: Stable Diffusion image generation
- **Pydantic**: Request/response validation
- **Uvicorn**: ASGI server
- **ReportLab**: PDF generation

### Frontend Technologies (Implemented)
- **Next.js 14.2**: React framework with App Router
- **React 18.2**: UI library with TypeScript
- **TypeScript**: Type-safe JavaScript
- **CSS3**: Custom styling with theme support

### AI/ML Dependencies (Implemented)
- **Ollama** for LLM
- **Diffusers**, **Transformers**, **safetensors**, **accelerate** for Stable Diffusion
- **PyTorch** (with optional CUDA support)
- **DreamShaper 8** safetensors checkpoint

### Technologies NOT Yet Implemented
- ❌ LangChain - Not currently used
- ❌ Coqui TTS - Planned for future
- ❌ OpenAI Whisper - Planned for future
- ❌ IP-Adapter - Planned for future
- ❌ SQLite/Database - Using file-based storage

## Development Environment

### Requirements
- Windows 10/11
- Python 3.8+
- Optional CUDA for GPU acceleration
- 8GB+ RAM (16GB+ recommended)
- Node.js 16+ for frontend

### Local Setup
```bash
# Backend
cd backend && pip install -r requirements.txt
ollama pull llama3.1:8b-instruct-q4_K_M
.\start_backend.bat

# Frontend
cd frontend && npm install && npm run dev
```

## Configuration

### Environment Variables (Improved)
- Ollama Model: `llama3.1:8b-instruct-q4_K_M` (hardcoded in agents)
- SD Checkpoint: `SD_CHECKPOINT_PATH` env var or `backend/pretrained/dreamshaper_8.safetensors`
- Generated Dir: `generated/` (relative to project root)
- Device: Auto-detected (CUDA if available, else CPU)

### Model Configuration
- SD safetensors: Place in `backend/pretrained/` directory
- Ollama model must be pulled locally
- Environment variable `SD_CHECKPOINT_PATH` can override default path

## API Architecture

### Implemented Endpoints
- `POST /api/generate` - Main story generation
  ```json
  {
    "prompt": "A cat who learns to sail",
    "generate_images": true
  }
  ```
- `GET /device` - Hardware info (CUDA/CPU detection)
- `GET /generated/*` - Static file serving for images and stories

### Request/Response
```json
// Response
{
  "status": "Story generated successfully",
  "story": {
    "title": "The Sailing Cat",
    "setting": "A peaceful harbor",
    "characters": ["Mittens the Cat"],
    "scenes": [...]
  }
}
```

## Backend Structure
```
backend/
├── agents/              # All agent implementations
│   ├── prompt_agent.py  # Input validation & enhancement
│   ├── writer_agent.py  # Story generation (Ollama)
│   ├── reviewer_agent.py # Quality assurance
│   ├── editor_agent.py  # Final polish & PDF export
│   ├── image_agent.py   # Image generation (SD)
│   ├── director_agent.py # Pipeline orchestration
│   ├── story_agent.py   # Facade pattern
│   └── evaluation_agent.py # Story evaluation
├── models/
│   └── story_schema.py  # Pydantic models
├── main.py              # FastAPI app
├── main_pipeline.py     # Pipeline helpers
└── requirements.txt     # Dependencies
```

## Frontend Structure (Next.js App Router)
```
frontend/src/
├── app/
│   ├── layout.tsx       # Root layout with ThemeProvider
│   └── page.tsx         # Main page component
├── pages/
│   ├── Home/
│   │   └── LandingPage.tsx  # Landing page
│   └── Story/
│       ├── StoryInput.tsx   # Prompt input
│       └── StoryDisplay.tsx # Story viewer
├── layout/
│   ├── Navigation.tsx   # Top nav with theme toggle
│   └── Footer.tsx       # Footer
├── shared/components/
│   ├── LoadingExperience.tsx # Loading animation
│   ├── ThemeToggle.tsx       # Theme switcher
│   └── ContactSection.tsx    # Contact info
├── contexts/
│   └── ThemeContext.tsx # Theme management
├── next.config.js       # Next.js configuration
└── tsconfig.json       # TypeScript configuration
```

## Data Flow (Current Implementation)
1. User submits prompt via frontend
2. Frontend sends POST to `/api/generate`
3. Backend: Prompt Agent validates/enhances
4. Backend: Writer Agent generates story (Ollama)
5. Backend: Reviewer Agent validates quality
6. Backend: Editor Agent polishes & exports PDF
7. Backend: Image Agent generates scene images (if enabled)
8. Backend: Evaluation Agent runs in background
9. Backend: Returns story JSON with image URLs
10. Frontend: Displays story with page navigation

## Performance Considerations
- Lazy-load heavy models; reuse pipeline instances
- Prefer GPU (half precision) when available
- CPU fallback with adjusted parameters
- Truncate prompts to CLIP-safe length (77 tokens)
- Background evaluation to avoid blocking response

## Security Considerations
- Sanitize input; validate prompt types
- Safe filename generation for all outputs
- CORS: allow all origins (needs tightening for production)
- Local-only processing (no external uploads)

## Known Issues & Limitations
1. ✅ **Model Path Fixed**: Now uses environment variable with fallback to `backend/pretrained/`
2. **No Environment Config**: Should use .env file instead of hardcoding
3. **CORS Too Permissive**: Currently allows all origins
4. **No Retention Policy**: Generated files accumulate indefinitely
5. **Single Mode Only**: No chatbot or advanced interaction modes yet
6. **Basic Character Consistency**: No IP-Adapter, just prompt engineering
7. **No Progress Streaming**: Client waits for complete response

## Deployment
- Health check: `/device` endpoint
- Environment variables: Need to be implemented
- Logging: Console-based, needs structured logging
- Static file serving: Works via `/generated/*` mount
