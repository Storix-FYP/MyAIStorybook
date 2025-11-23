# Active Context: MyAIStorybook (Backend Only)

## Current Work Focus

### Recent Development Status
- **Core Pipeline**: Fully functional multi-agent story generation system (backend operational)
- **FastAPI**: API endpoints stable; static file serving for `generated/*` working
- **Agents**: Prompt, Writer, Image, Reviewer, Editor, Director integrated
- **Images**: Stable Diffusion pipeline operational with hires-fix via img2img
- **Storage**: Outputs organized under `generated/` (images, stories, drafts, prompts, reviews, edits, exports, evaluations)

### Current System State
- **Backend**: Running locally via `backend/start_backend.bat`
- **Models**: Ollama LLM available; DreamShaper 8 safetensors in `backend/pretrained/`
- **Device**: CUDA auto-detected when available, CPU fallback otherwise
- **Config**: Path defaults present; environment variables recommended (see priorities)

## Active Decisions and Considerations

### Technical Decisions Made
1. **Local Models**: Use Ollama locally and Diffusers with local checkpoint
2. **Pipeline Contracts**: Each agent returns `(result, status)` and logs progress
3. **File-based Outputs**: Persist artifacts to `generated/` for inspection and serving
4. **Graceful Degradation**: Text story returns even if images fail
5. **CLIP Safety**: Truncate prompts to 77 tokens prior to SD calls

### Current Limitations
- **Hardcoded Paths**: SD checkpoint path still defaults to repo path
- **Minimal Validation**: Limited input sanitization for edge cases
- **No Cleanup**: Generated files grow without retention policy
- **CPU Performance**: Slow image generation without GPU

## Next Steps and Priorities (Backend)

### Immediate Improvements
1. **Configuration Management**: Read `SD_CHECKPOINT_PATH`, `OLLAMA_MODEL`, `GENERATED_DIR` from env
2. **Error Handling**: Standardize error payloads with `agent`, `stage`, `detail`
3. **Performance**: Reuse pipelines; tune steps/guidance for CPU vs GPU
4. **File Hygiene**: Simple retention policy for `generated/` directories
5. **Validation**: Sanitize and length-limit inputs at API boundary

### Short-term Goals (2-4 weeks)
- Dockerfile and compose for backend-only development
- Basic unit tests for agents (`test_*.py`) and API smoke tests
- Health checks and `/device` diagnostics hardening
- Structured logging (JSON) and timing metrics per agent

### Long-term Vision (2-3 months)
- Config system (env + .env file + pydantic Settings)
- Background queue for long-running image jobs
- Optional cloud export for artifacts
- Model selection strategies and presets

## Active Development Areas

### Backend Development
- **Agent Optimization**: Prompting, guidance, steps tuning
- **API Enhancement**: Better error surfaces and progress reporting
- **Caching Strategy**: Reuse in-memory pipelines; cache story JSONs
- **Static Serving**: Ensure predictable URLs for images/stories

## Current Challenges

### Technical Challenges
- **First Load Latency**: Model cold starts are slow
- **RAM Usage**: Large checkpoints; half precision where possible
- **CPU Fallback**: Acceptable quality with longer runtimes

## Development Environment Status

### Working Components
- ✅ FastAPI backend, endpoints responsive
- ✅ Agents integrated end-to-end
- ✅ Image generation (txt2img + hires img2img)
- ✅ `generated/` outputs and static serving

### Configuration Status
- ⚠️ Paths and models partly hardcoded; env support to add
- ✅ Python deps installed via `backend/requirements.txt`
- ✅ Batch script `start_backend.bat` available

### Known Issues
- ⚠️ SD checkpoint path not env-driven yet
- ⚠️ Limited input validation and error normalization
- ⚠️ No automatic cleanup for `generated/`
