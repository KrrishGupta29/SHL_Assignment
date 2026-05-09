# SHL Conversational Assessment Recommendation Agent

## Features
- Clarification of vague hiring requests
- SHL assessment recommendations
- Comparison between assessments
- Refinement handling
- Stateless API design
- Hybrid retrieval system

## API Endpoints
GET /health
POST /chat

## Tech Stack
- FastAPI
- Groq LLM
- Sentence Transformers
- FAISS
- BM25

## Deployment
Hosted on Render

## Run Locally
uvicorn app.main:app --reload
