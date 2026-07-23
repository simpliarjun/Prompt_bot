# Consumer Grievance Management System (CGMS)

A full-stack application that leverages the Gemini API to help consumers draft professional, factual, and actionable grievance letters.

## Features

- **AI-Powered Generation:** Converts raw consumer complaints into professional drafts using `gemini-3.5-flash`.
- **Stateless Auth:** Secure JWT-based authentication.
- **Rate Limiting:** Protects the Gemini API with a strict daily generation limit per user (tracked via MongoDB).
- **PDF Export:** Generates professional PDF versions of finalized grievance letters with embedded Unicode fonts.
- **Modern UI:** Built with React, Tailwind CSS v4, and TanStack Query.

## Project Structure

- `backend/`: FastAPI application.
- `frontend/`: React + Vite application.

## Prerequisites

- Docker and Docker Compose
- Node.js (for local frontend development)
- Python 3.11 (for local backend development)
- A Gemini API key (from Google AI Studio)

## Getting Started (Docker Compose)

1. Create a `.env` file in the `backend` directory:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Edit `backend/.env` and insert your actual `GEMINI_API_KEY` and a random string for `JWT_SECRET_KEY`.
3. Start the entire stack:
   ```bash
   docker-compose up --build
   ```
4. Access the frontend at `http://localhost:5173`.
5. Access the backend API docs at `http://localhost:8000/docs`.

## Local Development (Without Docker)

### Backend
1. Ensure a local MongoDB instance is running on `localhost:27017`.
2. `cd backend`
3. Create a virtual environment: `python -m venv venv && source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure `.env` in the backend folder.
6. Run the server: `fastapi dev main.py` or `uvicorn main:app --reload`
7. Run tests: `pytest`

### Frontend
1. `cd frontend`
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`

## Notes on Spec Corrections Applied

- Date conversion boundaries are explicitly handled (MongoDB doesn't store native Python `date` objects).
- ObjectIDs are validated and converted gracefully, preventing 500 errors on bad inputs.
- AI Generation implements a fallback/retry for malformed schema outputs from Gemini.
- A PDF rendering pipeline safely strips control characters and embeds DejaVu Sans fonts.
