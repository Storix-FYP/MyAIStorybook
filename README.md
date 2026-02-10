# 📖 MyAIStorybook

**AI-powered children's storybook generator** with personalized character images using facial recognition.  
Built with **FastAPI backend** + **Next.js frontend** + **Stable Diffusion WebUI** for professional-quality illustrations.

---

## ✨ Key Features

- 🎨 **Personalized Stories** - Upload your photo and become the story's main character
- 🤖 **AI Story Generation** - Powered by Ollama (Llama 3.1)
- 🖼️ **Professional Image Generation** - Uses Stable Diffusion WebUI with IP-Adapter FaceID Plus v2
- 🛡️ **Child-Safe Content** - Automatic content filtering for age-appropriate stories and images
- 📱 **Modern UI** - Responsive Next.js frontend with dark mode
- 🔐 **User Authentication** - Secure login and story management
- 💬 **Interactive Chatbot** - Chat with story characters
- 🎭 **Idea Workshop** - Brainstorm story ideas with AI assistance

---

## 📂 Project Structure

```
MyAIStorybook/
├── backend/                    # FastAPI backend
│   ├── main.py                # API entrypoint
│   ├── agents/                # AI agents
│   │   ├── writer_agent.py   # Story generation
│   │   ├── image_agent.py    # Standard image generation
│   │   ├── personalized_image_agent_webui_api.py  # Personalized images
│   │   ├── chatbot_agent.py  # Character chatbot
│   │   └── idea_workshop_agent.py  # Story ideation
│   ├── utils/                 # Utilities
│   │   ├── content_safety.py # Child-safe content filtering
│   │   └── ollama_manager.py # GPU memory management
│   ├── auth/                  # Authentication system
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/              # Next.js 14 app directory
│   │   ├── components/       # React components
│   │   └── contexts/         # React contexts
│   └── package.json          # Node dependencies
│
├── generated/                  # Generated content
│   ├── images/               # Story illustrations
│   ├── stories/              # Story JSON files
│   └── pdfs/                 # Exported PDFs
│
├── start_all.bat              # Start all services
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.10+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **CUDA-capable GPU** - NVIDIA GPU with 8GB+ VRAM recommended
4. **Ollama** - [Download](https://ollama.com/)
5. **Stable Diffusion WebUI** - Already included in project
6. **FFmpeg** - Required for Speech-to-Text functionality
   - Windows: `winget install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`


### Installation

1. **Clone the repository**
```bash
git clone https://github.com/glassesart14-alt/MyAIStorybook.git
cd MyAIStorybook
```

2. **Install Ollama model**
```bash
ollama pull llama3.1:8b-instruct-q8_0
```

3. **Download TTS voice models**
```bash
cd backend
download_tts_models.bat
```

4. **Start everything** (Recommended)
```bash
start_all.bat
```

This will:
- Start Stable Diffusion WebUI (port 7860)
- Start Backend API (port 8000)
- Start Frontend (port 3000)

**Access the app at:** http://localhost:3000

---

## 🎯 Running Individual Services

### Backend Only
```bash
cd backend
start_backend.bat
```
Backend runs at: http://127.0.0.1:8000  
API docs at: http://127.0.0.1:8000/docs

### Frontend Only
```bash
cd frontend
start_frontend.bat
```
Frontend runs at: http://localhost:3000

### WebUI Only
```bash
cd C:\Users\wahab\Downloads\FYP\storybook-fyp\stable-diffusion-webui
webui-user.bat
```
WebUI runs at: http://127.0.0.1:7860

---

## 🤖 AI Models Setup

### Stable Diffusion Model

**Model:** Realistic Vision V4.0  
**Location:** `stable-diffusion-webui/models/Stable-diffusion/`

Download from: [Civitai - Realistic Vision](https://civitai.com/models/4201/realistic-vision-v40)

### IP-Adapter Models

**Required files in WebUI:**
- `stable-diffusion-webui/extensions/sd-webui-controlnet/models/ip-adapter-faceid-plusv2_sd15.bin`
- `stable-diffusion-webui/models/Lora/ip-adapter-faceid-plusv2_sd15_lora.safetensors`

Download from: [IP-Adapter FaceID Plus v2](https://huggingface.co/h94/IP-Adapter-FaceID)

### Ollama Setup

1. **Install Ollama:** [Download here](https://ollama.com/)
2. **Pull the model:**
```bash
ollama pull llama3.1:8b-instruct-q8_0
```

3. **Test it:**
```bash
ollama run llama3.1:8b-instruct-q8_0 "Tell me a short story"
```

---

## 🛠️ Configuration

### Environment Variables

Create `backend/.env`:
```env
DATABASE_URL=postgresql://user:password@localhost/storybook
OLLAMA_MODEL=llama3.1:8b-instruct-q8_0
WEBUI_URL=http://127.0.0.1:7860
```

### WebUI Settings

Edit `stable-diffusion-webui/webui-user.bat`:
```batch
set COMMANDLINE_ARGS=--api --nowebui --skip-torch-cuda-test
```

---

## 🎨 Features in Detail

### 1. Personalized Image Generation
- Upload your photo
- AI detects your face using InsightFace
- Generates story scenes with your face
- Uses IP-Adapter FaceID Plus v2 for accurate facial likeness

### 2. Content Safety
- Automatic filtering of inappropriate prompts
- Child-safe negative prompts
- Blocks violence, explicit content, deformities
- Age-appropriate story themes

### 3. GPU Memory Management
- Automatically pauses Ollama during image generation
- Clears GPU cache for optimal performance
- Resumes Ollama after images are generated
- 5-10x faster image generation

### 4. Story Pipeline
```
User Input → Prompt Agent → Writer Agent → Reviewer Agent → 
Editor Agent → Image Generation → PDF Export
```



## 🐛 Troubleshooting

### WebUI not starting
- Check if port 7860 is available
- Ensure CUDA is installed correctly
- Run `webui-user.bat` manually to see errors

### Backend errors
- Verify virtual environment is activated
- Check `backend/requirements.txt` is installed
- Ensure Ollama is running

### Frontend issues
- Run `npm install` in frontend folder
- Clear Next.js cache: `rm -rf .next`
- Check Node.js version: `node --version`

### Image generation slow
- Ensure Ollama is being paused (check backend console)
- Verify GPU is being used (check Task Manager)
- Close other GPU-intensive applications

### Poor facial likeness
- Use a clear, front-facing photo
- Ensure face is well-lit
- Photo should be 512x512 or larger
- Only one face should be visible

---

## 🧑‍💻 Git Workflow

### Create a Branch
```bash
git checkout -b feature/my-feature
```

### Make Changes
```bash
git add .
git commit -m "Add new feature"
git push origin feature/my-feature
```

### Update from Main
```bash
git checkout main
git pull origin main
git checkout feature/my-feature
git merge main
```
