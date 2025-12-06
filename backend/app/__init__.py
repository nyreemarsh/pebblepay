"""
Contract Assistant Backend
A multi-agent system for creating robust freelance contracts.

Supports two input modes:
1. Chat input: Natural language description of contract
2. Blocks input: Visual graph JSON from block builder

Usage:
    # One-shot generation from chat
    from app import run_from_chat
    result = await run_from_chat("I'm a designer making a logo for...")
    
    # One-shot generation from blocks
    from app import run_from_blocks
    result = await run_from_blocks({"nodes": [...], "edges": [...]})
    
    # Interactive chat agent (asks questions)
    from app import create_chat_contract_agent
    agent = create_chat_contract_agent()
    result = await agent.run("user message")
"""
from .graph_workflow import (
    create_unified_contract_agent,
    create_chat_contract_agent,
    create_contract_graph_agent,  # Backwards compat
    run_from_chat,
    run_from_blocks,
    get_opening_message,
)
from .contract_schema import get_empty_contract_spec, calculate_missing_fields
from .state_graph import StateGraph, GraphAgent
from .llm import llm

__all__ = [
    # Main functions
    "run_from_chat",
    "run_from_blocks",
    "create_unified_contract_agent",
    "create_chat_contract_agent",
    "create_contract_graph_agent",
    "get_opening_message",
    # Schema
    "get_empty_contract_spec",
    "calculate_missing_fields",
    # Core
    "StateGraph",
    "GraphAgent",
    "llm",
]
