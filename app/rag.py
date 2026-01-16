"""RAG system with multi-query retrieval, Cohere reranking, and Redis caching."""

from typing import List, Tuple
import os
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.docstore.document import Document
from langchain.retrievers.multi_query import MultiQueryRetriever

from .utils import get_vector_store
from .constants import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    MULTI_QUERY_PROMPT_TEMPLATE,
    EMBEDDING_MODEL,
    REDIS_CACHE_DISTANCE_THRESHOLD,
    RAG_K,
    USE_MULTI_QUERY,
    RERANK_TOP_N,
    COHERE_RERANK_MODEL,
    DEFAULT_OPENAI_MODEL
)

from langchain_cohere import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever

# Configure chat prompt template
PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", USER_PROMPT_TEMPLATE)
])

REDIS_URL = os.getenv("REDIS_URL")
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

# Initialize Redis cache for LLM responses
if REDIS_URL:
    try:
        from langchain.globals import set_llm_cache
        from langchain_community.cache import RedisCache
        import redis
        
        # Test Redis connection
        r = redis.from_url(REDIS_URL)
        r.ping()
        
        # Set up standard Redis cache (exact match caching)
        set_llm_cache(RedisCache(redis_=r))
        print("✓ Redis cache enabled")
    except Exception as e:
        print(f"⚠ Redis cache disabled: {e}")

async def _build_chain():
    """Build RAG chain with retriever, optional reranking, and LLM."""
    store = await get_vector_store()
    base_retriever = store.as_retriever(search_kwargs={"k": RAG_K})
    
    # Enable multi-query retrieval for improved results
    if USE_MULTI_QUERY:
        try:
            from langchain.prompts import PromptTemplate
            query_prompt = PromptTemplate(
                input_variables=["question"],
                template=MULTI_QUERY_PROMPT_TEMPLATE
            )
            
            llm_for_queries = ChatOpenAI(model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL), temperature=0)
            multi_query_retriever = MultiQueryRetriever.from_llm(
                retriever=base_retriever,
                llm=llm_for_queries,
                prompt=query_prompt,
                include_original=True  # Always include the original query
            )
            print("✓ Multi-query retriever enabled")
            base_retriever = multi_query_retriever
        except Exception as e:
            print(f"⚠ Multi-query retriever failed: {e}")
    
    # Apply Cohere reranking if configured
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if cohere_api_key:
        try:
            compressor = CohereRerank(
                top_n=RERANK_TOP_N,
                model=COHERE_RERANK_MODEL,
            )
            retriever = ContextualCompressionRetriever(
                base_retriever=base_retriever,
                base_compressor=compressor,
            )
            print(f"✓ Cohere reranker enabled (top_n={RERANK_TOP_N})")
        except Exception as e:
            print(f"⚠ Cohere reranker failed: {e}")
            retriever = base_retriever
    else:
        retriever = base_retriever
    
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL))
    doc_chain = create_stuff_documents_chain(llm, prompt=PROMPT)
    rag_chain = create_retrieval_chain(retriever, doc_chain)

    return rag_chain

async def answer_with_docs_async(question: str) -> Tuple[str, List[str], List[str]]:
    """Query RAG system and return answer, sources, and context."""
    chain = await _build_chain()
    result = await chain.ainvoke({"input": question})
    
    answer = result["answer"]
    sources = []
    docs:List[Document] = result["context"]
    unique_sources = {d.metadata.get("source") for d in docs}
    sources = sorted(unique_sources)
    
    context = []
    for d in docs:
        context.append(d.page_content)

    return answer, sources, context