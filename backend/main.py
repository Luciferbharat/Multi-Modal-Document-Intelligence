from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import shutil

from dotenv import load_dotenv

from backend.ingestion.extract_text import extract_text_chunks
from backend.ingestion.extract_tables import extract_table_chunks
from backend.ingestion.extract_images import extract_image_entries
from backend.ingestion.ocr_engine import run_ocr_on_images
from backend.embedding.text_embedder import TextEmbedder
from backend.embedding.table_embedder import TableEmbedder
from backend.embedding.image_embedder import ImageEmbedder
from backend.retrieval.retriever import Retriever
from backend.llm.generator import LLMGenerator

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
VECTOR_DIR = BASE_DIR / "backend" / "vectorstore" / "faiss_index"
IMAGES_DIR = DATA_DIR / "images"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="Multi-Modal RAG QA System")

# CORS for simple frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add no-cache headers to prevent browser caching issues
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



# Global singletons (simple)
text_embedder = TextEmbedder()
table_embedder = TableEmbedder(text_embedder)
image_embedder = ImageEmbedder(text_embedder)
retriever = Retriever(VECTOR_DIR)
llm = LLMGenerator()


class AskRequest(BaseModel):
    query: str
    top_k: int = 5


class AskResponse(BaseModel):
    answer: str
    sources: list


def _build_and_save_index(pdf_path: Path):
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Text + tables + images
    text_chunks = extract_text_chunks(str(pdf_path))
    table_chunks = extract_table_chunks(str(pdf_path))
    image_entries = extract_image_entries(str(pdf_path), str(IMAGES_DIR))

    # 2. OCR on images
    ocr_entries = run_ocr_on_images(image_entries)

    # 3. Prepare all docs as dicts with 'id', 'page', 'modality', 'text'
    docs = []

    docs.extend(text_chunks)
    docs.extend(table_chunks)
    docs.extend(ocr_entries)

    # 4. Embedding
    embeddings = []
    for doc in docs:
        modality = doc["modality"]
        text = doc["text"]

        if modality == "text":
            vec = text_embedder.embed(text)
        elif modality == "table":
            vec = table_embedder.embed_table_text(text)
        elif modality == "image":
            vec = image_embedder.embed_ocr_text(text)
        else:
            continue

        embeddings.append(vec)

    if not embeddings:
        raise RuntimeError("No embeddings generated. Check ingestion pipeline.")

    retriever.build_and_save_index(docs, embeddings)


@app.post("/api/index-default")
async def index_default():
    """Index the default Qatar IMF PDF."""
    try:
        pdf_path = DATA_DIR / "qatar_test_doc.pdf"
        _build_and_save_index(pdf_path)
        return {"status": "ok", "message": "Indexed default PDF"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-and-index")
async def upload_and_index(file: UploadFile = File(...)):
    """Upload a PDF, save to data/, index it."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    dest_path = DATA_DIR / "uploaded.pdf"
    with dest_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        _build_and_save_index(dest_path)
        return {"status": "ok", "message": "Uploaded and indexed PDF."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask", response_model=AskResponse)
async def ask_rag(body: AskRequest):
    if not retriever.index_exists():
        raise HTTPException(
            status_code=400,
            detail="Index not built yet. Call /api/index-default or /api/upload-and-index first.",
        )

    try:
        results = retriever.search(body.query, body.top_k)
        contexts = [r["text"] for r in results]
        citations = [f"page {r['page']} ({r['modality']})" for r in results]

        answer = llm.generate_answer(body.query, contexts, citations)
        return AskResponse(answer=answer, sources=citations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend as static (optional: open http://localhost:8000)
# MOVED TO END so it doesn't swallow API routes (which are POST)
app.mount(
    "/",
    StaticFiles(directory=BASE_DIR / "frontend", html=True),
    name="frontend",
)
