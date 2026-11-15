# CGMS: Consumer Grievance Management System

CGMS drafts structured consumer grievance letters using Gemini 1.5, generates PDF filings, and tracks complaint status across an interactive dashboard. Built with FastAPI, MongoDB, React, and Tailwind CSS.

## Architecture

- `backend/`: FastAPI REST API with JWT authentication, MongoDB rate limiting, and ReportLab PDF compilation.
- `frontend/`: React SPA built with Vite and Tailwind CSS.

## Requirements

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (optional)
- MongoDB 7.0+
- Google Gemini API key

## Quick Start (Docker)

1. Set up backend configuration:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Set `GEMINI_API_KEY` and `JWT_SECRET_KEY` in `backend/.env`.
3. Launch services:
   ```bash
   docker-compose up --build
   ```
4. Web application runs at `http://localhost:5173`.
5. OpenAPI documentation runs at `http://localhost:8000/docs`.

## Local Development

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# or: source venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -p "*_unit.py"
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Security and Invariants

- CORS origins are sanitized, deduplicated, and stripped of trailing slashes.
- Rate limits are tracked by user ID and UTC date with automated TTL cleanup in MongoDB.
- Input validation sanitizes strings before PDF generation to prevent font rendering exceptions.
