# Study Assistant - Multimodal Biology RAG

Study Assistant is a full-stack multimodal RAG application for biology learning. Students can ask biology questions, upload an image such as a textbook diagram, and receive a grounded answer using retrieved textbook context. If the textbook retrieval is weak, the backend can fall back to curated web search results.

The project is split into a Next.js frontend and a FastAPI backend powered by LangGraph, LangChain, Google Generative AI, Supabase Storage, Supabase Postgres/PGVector, and Tavily.

## Output Example

Add the application output screenshot here after saving it in the repository, for example at `docs/images/output-example.png`.

<img width="1913" height="958" alt="Screenshot 2026-06-20 195913" src="https://github.com/user-attachments/assets/5c374b92-77e2-4883-aae7-97f72acc3dbc" />

FOR TESTING U CAN USE IMAGE OR ALREADY EXTRACTED IMAGES FROM HERE - https://drive.google.com/drive/folders/1fmK0ze2HkNwiixYtCB2yKSdZP6flIcSd?usp=sharing

DATABASE VIEW containing 2000 chunks taken from a 1000 page biology book: -

<img width="1608" height="828" alt="image" src="https://github.com/user-attachments/assets/9e11a166-27f2-48fa-ae5e-7045a23d3623" />

biology book link - https://www.kaggle.com/datasets/rohanthoma/ebook-pdfs

## Features

- Chat interface for student questions.
- Image upload support through Supabase Storage.
- Multimodal image understanding for diagrams, labels, textbook screenshots, and biological objects.
- Biology-only query guard to block unrelated or unsafe questions.
- Query rewriting for better vector retrieval.
- Textbook retrieval from Supabase PGVector.
- Similarity score checking to decide whether textbook context is strong enough.
- Tavily-powered web fallback for biology questions when local textbook retrieval is insufficient.
- Retrieved context sidebar so users can inspect the sources used to answer.
- FastAPI health endpoint for deployment checks.

## Tech Stack

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Axios
- Supabase JS client

### Backend

- FastAPI
- LangGraph
- LangChain
- Google Generative AI chat and embedding models
- Supabase Postgres with PGVector
- Tavily Search API
- Pydantic
- HTTPX

## Repository Structure

```text
assignment-rag/
+-- Readme.md
+-- backend/
|   +-- main.py                  # Vercel/FastAPI entrypoint
|   +-- requirements.txt         # Python runtime dependencies
|   +-- vercel.json              # Backend Vercel config
|   +-- server/
|   |   +-- main.py              # FastAPI app and API routes
|   +-- agent/
|   |   +-- graph.py             # LangGraph workflow
|   |   +-- state.py             # Agent state schema
|   |   +-- prompt.py            # Prompt-related code
|   |   +-- tool/
|   |   |   +-- tavily_search.py # Web search fallback
|   |   +-- utils/
|   |       +-- extract_text.py  # Model response text extraction
|   |       +-- image_loader.py  # Image download and validation
|   +-- db/
|   |   +-- db.py                # PGVector connection
|   |   +-- storage.py           # Supabase storage client
|   +-- model/
|   |   +-- embedding_model.py   # Google embedding model
|   |   +-- query_model.py       # Google chat model
|   +-- parser/
|       +-- parser.py            # Document parsing script
|       +-- clean.py             # Markdown cleanup script
|       +-- chunking.py          # Chunking and vector ingestion script
+-- frontend/
    +-- app/
    |   +-- page.tsx             # Main chat UI
    |   +-- layout.tsx
    |   +-- globals.css
    +-- utils/
    |   +-- supabase.js          # Supabase browser client
    |   +-- uploadImage.js       # Image upload helper
    +-- package.json
```

## How It Works

1. The user enters a question and optionally uploads an image.
2. The frontend uploads the image to Supabase Storage and sends the public image URL to the backend.
3. FastAPI receives the request at `POST /chat`.
4. LangGraph runs the agent workflow:
   - Analyze image if an image URL is provided.
   - Gate the request to ensure it is biology-related and safe.
   - Build a retrieval-friendly search query.
   - Retrieve textbook chunks from Supabase PGVector.
   - Check similarity scores.
   - Use Tavily web search if the textbook context is weak or missing.
   - Generate a final answer using the retrieved context.
5. The frontend displays the answer and shows retrieved context cards in the sidebar.

## Agent Workflow

The LangGraph workflow is defined in `backend/agent/graph.py`.

