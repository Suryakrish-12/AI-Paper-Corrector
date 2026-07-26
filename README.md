# SmartEval AI

**Intelligent Examination Paper Evaluation and Learning Analytics System**

SmartEval AI is a production-ready, AI-powered web application that automates the evaluation of descriptive exam answer scripts. Using OCR layout parsing, Sentence Transformers embeddings, and Large Language Model (LLM) grading engines, the system provides transparent, explainable scoring criteria along with detailed individual and institutional learning analytics.

---

## Technical Stack

* **Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Recharts, Zustand, Axios
* **Backend**: FastAPI, Python 3.12, SQLAlchemy, Uvicorn, PostgreSQL, Redis, Celery, WebSockets
* **AI Pipelines**: EasyOCR/PaddleOCR, Sentence Transformers (`all-MiniLM-L6-v2`), OpenAI API (with a robust rule-based local mock fallback model)

---

## Project Structure

```
smarteval-ai/
├── docker-compose.yml           # Multi-container orchestration
├── README.md                    # System documentation
├── .env.example                 # Environment templates
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                  # FastAPI mount & WebSockets endpoint
│   ├── seed.py                  # Database master data seeding script
│   └── app/
│       ├── config.py            # Configuration bindings
│       ├── database.py          # Session engines (Postgres & SQLite fallbacks)
│       ├── models.py            # Normalized database schema
│       ├── schemas.py           # Pydantic validation entities
│       ├── auth.py              # JWT authentication & RBAC check dependencies
│       ├── websocket.py         # Push connection manager
│       ├── celery_app.py        # Task runner configs
│       ├── tasks.py             # Evaluation pipeline orchestrator
│       ├── ai/                  # OCR, NLP & LLM pipelines
│       │   ├── ocr_pipeline.py
│       │   ├── nlp_engine.py
│       │   ├── llm_evaluator.py
│       │   └── explainable_ai.py
│       └── utils/               # File unzippers & Excel/PDF report generators
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── app/                 # Next.js App Router folders
        ├── components/          # Shared components
        ├── store/               # Zustand auth & evaluation states
        └── lib/                 # Axios clients
```

---

## Quick Start (Local Setup)

The backend features a **zero-configuration SQLite fallback** and **Mock AI mode** enabled by default. This allows you to run the entire system locally without needing local database servers or OpenAI API credentials.

### 1. Run the Backend

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment variables:
   ```bash
   cp ../.env.example .env
   ```
5. Seed the database with demo users and departments:
   ```bash
   python seed.py
   ```
6. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

The Swagger docs will be available at `http://localhost:8000/docs`.

### 2. Run the Frontend

1. Navigate to the frontend folder:
   ```bash
   cd ../frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

Open your browser to `http://localhost:3000`.

---

## Seed Accounts for Demo Logins

The database seeder creates standard accounts (default password is `password123` for all):

| Role | Email | Password | Purpose |
| --- | --- | --- | --- |
| **Institution Admin** | `admin@smarteval.ai` | `password123` | Inspects accuracy logs, audits, and department lists |
| **Faculty / Evaluator** | `faculty@smarteval.ai` | `password123` | Creates rubrics, uploads scripts, and overrides grades |
| **Student (Excellent)** | `student1@smarteval.ai` | `password123` | View graded cards, AI descriptions, and strengths radar |
| **Student (Average)** | `student2@smarteval.ai` | `password123` | Compares scores against class medians and reviews recommendations |

---

## Deployment (Docker Compose)

To spin up the complete, production-ready system with PostgreSQL, Redis, Celery, FastAPI, and Next.js containers:

1. Configure the `.env` parameters.
2. In the root workspace directory, run:
   ```bash
   docker-compose up --build
   ```

This spins up the database, cache brokers, backend microservice, background task workers, and compiled Next.js bundle automatically.
