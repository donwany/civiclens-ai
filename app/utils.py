"""Utility functions for vector store initialization."""

import os
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.v2.engine import PGEngine
from langchain_postgres.v2.vectorstores import PGVectorStore
from .constants import EMBEDDING_MODEL, EMBEDDING_TABLE_NAME

PG_CONN_STR = os.getenv("DATABASE_URL")

PG_ENGINE = PGEngine.from_connection_string(
    url=PG_CONN_STR,
)

embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

async def get_vector_store() -> PGVectorStore:
    """Initialize and return PostgreSQL vector store instance."""
    return await PGVectorStore.create(
        engine=PG_ENGINE,
        embedding_service=embeddings,
        table_name=EMBEDDING_TABLE_NAME,
    )

