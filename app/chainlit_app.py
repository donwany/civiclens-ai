"""
Chainlit-based Company Knowledge Assistant

Interactive chat interface for document Q&A using RAG (Retrieval-Augmented Generation).
Provides document ingestion capabilities and real-time question answering with source attribution.
"""

import asyncio
import os
import time
from typing import Dict, Any

import chainlit as cl

from app.rag import answer_with_docs_async
from app.ingest import run_ingest_async

# ============================================================================
# Global State Management
# ============================================================================
# Thread-safe ingestion tracking to prevent concurrent ingestion jobs
_ingest_lock = asyncio.Lock()
_ingest_task: asyncio.Task | None = None
_ingest_last: Dict[str, Any] = {
    "status": "idle",      # Current status: idle | running | succeeded | failed
    "started_at": None,    # Timestamp when ingestion started
    "finished_at": None,   # Timestamp when ingestion completed
    "stats": None,         # Ingestion statistics (documents, chunks, files)
    "error": None,         # Error message if failed
}


async def _ingest_job():
    """
    Execute document ingestion in background.
    
    Processes documents from data/ folder and stores them in the vector database.
    Updates global state to track progress and results.
    """
    # Initialize ingestion status
    _ingest_last.update({
        "status": "running",
        "started_at": time.time(),
        "finished_at": None,
        "stats": None,
        "error": None
    })
    
    try:
        # Run ingestion process
        stats = await run_ingest_async()
        
        # Update with success status
        _ingest_last.update({
            "status": "succeeded",
            "finished_at": time.time(),
            "stats": stats
        })
    except Exception as e:
        # Update with failure status
        _ingest_last.update({
            "status": "failed",
            "finished_at": time.time(),
            "error": str(e)
        })


# @cl.on_chat_start
# async def start():
#     """
#     Initialize chat session on user connection.
    
#     Sets up default user preferences and displays welcome message.
#     """
#     # Configure default session settings
#     cl.user_session.set("show_sources", True)
    
#     # Send welcome message
#     await cl.Message(
#         content="Welcome! Type `/ingest` to load documents or start asking questions if documents are already loaded."
#     ).send()

@cl.on_chat_start
async def start():
    """
    Initialize chat session on user connection.

    Sets up default user preferences, displays welcome message,
    and provides example questions users can ask.
    """
    # Configure default session settings
    cl.user_session.set("show_sources", True)

    # Suggested questions for the UI
    suggested_questions = [
        "What is the mission of the President’s Council of Advisors on Science and Technology?",
        "Why restore the Department of War?",
        "Why should men be excluded from women’s sports?",
        "What are the objectives of strengthening efforts to protect U.S. nationals from wrongful detention abroad?",
        "What actions are required to end radical indoctrination in K–12 schooling?",
        "How can educational freedom and opportunity for families be expanded?",
        "How can parents and communities be empowered to improve education outcomes?",
        "Why criminalize burning the American flag?",
        "How can barriers to AI leadership be removed?",
        "What does preventing “woke AI” in the federal government entail?",
        "How can the export of the American AI technology stack be promoted globally?",
        "What role does AI play in curing pediatric cancer?",
        "How can the integrity of American elections be preserved?",
        "How can the meaning and value of American citizenship be protected?"
    ]

    # Store questions in session (for UI rendering, buttons, or dropdowns)
    cl.user_session.set("suggested_questions", suggested_questions)

    # Send welcome message with guidance
    await cl.Message(
        content=(
            "Welcome! to 🇺🇸 CivicLens AI \n Advancing AI Education, Civic Literacy, and Responsible Governance for America’s Future  \n"
            "Type `/ingest` to load documents or start asking questions if documents are already loaded.\n\n"
            "You can also explore questions such as:\n"
            + "\n".join([f"- {q}" for q in suggested_questions])
        )
    ).send()