```text
analyze_image
    |
    v
gate
    +-- blocked -> END
    |
    v
build_query
    |
    v
retrieve
    +-- web_fallback
    |
    v
answer
    |
    v
END
```

### Main Nodes

- `analyze_image_node`: Downloads and analyzes an uploaded image using a multimodal model.
- `gate_node`: Blocks unrelated, unsafe, or prompt-injection style requests.
- `build_query_node`: Converts the user question and image summary into a strong retrieval query.
- `retrieve_node`: Retrieves relevant textbook chunks from PGVector.
- `web_fallback_node`: Searches trusted biology sources using Tavily if local context is weak.
- `answer_node`: Produces the final student-friendly response.

## Backend API

### `GET /`

Basic server check.

Response:

```json
{
  "status": "ok",
  "message": "Backend server is running"
}
```

### `GET /health`

Health check route for deployment platforms.

Response:

```json
{
  "status": "healthy"
}
```

### `POST /chat`

Runs the RAG workflow.

Request body:

```json
{
  "message": "Explain prokaryotic cells",
  "session_id": "optional-session-id",
  "image_url": "https://example.com/image.png",
  "image_path": null
}
```

Response body:

```json
{
  "answer": "Generated answer",
  "used_web_fallback": false,
  "retrieved_context": "Retrieved textbook chunks",
  "web_search_results": null
}
```

## Environment Variables

Do not commit real secrets. Use `.env` files locally and platform environment variables in production.

### Backend `.env`

Create `backend/.env`:

```env
GOOGLE_API_KEY=""
SUPABASE_DATABASE_URL=""
SUPABASE_URL=""
SUPABASE_SERVICE_ROLE_KEY=""
SUPABASE_BUCKET=""
COLLECTION_NAME="documents"
TAVILY_API_KEY=""
```

Backend variable notes:

- `GOOGLE_API_KEY`: Used for chat completion and embeddings.
- `SUPABASE_DATABASE_URL`: Postgres connection string for Supabase PGVector.
- `SUPABASE_URL`: Supabase project URL.
- `SUPABASE_SERVICE_ROLE_KEY`: Server-side key for privileged Supabase access.
- `SUPABASE_BUCKET`: Storage bucket name.
- `COLLECTION_NAME`: Vector collection name. The current backend uses `documents`.
- `TAVILY_API_KEY`: Used for web fallback search.

### Frontend `.env.local`

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=""
NEXT_PUBLIC_SUPABASE_ANON_KEY=""
NEXT_PUBLIC_SUPABASE_BUCKET=""
NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"
```

Frontend variable notes:

- `NEXT_PUBLIC_SUPABASE_URL`: Public Supabase project URL.
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase browser anon key.
- `NEXT_PUBLIC_SUPABASE_BUCKET`: Bucket used for image uploads.
- `NEXT_PUBLIC_BACKEND_URL`: FastAPI backend URL.

## Local Development

### Prerequisites

- Node.js 20 or newer
- Python 3.11 or compatible Python 3 version
- Supabase project with Postgres and Storage enabled
- PGVector support in Supabase
- Google API key for Generative AI
- Tavily API key if web fallback is required

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd assignment-rag
```

### 2. Start the Backend

