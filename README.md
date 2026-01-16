# 🇺🇸 CivicLens AI
Making Presidential Decisions Understandable for Every American Youth
---

An AI-powered document Q&A system built with Chainlit, LangChain, and RAG (Retrieval-Augmented Generation). Upload Executive Orders documents and get accurate answers with source attribution.

![kids](./assets/kids.png)

## 🚀 Executive Summary

Over the course of his administration, President Donald J. Trump signed more than 226 Executive Orders, shaping critical aspects of American society including the economy, education, healthcare, national security, technology, and global engagement. Despite their profound and long-term impact, Executive Orders remain poorly understood by many young Americans, limiting civic awareness and informed participation in democratic processes.

This project addresses that gap by leveraging responsible artificial intelligence to translate complex executive actions into clear, accessible, and age-appropriate explanations for children, teenagers, families, and future workers. Inspired by visual documentation of signed Executive Orders, the initiative recognizes a broader challenge: policy decisions that directly affect everyday life are often inaccessible to the very populations they shape.

The proposed solution uses AI-driven summarization, contextualization, and educational interfaces to improve civic literacy at scale, while prioritizing transparency, accuracy, bias mitigation, and data safety. By making government actions understandable and relevant, the project empowers young people to engage critically with public policy, supports equitable access to civic knowledge, and strengthens trust in democratic institutions. This initiative aligns with the White House AI Challenge’s goals of applying AI for public good, advancing education, and fostering informed, inclusive participation in civic life.

## 🎯 The Problem

* Executive orders are written in **complex legal language**
* Youth are often **excluded from political discourse**
* Civics education struggles to stay **current and engaging**
* Policymakers themselves face **information overload**
* Critical decisions are sometimes made without a **plain-language briefing**

America cannot maintain global leadership if its future leaders do not understand how government works **today**.

### 📚 **Impact**

CivicLens AI delivers measurable national impact by:

* Making real government decisions understandable to millions of students
* Encouraging early civic participation and critical thinking
* Connecting AI education to real-world governance and leadership
* Preparing youth to responsibly engage with AI-powered systems

By meeting young Americans where they are and explaining policies that affect their daily lives, CivicLens AI turns AI education into a living civic experience rather than an abstract technical concept.

### 🌟**Innovation**

CivicLens AI introduces a **multi-audience AI translation framework** that generates:

* Child-friendly explanations (ages 10–12)
* Teen-focused impact summaries (ages 13–15)
* Policy and trade-off analyses (ages 16–18)
* Plain-language executive briefings for policymakers

This “one document, many explanations” approach is a novel application of AI that bridges education, governance, and leadership—an area rarely addressed by existing AI education tools.

### 👧🧒 For Youth (Ages 10–18)

CivicLens AI makes government understandable and engaging by:

- Explaining executive orders in **simple, relatable language**
- Adapting explanations based on age group:
  - **Ages 10–12:** Story-based explanations and everyday examples
  - **Ages 13–15:** Real-world connections to school, technology, and society
  - **Ages 16–18:** Policy impacts, trade-offs, and future implications
- Showing **how policies affect education, jobs, safety, technology, and opportunity**
- Encouraging **curiosity, critical thinking, and civic responsibility**
- Bringing youth into political discourse as **future leaders, not passive observers**

### 🏛️ For the White House & Federal Leaders

CivicLens AI also supports governance by:

- Providing **plain-English summaries** of executive orders before signing
- Highlighting:
  - Youth and generational impact
  - Long-term consequences
  - Implementation challenges
- Flagging potential misunderstandings and public perception risks
- Enabling **faster, clearer decision-making** under intense time constraints

---

## Features

- 🔍 **Multi-Query Retrieval** - Generates alternative queries for improved search results
- 📊 **Cohere Reranking** - Uses Cohere's reranking model for better relevance
- ⚡ **Redis Caching** - Caches LLM responses for faster repeated queries
- 💬 **Interactive Chat Interface** - Built with Chainlit for real-time conversations
- 📁 **Multiple File Formats** - Supports PDF, DOCX, Markdown, and TXT files
- 🗂️ **PostgreSQL + pgvector** - Efficient vector storage and similarity search
- 📈 **RAGAS Evaluation** - Automated quality metrics for RAG system performance
- 🔬 **LangSmith Integration** - Optional tracing and monitoring for debugging

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Chainlit |
| **LLM** | OpenAI GPT-4o |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Vector DB** | PostgreSQL + pgvector |
| **Cache** | Redis |
| **Reranking** | Cohere |
| **Framework** | LangChain |
| **Deployment** | Docker + Docker Compose |

## Architecture

![kids](./assets/whitehouse.drawio.png)


<!-- ```
┌─────────────┐
│   Chainlit  │ ← User Interface
└──────┬──────┘
       │
┌──────▼──────┐
│  RAG System │ ← Multi-query + Reranking
└──────┬──────┘
       │
   ┌───▼───┬─────────┬─────────┐
   │ PG +  │  Redis  │  OpenAI │
   │pgvector│  Cache  │   API   │
   └───────┴─────────┴─────────┘
``` -->

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- (Optional) Cohere API key for reranking
- (Optional) LangSmith API key for tracing and monitoring

## Quick Start

### 0. Download Dataset
```python
# download .csv from https://www.federalregister.gov/presidential-documents/executive-orders

python download_executive_orders_pdf_files.py
```

### 1. Clone the Repository

```bash
git clone <repository-url>
cd civic-lens-ai
```