@cl.on_message
async def main(message: cl.Message):
    """
    Process incoming user messages.
    
    Routes commands to command handler or processes questions through RAG system.
    Displays answers with sources and context.
    """
    content = message.content.strip()
    
    # Route commands to dedicated handler
    if content.startswith("/"):
        await handle_command(content)
        return
    
    # Validate non-empty input
    if not content:
        await cl.Message(content="Please ask a question or use a command like `/ingest` or `/status`.").send()
        return
    
    # Initialize response message
    msg = cl.Message(content="")
    await msg.send()
    
    start_time = time.perf_counter()
    
    try:
        # Query RAG system for answer
        answer, sources, contexts = await answer_with_docs_async(content)
        
        elapsed = time.perf_counter() - start_time
        
        # Display main answer
        msg.content = answer
        await msg.update()
        
        # Append source documents if enabled
        show_sources = cl.user_session.get("show_sources", True)
        if show_sources and sources:
            sources_text = "\n\n**Sources:**\n" + "\n".join([f"- `{src}`" for src in sources])
            msg.content += sources_text
            await msg.update()
        
        # Attach context snippets as side panel elements
        if contexts:
            elements = []
            for idx, ctx in enumerate(contexts[:5], 1):  # Display top 5 contexts
                elements.append(
                    cl.Text(
                        name=f"Context {idx}",
                        content=ctx,
                        display="side"
                    )
                )
            msg.elements = elements
            await msg.update()
        
        # Display performance metrics
        await cl.Message(
            content=f"_⏱️ Response time: {elapsed:.2f}s_",
            author="System"
        ).send()
        
    except Exception as e:
        # Log error details for debugging
        print(f"Error in main: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Display user-friendly error message
        msg.content = f"❌ Error: {str(e)}\n\nI encountered an error processing your question. Please try again or check the logs."
        await msg.update()


async def handle_command(command: str):
    """
    Process special slash commands.
    
    Available commands: /ingest, /status, /help
    
    Args:
        command (str): Command string starting with '/'
    """
    global _ingest_task
    
    # Extract command name
    cmd = command.lower().split()[0]
    
    # Document ingestion command
    if cmd == "/ingest":
        # Prevent concurrent ingestion jobs
        async with _ingest_lock:
            if _ingest_task and not _ingest_task.done():
                await cl.Message(
                    content="⚠️ Ingestion is already running. Please wait for it to complete."
                ).send()
                return
            
            await cl.Message(content="🔄 Starting document ingestion...").send()
            _ingest_task = asyncio.create_task(_ingest_job())
        
        # Monitor ingestion progress and report results
        try:
            await _ingest_task
            status = _ingest_last["status"]
            
            if status == "succeeded":
                stats = _ingest_last.get("stats", {})
                files = stats.get("files", [])
                
                # Build list of ingested files
                file_list = ""
                if files:
                    file_list = "\n\n**Top 5 Files ingested:**\n" + "\n".join([f"- `{os.path.basename(f)}`" for f in files[:5]])
                
                # Report success with statistics
                await cl.Message(
                    content=f"✅ Ingestion completed successfully!\n\n"
                           f"- Documents: {stats.get('documents', 0)}\n"
                           f"- Chunks: {stats.get('chunks', 0)}"
                           f"{file_list}"
                ).send()
            else:
                # Report failure
                error = _ingest_last.get("error", "Unknown error")
                await cl.Message(
                    content=f"❌ Ingestion failed: {error}"
                ).send()
        except Exception as e:
            await cl.Message(content=f"❌ Ingestion error: {str(e)}").send()
    
    # Status inquiry command
    elif cmd == "/status":
        # Build status message based on current state
        status = _ingest_last["status"]
        
        if status == "idle":
            msg = "📊 **Ingestion Status:** Idle\n\nNo ingestion has been run yet. Use `/ingest` to start."
        elif status == "running":
            msg = "📊 **Ingestion Status:** Running 🔄\n\nPlease wait..."
        elif status == "succeeded":
            stats = _ingest_last.get("stats", {})
            finished = _ingest_last.get("finished_at")
            elapsed = finished - _ingest_last.get("started_at", finished) if finished else 0
            msg = (f"📊 **Ingestion Status:** Succeeded ✅\n\n"
                  f"- Documents: {stats.get('documents', 0)}\n"
                  f"- Chunks: {stats.get('chunks', 0)}\n"
                  f"- Time: {elapsed:.1f}s")
        else:  # failed
            error = _ingest_last.get("error", "Unknown error")
            msg = f"📊 **Ingestion Status:** Failed ❌\n\nError: {error}"
        
        await cl.Message(content=msg).send()
    
    # Help documentation command
    elif cmd == "/help":
        await cl.Message(
            content="""# Available Commands

**Document Management:**
- `/ingest` - Ingest documents from the data/ folder
- `/status` - Check ingestion status

**Help:**
- `/help` - Show this help message

**Tips:**
- Just type your question to get answers from ingested documents
- Sources are automatically displayed with answers
- Context snippets are available in the side panel"""
        ).send()
    
    # Unknown command
    else:
        await cl.Message(
            content=f"Unknown command: `{cmd}`\n\nUse `/help` to see available commands."
        ).send()


@cl.on_settings_update
async def setup_settings(settings):
    """
    Update user session settings.
    
    Args:
        settings (dict): Updated settings from UI
    """
    cl.user_session.set("show_sources", settings.get("show_sources", True))
