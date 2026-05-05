"""
ingest.py  –  Run this ONCE (or whenever docs change) to build the vector store.

Usage:
    python ingest.py

Put your PDFs, .txt, and .md files inside the  ./docs/  folder before running.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── LangChain imports ──────────────────────────────────────────────────────
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

DOCS_DIR   = Path(__file__).parent / "docs"
CHROMA_DIR = Path(__file__).parent / "chroma_db"


def load_documents():
    """Load all PDFs and text files from ./docs/"""
    docs = []

    # Load PDFs
    pdf_loader = DirectoryLoader(
        str(DOCS_DIR),
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    docs.extend(pdf_loader.load())

    # Load .txt files
    txt_loader = DirectoryLoader(
        str(DOCS_DIR),
        glob="**/*.txt",
        loader_cls=TextLoader,
        show_progress=True,
    )
    docs.extend(txt_loader.load())

    # Load .md files
    md_loader = DirectoryLoader(
        str(DOCS_DIR),
        glob="**/*.md",
        loader_cls=TextLoader,
        show_progress=True,
    )
    docs.extend(md_loader.load())

    return docs


def ingest():
    if not DOCS_DIR.exists():
        print(f"[ERROR] docs/ folder not found at {DOCS_DIR}")
        sys.exit(1)

    print(f"\n📂  Loading documents from  {DOCS_DIR} …")
    docs = load_documents()

    if not docs:
        print("[WARN] No documents found. Add PDFs or .txt files to ./docs/")
        sys.exit(0)

    print(f"✅  Loaded {len(docs)} document page(s)")

    # ── Split into chunks ──────────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"✂️   Split into {len(chunks)} chunks")

    # ── Embed using a free local model (no API key needed) ─────────────────
    print("🔢  Embedding with sentence-transformers/all-MiniLM-L6-v2 …")
    embeddings = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # ── Store in ChromaDB ──────────────────────────────────────────────────
    print(f"💾  Saving vector store to  {CHROMA_DIR} …")
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="institution_kb",
    )
    vectordb.persist()

    print(f"\n🎉  Done! {len(chunks)} chunks indexed into ChromaDB.")
    


if __name__ == "__main__":
    ingest()
