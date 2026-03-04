# DockRadius

> Docker Blast Radius Analyzer — Visualize infrastructure impact and risk analysis for Docker commands.

DockRadius parses Docker CLI commands, generates deterministic infrastructure diagrams, and provides AI-powered risk analysis using Groq's Llama 3.3 70B.

## Architecture

```
┌──────────────────┐      POST /analyze      ┌──────────────────────────────┐
│   Next.js UI     │ ───────────────────────► │   FastAPI Backend            │
│   (port 3000)    │ ◄─────────────────────── │   (port 8000)               │
│                  │                          │                              │
│  - Command Input │   { mermaid, analysis }  │  Pipeline:                   │
│  - Mermaid Viewer│                          │  1. Parser (shlex)           │
│  - Analysis Panel│                          │  2. Graph Builder            │
└──────────────────┘                          │  3. Mermaid Generator        │
                                              │  4. LLM Analysis (Groq)     │
                                              └──────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Groq API Key (optional — fallback analysis works without it)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env and add your Groq API key
# GROQ_API_KEY=gsk_your_key_here

# Start server
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 3. Use the App

1. Open **http://localhost:3000**
2. Enter a Docker command (e.g. `docker run -p 80:80 nginx`)
3. Click **Analyze Command**
4. View the infrastructure diagram and AI-powered risk analysis

## Supported Commands

| Command | Description |
|---------|-------------|
| `docker run` | Run a container with ports, volumes, networks |
| `docker build` | Build an image from a Dockerfile |
| `docker exec` | Execute a command in a running container |
| `docker stop` | Stop a running container |
| `docker rm` | Remove a container |
| `docker network create` | Create a Docker network |
| `docker volume create` | Create a Docker volume |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | No | — | Groq API key for LLM analysis (fallback mode without it) |

## Example Flow

**Input:**
```
docker run -d --name webserver -p 80:80 -p 443:443 -v ./html:/usr/share/nginx/html nginx:latest
```

**Output:**
- Mermaid infrastructure diagram showing host → container → ports → volumes
- AI analysis with risk level, infrastructure impact, and blast radius

## Security

- ⚡ **No command execution** — static parsing only
- 🔒 **Input validation** — via Pydantic schemas
- 🛡️ **LLM output sanitization** — validated with Pydantic models
- 🚫 **No shell access** — uses `shlex.split()` for safe tokenization

## Tech Stack

- **Frontend:** Next.js 16, TypeScript, Tailwind CSS 4, Mermaid.js
- **Backend:** FastAPI, Python 3.11+, Pydantic, Groq SDK
- **AI:** Llama 3.3 70B via Groq API