### 2. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and set required variables:

```env
# Required
OPENAI_API_KEY=sk-...your-key...
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres

# Optional but recommended
REDIS_URL=redis://redis:6379
COHERE_API_KEY=your-cohere-key

# Optional - LangSmith tracing and monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=company-knowledge-assistant
```

### 3. Add Documents

Place your documents in the `data/` folder:

```bash
mkdir -p data
cp /path/to/your/documents/* data/
```

Supported formats: `.pdf`, `.docx`, `.md`, `.txt`

### 4. Start the Application

```bash
docker-compose up -d
```

This will start:
- PostgreSQL with pgvector extension (port 5432)
- Redis (port 6379)
- Chainlit application (port 1776)

### 5. Access the Interface

Open your browser and navigate to:

```
http://localhost:1776
```

### 6. Ingest Documents

In the chat interface, type:

```
/ingest
```

Wait for the ingestion to complete. You'll see statistics about documents and chunks processed.

### 7. Ask Questions

Simply type your questions in the chat:

```
What are the objectives of strengthening efforts to protect U.S. nationals from wrongful detention abroad?
```

The system will:
1. Retrieve relevant document chunks
2. Rerank results (if Cohere is configured)
3. Generate an answer with source attribution
4. Display context snippets in the side panel

## Available Commands

| Command | Description |
|---------|-------------|
| `/ingest` | Load documents from `data/` folder |
| `/status` | Check ingestion status |
| `/help` | Display help message |

## Local Development (Without Docker)

### 1. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start PostgreSQL and Redis

You can use Docker for just the databases:

```bash
docker-compose up postgres redis -d
```

Or install locally and ensure they're running.

### 3. Update Environment Variables

For local development, update `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
REDIS_URL=redis://localhost:6379
```

### 4. Run the Application

```bash
chainlit run app/chainlit_app.py --host 0.0.0.0 --port 1776
```

## Configuration

### Chunking Parameters

Edit `app/constants.py`:

```python
CHUNK_SIZE = 500          # Characters per chunk
CHUNK_OVERLAP = 100       # Overlap between chunks
```

### Retrieval Settings

```python
RAG_K = 10                # Number of chunks to retrieve
USE_MULTI_QUERY = True    # Enable multi-query retrieval
RERANK_TOP_N = 8          # Top chunks after reranking
```

### Model Selection

```python
DEFAULT_OPENAI_MODEL = "gpt-4o"           # LLM for answers
EMBEDDING_MODEL = "text-embedding-3-small" # For embeddings
```

## Evaluation

Run RAGAS evaluation to measure system quality:

```bash
python -m app.eval_ragas
```

This evaluates:
- **Faithfulness**: Answer accuracy vs. context
- **Answer Relevancy**: How well answers address questions
- **Context Precision**: Quality of retrieved chunks
- **Context Recall**: Completeness of information

## Project Structure

```
company-knowledge-assistant-v2/
├── app/
│   ├── chainlit_app.py      # Main Chainlit application
│   ├── rag.py               # RAG system implementation
│   ├── ingest.py            # Document ingestion
│   ├── utils.py             # Vector store utilities
│   ├── constants.py         # Configuration constants
│   └── eval_ragas.py        # RAGAS evaluation
├── data/                    # Document storage
├── seed/                    # Test data for evaluation
├── .chainlit/
│   └── config.toml          # Chainlit UI configuration
├── docker-compose.yml       # Docker services
├── Dockerfile               # Application container
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

## Troubleshooting

### Container Issues

```bash
# View logs
docker-compose logs app

# Restart services
docker-compose restart

# Rebuild containers
docker-compose up --build
```

### Database Connection Errors

Ensure PostgreSQL is healthy:

```bash
docker-compose ps
docker-compose logs postgres
```

### Redis Cache Not Working

Check Redis connection:

```bash
docker-compose logs redis
docker exec -it cka-redis redis-cli ping
```

### Ingestion Failures

- Verify documents are in `data/` folder
- Check file formats are supported
- Review application logs for errors

## Performance Tips

1. **Enable Cohere Reranking**: Significantly improves answer quality
2. **Use Redis Caching**: Speeds up repeated queries
3. **Adjust `RAG_K`**: Higher values retrieve more context but slower
4. **Tune Chunk Size**: Balance between context and precision

## API Keys

### OpenAI (Required)
Get your API key from: https://platform.openai.com/api-keys

### Cohere (Optional)
Get your API key from: https://dashboard.cohere.com/api-keys

Improves answer quality by reranking retrieved documents.

### LangSmith (Optional)
Get your API key from: https://smith.langchain.com/settings

**Benefits:**
- **Trace LLM calls**: Monitor every step of the RAG pipeline
- **Debug issues**: See exact prompts, responses, and latencies
- **Track costs**: Monitor OpenAI API usage and spending
- **Evaluate performance**: Compare different configurations
- **Production monitoring**: Alert on errors and performance degradation

**Setup:**
1. Create account at https://smith.langchain.com
2. Create a new project (or use default)
3. Get API key from Settings > API Keys
4. Add to `.env`:
   ```env
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=lsv2_pt_...
   LANGCHAIN_PROJECT=company-knowledge-assistant
   ```

**View Traces:**
After starting the application, visit https://smith.langchain.com to see:
- Complete trace of each question/answer
- Token usage per LLM call
- Retrieved documents and reranking scores
- Cache hit/miss statistics
- Error tracking and debugging info

