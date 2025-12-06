"""
Graph Workflow Definition
Unified contract generation workflow that handles both chat and blocks input.

Workflow:
1. detect_input_type - Decide if input is chat or blocks
2. parse (chat or blocks) - Parse into contract_spec
3. normalize_spec - Fill defaults, format dates
4. validate_spec - Check for issues
5. generate_contract - Create contract text
6. explain_contract - Summarize in plain English
"""
from typing import Dict, Any, Optional
from .state_graph import StateGraph, GraphAgent
from .contract_schema import get_empty_contract_spec

# Import all nodes
from .nodes.detect_input_node import detect_input_type_node, route_by_input_type
from .nodes.update_spec_node import update_spec_from_message_node
from .nodes.parse_blocks_node import parse_blocks_node
from .nodes.normalize_spec_node import normalize_spec_node
from .nodes.validate_spec_node import validate_spec_node
from .nodes.generate_contract_node import generate_contract_node
from .nodes.explain_contract_node import explain_contract_node


def create_unified_contract_agent() -> GraphAgent:
    """
    Create a unified contract agent that handles both chat and blocks input.
    
    Workflow:
    1. detect_input_type - Check if chat or blocks input
    2a. update_spec (if CHAT) - Extract info from chat message
    2b. parse_blocks (if BLOCKS) - Parse block graph into spec
    3. normalize_spec - Ensure consistent formatting, fill defaults
    4. validate_spec - Check for issues
    5. generate_contract - Create the full contract text
    6. explain_contract - Summarize in plain English
    """
    wf = StateGraph()
    
    # Add all nodes
    wf.add_node("detect_input", detect_input_type_node)
    wf.add_node("parse_chat", update_spec_from_message_node)
    wf.add_node("parse_blocks", parse_blocks_node)
    wf.add_node("normalize_spec", normalize_spec_node)
    wf.add_node("validate_spec", validate_spec_node)
    wf.add_node("generate_contract", generate_contract_node)
    wf.add_node("explain_contract", explain_contract_node)
    
    # Set entry point
    wf.set_entry_point("detect_input")
    
    # Route based on input type
    wf.add_conditional_edges(
        "detect_input",
        route_by_input_type,
        {
            "CHAT": "parse_chat",
            "BLOCKS": "parse_blocks",
            "NONE": "validate_spec",  # Skip to validation which will fail
        },
    )
    
    # Both parse paths lead to normalize
    wf.add_edge("parse_chat", "normalize_spec")
    wf.add_edge("parse_blocks", "normalize_spec")
    
    # Normalize → Validate → Generate → Explain
    wf.add_edge("normalize_spec", "validate_spec")
    wf.add_edge("validate_spec", "generate_contract")
    wf.add_edge("generate_contract", "explain_contract")
    
    # Compile the graph
    compiled = wf.compile()
    
    # Initial state
    initial_state = {
        # Inputs (one or the other)
        "chat_input": None,
        "blocks_input": None,
        
        # Processing state
        "input_type": None,
        "raw_input": None,
        "contract_spec": get_empty_contract_spec(),
        
        # Normalization
        "normalization_notes": [],
        
        # Validation
        "validation_result": None,
        "is_valid": False,
        "issues": [],
        "warnings": [],
        
        # Generation
        "contract_text": None,
        "summary": None,
        
        # Notes
        "parse_notes": [],
    }
    
    agent = GraphAgent(
        name="unified_contract_agent",
        description="Generates contracts from either chat prompts or visual block graphs.",
        graph=compiled,
        initial_state=initial_state,
    )
    
    return agent


async def run_from_chat(chat_input: str) -> Dict[str, Any]:
    """
    Convenience function to run the agent with chat input.
    
    Args:
        chat_input: Natural language description of the contract
        
    Returns:
        Final state with contract_text, summary, validation, etc.
    """
    agent = create_unified_contract_agent()
    agent.state["chat_input"] = chat_input
    agent.state["input"] = chat_input  # For compatibility with update_spec_node
    
    result = await agent.graph.run(agent.state)
    return result


async def run_from_blocks(blocks_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to run the agent with blocks input.
    
    Args:
        blocks_input: Block graph JSON with nodes and edges
        
    Returns:
        Final state with contract_text, summary, validation, etc.
    """
    agent = create_unified_contract_agent()
    agent.state["blocks_input"] = blocks_input
    
    result = await agent.graph.run(agent.state)
    return result


# === CHAT-BASED INTERACTIVE AGENT ===
# For the conversational flow (asks questions iteratively)

from .nodes.decide_next_step_node import decide_next_step_node, route_by_next_action
from .nodes.ask_question_node import ask_question_node


def create_chat_contract_agent() -> GraphAgent:
    """
    Create an interactive chat agent that asks questions to build a contract.
    
    This is the conversational workflow that asks follow-up questions.
    """
    wf = StateGraph()
    
    # Add all nodes
    wf.add_node("update_spec", update_spec_from_message_node)
    wf.add_node("decide_next_step", decide_next_step_node)
    wf.add_node("ask_question", ask_question_node)
    wf.add_node("normalize_spec", normalize_spec_node)
    wf.add_node("validate_spec", validate_spec_node)
    wf.add_node("generate_contract", generate_contract_node)
    wf.add_node("explain_contract", explain_contract_node)
    
    # Set the entry point
    wf.set_entry_point("update_spec")
    
    # Define edges
    wf.add_edge("update_spec", "decide_next_step")
    
    # Conditional routing based on whether we need more info
    wf.add_conditional_edges(
        "decide_next_step",
        route_by_next_action,
        {
            "ASK_MORE": "ask_question",
            "GENERATE": "normalize_spec",
        },
    )
    
    # Normalize → Validate → Generate → Explain
    wf.add_edge("normalize_spec", "validate_spec")
    wf.add_edge("validate_spec", "generate_contract")
    wf.add_edge("generate_contract", "explain_contract")
    
    # ask_question and explain_contract are terminal nodes
    
    # Compile
    compiled = wf.compile()
    
    # Initial state
    initial_state = {
        "input": None,
        "contract_spec": get_empty_contract_spec(),
        "missing_fields": None,
        "next_action": None,
        "assistant_message": None,
        "contract_text": None,
        "summary": None,
        "questions_asked": 0,
        "extraction_notes": None,
        "decision_reason": None,
        "current_question_field": None,
        "normalization_notes": [],
        "validation_result": None,
        "is_valid": False,
        "issues": [],
        "warnings": [],
    }
    
    agent = GraphAgent(
        name="chat_contract_agent",
        description="Interactive agent that gathers contract info through conversation.",
        graph=compiled,
        initial_state=initial_state,
    )
    
    return agent


def get_opening_message() -> str:
    """Get the opening message for the chat assistant."""
    return """Hi there! 👋 I am Pibble, your friendly contract assistant. 

Here's how I work: I'll ask you a few simple questions about your project, and then I'll create a comprehensive contract that protects both you and your client. I'll cover everything from payment terms to what happens if things don't go as planned.

Let's get started! Tell me a bit about what you're working on - who's your client and what will you be delivering?"""


# Backwards compatibility
def create_contract_graph_agent() -> GraphAgent:
    """Alias for create_chat_contract_agent for backwards compatibility."""
    return create_chat_contract_agent()
