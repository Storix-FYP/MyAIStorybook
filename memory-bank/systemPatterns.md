# System Patterns: MyAIStorybook (Current Implementation - Iteration 1)

## Architecture Overview

### Multi-Agent Pipeline (Backend)
```
User Input → PromptAgent → WriterAgent → ReviewerAgent → EditorAgent → Final Story
                                ↓
                          ImageAgent (optional) → Images
                                ↓
                          EvaluationAgent (background)
```
- `DirectorAgent` orchestrates sequencing and status tracking
- `StoryAgent` acts as a facade for pipeline invocation

## Key Backend Design Patterns

### 1) Facade Pattern
- `StoryAgent` provides a single entry point for story generation
- Delegates to `DirectorAgent` which manages the multi-agent workflow
- Simplifies external interface while maintaining internal complexity

### 2) Pipeline Pattern
- Each agent performs a specialized step and returns `(result, status)`
- Director coordinates flow and aggregates progress
- Sequential processing: Prompt → Writer → Reviewer → Editor
- Images generated separately after story completion

### 3) Hardcoded Configuration (Current - Needs Improvement)
- Model paths hardcoded in agent files
- No environment variable support yet
- Device selection auto-detected at runtime

### 4) Observer Pattern (Partial Implementation)
- Status logs emitted per agent (✅, ❌, ⚠️)
- Console-based logging only (no structured logging yet)
- Stages: prompt→writer→review→edit→image

## Data Flow (Backend)

### Input Processing
```
Raw Input → Sanitization → Enhancement (PromptAgent) → Classified Prompt
```

### Story Generation
```
Enhanced Prompt → Structure + Scenes (WriterAgent using Ollama)
```

### Image Generation
```
Scene Description → Truncate to 77 tokens → SD txt2img → img2img hires fix → PNG under generated/images
```

### Quality & Edit
```
Story → ReviewerAgent → EditorAgent → Final Story JSON + PDF under generated/
```

### Background Evaluation
```
Final Story → EvaluationAgent (subprocess) → Metrics saved to generated/evaluations
```

## Error Handling Patterns
- Graceful degradation: deliver text story if images fail
- Retry logic: WriterAgent retries up to 2 times on JSON parse errors
- Safe defaults: CPU fallback when CUDA unavailable
- Input validation: sanitize prompt; enforce reasonability
- Truncation: Auto-truncate long image prompts to 77 tokens

## Performance Patterns
- Lazy model loading (models loaded on first use)
- Pipeline reuse within DirectorAgent
- GPU-first with half precision (float16) where possible
- CPU mode: reduced steps for acceptable latency
- CLIP-safe prompt trimming (≤ 77 tokens)
- Two-pass image generation for quality

## File I/O & Paths
- Safe filename generation for all artifacts
- Directory layout under `generated/`:
  ```
  generated/
  ├── images/        # Generated scene illustrations
  ├── stories/       # Final story JSON files
  ├── drafts/        # Writer agent outputs
  ├── prompts/       # Enhanced prompts
  ├── reviews/       # Reviewer feedback
  ├── edits/         # Editor outputs
  ├── exports/       # PDF files
  └── evaluations/   # Story quality metrics
  ```
- No retention policy (files accumulate)

## Frontend Patterns

### Component Structure
- **Container Pattern**: App.tsx manages global state
- **Presentational Components**: Separate display from logic
- **Context API**: ThemeContext for theme management
- **Controlled Components**: Form inputs managed by React state

### State Management
- Local state with useState hooks
- Theme state in Context API
- No Redux or complex state management (simple app)

### Data Flow (Frontend)
```
User Input → StoryInput.tsx → POST /api/generate → Backend
Backend Response → App.tsx state → StoryDisplay.tsx → Rendered pages
```

## Testing Patterns
- Agent unit tests in `backend/agents/test_*.py`
- Manual testing for primary flows
- No automated API tests yet
- No frontend tests yet

## Security Patterns
- No external uploads of user content
- CORS currently allows all origins (needs tightening)
- Input sanitization for filenames
- No user authentication (local-only app)

## Current Limitations & Technical Debt

### Configuration Management
- Hardcoded model paths need environment variables
- No centralized config file
- Each user must manually update image_agent.py with their SD path

### Observability
- Console logging only
- No structured logs
- No timing metrics
- No error aggregation

### Scalability
- Single-user, synchronous processing
- No request queuing
- No concurrent session support
- Long-running image generation blocks response

### State Management
- File-based storage only
- No database
- No transaction support
- Manual file cleanup required

### Error Handling
- Basic try-catch only
- No comprehensive error taxonomy
- No retry mechanisms for network calls
- Limited validation

## Design Decisions & Rationale

### Why Facade + Director?
- **StoryAgent** maintained for backward compatibility
- **DirectorAgent** provides actual orchestration
- Allows future refactoring without breaking existing code

### Why File-Based Storage?
- Simplicity for first iteration
- No database setup required
- Human-readable JSON for debugging
- Easy to migrate to DB later

### Why Local Models?
- Privacy-first approach
- No API costs
- Offline operation
- Full control over processing

### Why Multi-Pass Image Generation?
- txt2img creates base image
- img2img refines for higher quality
- Better results than single-pass generation

### Why Background Evaluation?
- Non-blocking API response
- User gets story immediately
- Evaluation happens asynchronously
- Metrics for future analysis
