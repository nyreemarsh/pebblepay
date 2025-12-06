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

# Initialize FastAPI app
app = FastAPI(title="PebblePay API", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active agent sessions
# In production, use Redis or a database for session management
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
    contract_ready: bool = False  # Flag to show download/explain buttons


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "PebblePay API"}


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Process a chat message through the contract agent.
    
    Creates a new agent session if session_id is not provided.
    Returns the agent's response along with contract state.
    """
    try:
        # Get or create session
        session_id = message.session_id
        if not session_id or session_id not in agent_sessions:
            # Create new agent session
            agent = create_contract_graph_agent()
            session_id = str(uuid.uuid4())
            agent_sessions[session_id] = agent
        else:
            agent = agent_sessions[session_id]
        
        # Process the message through the agent
        state = await agent.run(message.message)
        
        # Extract response components
        assistant_message = state.get("assistant_message", "")
        contract_spec = state.get("contract_spec")
        contract_text = state.get("contract_text")
        summary = state.get("summary")
        missing_fields = state.get("missing_fields", [])
        
        # Generate suggestions if we're asking questions
        suggestions = None
        if state.get("next_action") == "ASK_MORE" and missing_fields:
            # Provide quick answer suggestions based on the question
            current_field = state.get("current_question_field")
            if current_field:
                # Add contextual suggestions based on field type
                suggestions = get_field_suggestions(current_field)
        
        # Check if contract is ready
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
        print(f"[API] Error processing chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.get("/api/session/{session_id}/state")
async def get_session_state(session_id: str):
    """Get the current state of an agent session."""
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    agent = agent_sessions[session_id]
    return {
        "session_id": session_id,
        "state": agent.state,
        "turn_count": agent.turn_count,
    }


@app.post("/api/session/{session_id}/reset")
async def reset_session(session_id: str):
    """Reset an agent session to initial state."""
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    agent = agent_sessions[session_id]
    agent.reset()
    
    return {"status": "reset", "session_id": session_id}


@app.get("/api/opening-message")
async def get_opening_message_endpoint():
    """Get the opening message for new conversations."""
    return {"message": get_opening_message()}


@app.get("/api/session/{session_id}/download-contract")
async def download_contract_pdf(session_id: str):
    """
    Download the generated contract as a PDF.
    """
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    agent = agent_sessions[session_id]
    state = agent.state
    
    contract_text = state.get("contract_text")
    contract_spec = state.get("contract_spec", {})
    
    if not contract_text:
        raise HTTPException(status_code=400, detail="No contract has been generated yet")
    
    try:
        # Generate PDF
        pdf_bytes = generate_contract_pdf(contract_text, contract_spec)
        
        # Create filename from title
        title = contract_spec.get("title", "contract")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]
        filename = f"{safe_title}.pdf"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition",
            }
        )
    except Exception as e:
        print(f"[API] Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@app.get("/api/session/{session_id}/explain-contract")
async def explain_contract(session_id: str):
    """
    Get a plain-English explanation of the contract.
    """
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    agent = agent_sessions[session_id]
    state = agent.state
    
    contract_text = state.get("contract_text")
    contract_spec = state.get("contract_spec", {})
    
    if not contract_text:
        raise HTTPException(status_code=400, detail="No contract has been generated yet")
    
    # Check if we already have a summary
    if state.get("summary"):
        return {"explanation": state["summary"]}
    
    try:
        # Generate explanation using the explain node
        result = await explain_contract_node(state)
        summary = result.get("summary", "")
        
        # Store it in the session
        agent.state["summary"] = summary
        
        return {"explanation": summary}
    except Exception as e:
        print(f"[API] Error explaining contract: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error explaining contract: {str(e)}")


def get_field_suggestions(field: str) -> list:
    """Generate contextual suggestions for a field."""
    suggestions_map = {
        "payment_schedule": [
            "50% upfront, 50% on completion",
            "100% upfront",
            "100% on completion",
            "Milestone-based payments",
        ],
        "max_revisions": [
            "Unlimited revisions",
            "2 rounds of revisions",
            "3 rounds of revisions",
            "1 round of revisions",
        ],
        "dispute_method": [
            "Mediation first, then court",
            "Direct negotiation",
            "Small claims court",
            "Arbitration",
        ],
        "late_delivery_policy": [
            "No penalty",
            "5% per day late",
            "Grace period of 3 days",
        ],
    }
    return suggestions_map.get(field, [])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