```bash
cd backend
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

On macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Verify:

```text
http://localhost:8000/health
```

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## Supabase Setup

### Storage

Create a Supabase Storage bucket for image uploads. The frontend expects the bucket name in:

```env
NEXT_PUBLIC_SUPABASE_BUCKET=""
```

If images are sent to the backend by public URL, the uploaded files must be publicly readable or accessible through a signed URL.

### Database and Vector Store

The backend uses `langchain-postgres` with PGVector. The vector store is initialized in `backend/db/db.py` with:

```python
collection_name="documents"
```

Make sure your Supabase Postgres connection string is set in:

```env
SUPABASE_DATABASE_URL=""
```

## Document Ingestion Pipeline

The parser scripts are for preparing textbook content and storing embeddings.

Typical flow:

1. Parse the textbook into markdown.
2. Clean markdown.
3. Split markdown into chunks.
4. Generate embeddings.
5. Store chunks in Supabase PGVector.

Relevant files:

- `backend/parser/parser.py`: Converts source document content into markdown.
- `backend/parser/clean.py`: Removes unwanted image markers, HTML tables, markdown tables, and extra spacing.
- `backend/parser/chunking.py`: Splits cleaned markdown by headers and character windows, then stores chunks in PGVector.

Current chunking settings:

```python
chunk_size=1200
chunk_overlap=200
```

The ingestion script currently points to:

```text
backend/data/parsed/markdown/ConceptsofBiology-cleaned.md
```

Before running ingestion, make sure the expected data files exist locally and the backend environment variables are configured.

Run from the `backend` directory:

```bash
python parser/chunking.py
```

## Deployment

### Frontend on Vercel

Create a Vercel project with:

```text
Root Directory: frontend
Framework: Next.js
Build Command: npm run build
```

Set frontend environment variables:

```env
NEXT_PUBLIC_SUPABASE_URL=""
NEXT_PUBLIC_SUPABASE_ANON_KEY=""
NEXT_PUBLIC_SUPABASE_BUCKET=""
NEXT_PUBLIC_BACKEND_URL="https://your-backend-url"
```

### Backend on Vercel

Create another Vercel project with:

```text
Root Directory: backend
Framework: FastAPI / Python
Install Command: pip install -r requirements.txt
Build Command: empty
```

The backend entrypoint is:

```python
from server.main import app
```

in:

```text
backend/main.py
```

Set backend environment variables:

```env
GOOGLE_API_KEY=""
SUPABASE_DATABASE_URL=""
SUPABASE_URL=""
SUPABASE_SERVICE_ROLE_KEY=""
SUPABASE_BUCKET=""
COLLECTION_NAME="documents"
TAVILY_API_KEY=""
```

### Backend Deployment Warning

The backend uses AI, vector database, and document tooling dependencies. If Vercel reports a bundle or ephemeral storage limit error, deploy the backend to a Python-friendly server platform such as Render, Railway, Fly.io, or a VPS, then keep the frontend on Vercel.

In that setup:

```env
NEXT_PUBLIC_BACKEND_URL="https://your-render-or-railway-backend-url"
```

## CORS

The backend currently allows all origins:

```python
allow_origins=["*"]
```

For production, replace it with your frontend URL:

```python
allow_origins=["https://your-frontend.vercel.app"]
```

## Common Problems and Fixes

### Vercel cannot detect FastAPI

Make sure `backend/main.py` exists and exports the FastAPI app:

```python
from server.main import app
```

Also make sure the Vercel root directory is set to:

```text
backend
```

### `could not import "main.py"`

This usually means an import failed during startup. Check Vercel logs for the full stack trace. Common causes:

- Missing environment variables.
- Importing a package that is not in `requirements.txt`.
- Initializing database/API clients at import time.
- Commenting out a function but still importing it elsewhere.

### Bundle size exceeds Vercel limit

Remove offline-only dependencies from `requirements.txt`, especially document parsing or ML model packages that are not needed at request time. If the backend is still too large, host it outside Vercel.

### `/health` works but `/chat` fails

The app is deployed, but the RAG pipeline is failing. Check:

- `GOOGLE_API_KEY`
- `SUPABASE_DATABASE_URL`
- PGVector collection/table setup
- Tavily key if fallback search is triggered
- Whether your Supabase database allows external connections

### Image upload works but image analysis fails

Check:

- Supabase bucket permissions
- Public URL or signed URL accessibility
- Image MIME type must be one of `image/jpeg`, `image/png`, or `image/webp`
- Image size must be under 5 MB

## Useful Commands

Run backend locally:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Run frontend locally:

```bash
cd frontend
npm run dev
```

Test backend import:

```bash
cd backend
python -c "from main import app; print(app.title)"
```

Test backend health:

```bash
curl http://localhost:8000/health
```

Build frontend:

```bash
cd frontend
npm run build
```

## Security Notes

- Never commit `.env` files with real secrets.
- Keep `SUPABASE_SERVICE_ROLE_KEY` only on the backend.
- Only expose `NEXT_PUBLIC_*` variables to the frontend.
- Restrict CORS before production use.
- Use Supabase Row Level Security and Storage policies carefully.
- Validate user-uploaded files before processing them.

## Roadmap Ideas

- Add authentication and per-user chat history.
- Store conversation sessions in Supabase.
- Add streaming responses.
- Add citations with exact source metadata.
- Improve markdown rendering in bot answers.
- Add admin ingestion UI for uploading new textbooks.
- Add automated tests for `/health`, `/chat`, and graph routing.
- Move deployment-ready backend to a long-running Python host if Vercel limits become restrictive.

## License

Add your license here.
