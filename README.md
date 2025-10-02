# 📖 Storybook-FYP

**AI-powered storybook generator** with a **FastAPI backend** + **React frontend**.  
It generates children’s stories, reviews them, and illustrates scenes using **Stable Diffusion**.

---

## 📂 Project Structure

storybook-fyp/
│── backend/ # FastAPI backend
│ ├── main.py # FastAPI entrypoint
│ ├── agents/ # AI agents (story, image, review, etc.)
│ ├── models/ # Pydantic schemas
│ └── requirements.txt # Backend dependencies
│
│── generated/
│ ├── images/ # Generated images
│
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
git clone https://github.com/<username>/storybook-fyp.git
cd storybook-fyp

2️⃣ Always Create Your Own Branch
git checkout -b my-branch-name

👉 Example branch names:

wahab-frontend
mujahid-backend
ahmed-ai-agent

