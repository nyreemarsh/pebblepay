"""
Detect Input Type Node
Determines whether the input is chat-based or blocks-based and routes accordingly.
"""
from typing import Dict, Any


async def detect_input_type_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads: state["chat_input"], state["blocks_input"]
    Determines the input type and sets up for the appropriate parsing path.
    Writes: "input_type", "raw_input"
    """
    chat_input = state.get("chat_input")
    blocks_input = state.get("blocks_input")
    
    if blocks_input and isinstance(blocks_input, dict):
        # Blocks-based input (from visual builder)
        return {
            "input_type": "BLOCKS",
            "raw_input": blocks_input,
        }
    elif chat_input and isinstance(chat_input, str) and chat_input.strip():
        # Chat-based input (natural language)
        return {
            "input_type": "CHAT",
            "raw_input": chat_input.strip(),
        }
    else:
        # No valid input
        return {
            "input_type": "NONE",
            "raw_input": None,
            "_error": "No valid input provided. Provide either chat_input (str) or blocks_input (dict).",
        }


def route_by_input_type(state: Dict[str, Any]) -> str:
    """
    Routing function for conditional edges.
    Returns the next node name based on input_type.
    """
    input_type = state.get("input_type", "NONE")
    return input_type

