📖 Storybook-FYP

AI-powered storybook generator with FastAPI backend + React frontend.
It generates children’s stories, reviews them, and illustrates scenes with Stable Diffusion.

📂 Project Structure
storybook-fyp/
│── backend/              # FastAPI backend
│   ├── main.py           # FastAPI entrypoint
│   ├── agents/           # AI agents (story, image, review, etc.)
│   ├── models/           # Pydantic schemas
│   └── requirements.txt  # Backend dependencies
│
│── generated/             
│   ├── images/ 
|
│── frontend/             # React frontend
│   ├── public/           # Static assets
│   ├── src/              # React components & logic
│   └── package.json      # Frontend dependencies
│
└── README.md             # Documentation & setup guide

🧑‍💻 Git Workflow (Team Collaboration)

This project is worked on by multiple people. To avoid conflicts, follow this workflow:

1️⃣ Clone the Repository (First Time Only)
git clone https://github.com/<your-org-or-username>/storybook-fyp.git
cd storybook-fyp

2️⃣ Always Create Your Own Branch
git checkout -b <your-branch-name>


👉 Example branch names:

wahab-frontend

mujahid-backend

ahmed-ai-agent

3️⃣ Make Changes & Save Them
git add .
git commit -m "Meaningful message about what you changed"

4️⃣ Push Your Branch to GitHub
git push -u origin <your-branch-name>

5️⃣ Pull Latest Code Before Working (VERY IMPORTANT)
git checkout main
git pull origin main
git checkout <your-branch-name>
git merge main

6️⃣ Creating a Pull Request (PR)

Push your branch to GitHub (git push origin <branch-name>).

Open GitHub → Go to your branch → Click New Pull Request.

Ask your teammates to review.

Once approved, merge into main.

7️⃣ Resolving Merge Conflicts

If GitHub shows a merge conflict:

Open the file with conflicts

Look for <<<<<<<, =======, >>>>>>>

Keep the correct code manually

Save → Commit → Push again

✅ Golden Rule:

Never push directly to main.

Always use branches + PRs.

🚀 Backend Setup (FastAPI)
Create & activate virtual environment
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac

Install dependencies
pip install -r requirements.txt

Run FastAPI backend
uvicorn main:app --reload


Backend runs at: http://127.0.0.1:8000

🎨 Frontend Setup (React)
Install dependencies
cd frontend
npm install

Run frontend
npm start


Frontend runs at: http://localhost:3000

⚠️ If React is not installed globally:

npm install -g create-react-app

🤖 AI Model Setup
Using Pre-downloaded .safetensors Model

Place your model here:

backend/models/pretrained/realismByStableYogi_sd15V9.safetensors


Update image_agent.py:

self.pipe = StableDiffusionPipeline.from_single_file(
    "backend/models/pretrained/realismByStableYogi_sd15V9.safetensors",
    torch_dtype=dtype,
    safety_checker=None
)

🦙 Ollama Setup (Optional LLM Testing)
Install Ollama

Download & install from: https://ollama.com/download

Pull Dolphin 8B model
ollama pull dolphin:8b

Test on CMD
ollama run dolphin:8b "Tell me a short story about a robot and a dog"

⚠️ Common Issues

Branch conflicts → Always git pull origin main before pushing.

React not found → Run npm install -g create-react-app.

CUDA errors → Ensure PyTorch matches your CUDA version.

Model not loading → Check .safetensors is in backend/models/pretrained/.

📌 Git Cheatsheet (Quick Reference)
# Clone repo (first time only)
git clone https://github.com/<your-org-or-username>/storybook-fyp.git
cd storybook-fyp

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
