# Multi-Modal RAG QA System (Qatar IMF Report)

This project implements a **multi-modal Retrieval-Augmented Generation (RAG)** system
for answering questions over IMF-style Article IV reports (text, tables, images). :contentReference[oaicite:1]{index=1}  

## Features

- PDF ingestion:
  - Text extraction + smart chunking (page-aware)
  - Table extraction (via Camelot, if installed)
  - Image extraction + OCR (Tesseract)
- Unified vector index (FAISS) over all modalities
- RAG-based QA using Groq LLaMA model with page-level citations
- Simple web UI (HTML/JS/CSS) for:
  - indexing default or uploaded PDF
  - asking questions and viewing sources
- Single entrypoint: `python run.py`

## Quickstart

```bash
pip install -r requirements.txt
# Ensure Tesseract is installed and in PATH
python run.py
