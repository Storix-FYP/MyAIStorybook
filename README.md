# 📖 Storybook-FYP

**AI-powered storybook generator** with a **FastAPI backend** + **React frontend**.  
It generates children’s stories, reviews them, and illustrates scenes using **Stable Diffusion**.

---

## 📂 Project Structure

storybook-fyp/

│── backend/ # FastAPI backend

│     ├── main.py # FastAPI entrypoint

│     ├── agents/ # AI agents (story, image, review, etc.)
  
│     ├── models/ # Pydantic schemas
   
│     └── requirements.txt # Backend dependencies

│

│── generated/

│ ├── images/ # Generated images

│ ├── stories/ # Generated stories

|

│── frontend/ # React frontend

│ ├── public/ # Static assets

│ ├── src/ # React components & logic

│ └── package.json # Frontend dependencies

│

└── README.md # Documentation & setup guide



---

## 🧑‍💻 Git Workflow (Team Collaboration)

This project is worked on by multiple contributors. To avoid conflicts, **follow this workflow**:

### 1️⃣ Clone the Repository (First Time Only)
```bash
git clone https://github.com/glassesart14-alt/MyAIStorybook.git
cd MyAIStorybook
```

### 2️⃣ Always Create Your Own Branch
```bash
git checkout -b my-branch-name
```
👉 Example branch names:

* wahab-frontend
* mujahid-backend
* ahmed-ai-agent

### 3️⃣ Make Changes & Commit
```bash
git add .
git commit -m "Meaningful message about what you changed"
```

### 4️⃣ Push Your Branch to GitHub
```bash
git push -u origin my-branch-name
```

### 5️⃣ Pull Latest Code Before Working (VERY IMPORTANT)
```bash
git checkout main
git pull origin main
git checkout my-branch-name
git merge main
```

### 6️⃣ Creating a Pull Request (PR)
1. Push your branch:
```bash
git push origin my-branch-name
```

2. Go to GitHub → Your branch → New Pull Request
3. Ask teammates for review
4. Once approved, merge into main

✅ Golden Rule:
* Never push directly to main
* Always use branches + PRs

## To run the Whole project:

Open terminal as Administrator and run:
```bash
.\start_all.bat
```
This automaticaly installs all necessary packages.

## 🚀 Run Backend Only (FastAPI)

Open terminal as Administrator and run:
```bash
cd backend
.\start_backend.bat
```
This automatically installs requirements.txt in a virtual environment (venv).

👉 Backend runs at: http://127.0.0.1:8000

## 🎨 Run Frontend Only (React)

Open terminal as Administrator and run:
```bash
cd frontend
.\start_frontend.bat
```
This automaticaly installs the necessary packages.

👉 Frontend runs at: http://localhost:3000

## 🤖 AI Model Setup

Model Link: https://civitai.com/models/4384/dreamshaper

Using a pre-downloaded **.safetensors** model:

Place your model here:
```bash
backend/models/pretrained/dreamshaper_8.safetensors
```

Update **image_agent.py**:
```bash
self.pipe = StableDiffusionPipeline.from_single_file(
    "backend/models/pretrained/dreamshaper_8.safetensors",
    torch_dtype=dtype,
    safety_checker=None
)
```

## 🦙 Ollama Setup 
1. Install Ollama → Download here
2. Pull llama3.1:8b model:
```bash
ollama pull llama3.1:8b-instruct-q4_K_M 
```

Test on CMD:
```bash
ollama run llama3.1:8b-instruct-q4_K_M  "Tell me a short story about a robot and a dog"
```

## ⚠️ Common Issues

* Branch conflicts → Always git pull origin main before pushing.
* React not found → Run npm install -g create-react-app.
* CUDA errors → Ensure PyTorch matches your CUDA version.
* Model not loading → Check .safetensors file is in backend/models/pretrained/.

## 📌 Git Cheatsheet (Quick Reference)
```bash
# Clone repo (first time only)
git clone https://github.com/glassesart14-alt/MyAIStorybook.git
cd MyAIStorybook

# Create new branch
git checkout -b my-feature

# Stage and commit changes
git add .
git commit -m "Added new feature"

# Push your branch
git push -u origin my-feature

# Switch to main & update
git checkout main
git pull origin main

# Merge latest main into your branch
git checkout my-feature
git merge main

# Push after merge
git push origin my-feature
```











