"""
PebblePay Backend API Server
Integrates the contract agent system with a REST API.
"""
import os
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import io

from app.graph_workflow import create_contract_graph_agent, get_opening_message
from app.pdf_generator import generate_contract_pdf
from app.nodes.explain_contract_node import explain_contract_node

# ——— TTS Support (from main branch)
from tts import router as tts_router
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
root_dir = Path(__file__).parent.parent
load_dotenv(dotenv_path=root_dir / ".env")
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)

# Initialize FastAPI app
app = FastAPI(title="PebblePay API", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ——— Include TTS Router
app.include_router(tts_router, prefix="/api")

# ——— Agent Session Storage
agent_sessions: Dict[str, Any] = {}


class ChatMessage(BaseModel):
    """Request model for chat messages."""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat messages."""
    response: str
    session_id: str
    contract_spec: Optional[Dict[str, Any]] = None
    contract_text: Optional[str] = None
    summary: Optional[str] = None
    missing_fields: Optional[list] = None
    suggestions: Optional[list] = None
    contract_ready: bool = False


@app.get("/")
async def root():
    return {"status": "ok", "service": "PebblePay API"}


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/opening-message")
async def get_opening_message_endpoint():
    """Get the opening message for new conversations."""
    return {"message": get_opening_message()}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):

    try:
        session_id = message.session_id

        # Create new session if needed
        if not session_id or session_id not in agent_sessions:
            agent = create_contract_graph_agent()
            session_id = str(uuid.uuid4())
            agent_sessions[session_id] = agent
        else:
            agent = agent_sessions[session_id]

        # Run agent step
        state = await agent.run(message.message)

        assistant_message = state.get("assistant_message", "")
        contract_spec = state.get("contract_spec")
        contract_text = state.get("contract_text")
        summary = state.get("summary")
        missing_fields = state.get("missing_fields", [])

        suggestions = None
        if state.get("next_action") == "ASK_MORE" and missing_fields:
            current_field = state.get("current_question_field")
            suggestions = get_field_suggestions(current_field) if current_field else None

        contract_ready = bool(contract_text)

        return ChatResponse(
            response=assistant_message or "Processing...",
            session_id=session_id,
            contract_spec=contract_spec,
            contract_text=contract_text,
            summary=summary,
            missing_fields=missing_fields,
            suggestions=suggestions,
            contract_ready=contract_ready,
        )

    except Exception as e:
        print("[API] Error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}/download-contract")
async def download_contract_pdf(session_id: str):

    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = agent_sessions[session_id]
    state = agent.state

    contract_text = state.get("contract_text")
    contract_spec = state.get("contract_spec", {})

    if not contract_text:
        raise HTTPException(status_code=400, detail="No contract available")

    try:
        pdf_bytes = generate_contract_pdf(contract_text, contract_spec)

        title = contract_spec.get("title", "contract")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]
        filename = f"{safe_title}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}/explain-contract")
async def explain_contract(session_id: str):

    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = agent_sessions[session_id]
    state = agent.state

    contract_text = state.get("contract_text")
    if not contract_text:
        raise HTTPException(status_code=400, detail="No contract available")

    if state.get("summary"):
        return {"explanation": state["summary"]}

    result = await explain_contract_node(state)
    summary = result.get("summary", "")

    agent.state["summary"] = summary

    return {"explanation": summary}


def get_field_suggestions(field: str) -> list:
    suggestions_map = {
        "payment_schedule": ["50% upfront", "100% upfront", "On completion"],
        "max_revisions": ["Unlimited", "2 revisions", "3 revisions"],
        "dispute_method": ["Mediation", "Negotiation", "Arbitration"],
        "late_delivery_policy": ["No penalty", "5% per day late", "3-day grace period"],
    }
    return suggestions_map.get(field, [])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

