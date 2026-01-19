"""
Document Ingestion Module

Loads documents from data/ folder, chunks them, and stores in vector database.
Supports PDF, DOCX, Markdown, and TXT files.

"""


import tempfile
from typing import Tuple
import boto3

import os, glob, uuid, asyncio, traceback
from typing import Iterable, List, Dict, Any
from pathlib import Path

from langchain.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader, PyMuPDFLoader, UnstructuredWordDocumentLoader,TextLoader

from .utils import get_vector_store
from .constants import (
    DEFAULT_DATA_DIR, 
    CHUNK_SIZE, 
    CHUNK_OVERLAP, 
    INDEX_NAME,
    HNSW_EF_CONSTRUCTION,
    HNSW_M
)
from langchain_postgres.v2.indexes import HNSWIndex, DistanceStrategy

DATA_DIR = os.getenv("DATA_DIR", DEFAULT_DATA_DIR)

def _load_docs(base: str = DATA_DIR) -> tuple[List[Document], List[str]]:
    """Load documents from directory and return documents with file paths."""
    docs: List[Document] = []
    file_paths: List[str] = []

    # Recursively process all files in base directory
    for path in glob.glob(os.path.join(base, "**", "*"), recursive=True):
        if os.path.isdir(path) or os.path.basename(path).startswith("."):
            continue
        
        ext = os.path.splitext(path)[1].lower()
        try:
            # Load based on file extension
            if ext == ".md":
                for d in UnstructuredMarkdownLoader(path).load():
                    docs.append(d)
                file_paths.append(path)
            elif ext == ".pdf":
                for d in PyMuPDFLoader(path).load():
                    docs.append(d)
                file_paths.append(path)
            elif ext == ".docx":
                for d in UnstructuredWordDocumentLoader(path).load():
                    docs.append(d)
                file_paths.append(path)
            elif ext == ".txt":
                for d in TextLoader(path).load():
                    docs.append(d)
                file_paths.append(path)

        except Exception:
            print(f"INGEST ERROR: failed to load {path}")
            traceback.print_exc()

    return docs, file_paths


# # Environment variables
# S3_BUCKET = os.getenv("S3_BUCKET")
# S3_PREFIX = os.getenv("S3_PREFIX", "")  # optional folder path in bucket

# # AWS variables (boto3 picks these up automatically)
# AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
# AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

# s3 = boto3.client("s3")

# def _load_docs_from_s3(
#     bucket: str = S3_BUCKET,
#     prefix: str = S3_PREFIX,
# ) -> Tuple[List[Document], List[str]]:
#     """Load documents from an S3 bucket and return documents with S3 paths."""
    
#     docs: List[Document] = []
#     file_paths: List[str] = []

#     paginator = s3.get_paginator("list_objects_v2")

#     for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
#         for obj in page.get("Contents", []):
#             key = obj["Key"]

#             # Skip directories and hidden files
#             if key.endswith("/") or os.path.basename(key).startswith("."):
#                 continue

#             ext = os.path.splitext(key)[1].lower()

#             try:
#                 with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
#                     s3.download_fileobj(bucket, key, tmp)
#                     tmp_path = tmp.name

#                 # Load based on file extension
#                 if ext == ".md":
#                     docs.extend(UnstructuredMarkdownLoader(tmp_path).load())
#                 elif ext == ".pdf":
#                     docs.extend(PyMuPDFLoader(tmp_path).load())
#                 elif ext == ".docx":
#                     docs.extend(UnstructuredWordDocumentLoader(tmp_path).load())
#                 elif ext == ".txt":
#                     docs.extend(TextLoader(tmp_path).load())
#                 else:
#                     continue

#                 file_paths.append(f"s3://{bucket}/{key}")

#             except Exception:
#                 print(f"INGEST ERROR: failed to load s3://{bucket}/{key}")
#                 traceback.print_exc()

#             finally:
#                 if os.path.exists(tmp_path):
#                     os.remove(tmp_path)

#     return docs, file_paths



def _chunk(docs: List[Document]) -> List[Document]:
    """Split documents into smaller chunks for embedding."""
    print(f"INGEST: chunking {len(docs)} documents")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    
    try:
        return splitter.split_documents(docs)
    except Exception:
        print(f"INGEST ERROR: chunking failed")
        traceback.print_exc()
        raise

async def _create_index(store):
    """Create HNSW index for efficient similarity search if not exists."""
    if await store.ais_valid_index(INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists, skipping creation.")
        return
    
    index = HNSWIndex(
        name=INDEX_NAME,
        distance_strategy=DistanceStrategy.COSINE_DISTANCE,
        ef_construction=HNSW_EF_CONSTRUCTION,
        m=HNSW_M,
    )
    await store.aapply_vector_index(index, concurrently=True)
    print("Index created successfully.")

async def run_ingest_async() -> dict:
    """
    Execute document ingestion pipeline.
    
    Returns:
        dict: Statistics with document count, chunk count, and file paths
    """
    # Load documents from data directory
    docs, file_paths = _load_docs()

    # Split into chunks
    chunks = _chunk(docs)

    # Store in vector database
    store = await get_vector_store()
    await store.aadd_documents(chunks)
    print(f"INGEST: {len(docs)} docs, {len(chunks)} chunks")

    # Create search index
    await _create_index(store)

    return {
        "documents": len(docs),
        "chunks": len(chunks),
        "files": file_paths,
    }

