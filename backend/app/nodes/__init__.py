"""
Contract Assistant Nodes
Each node handles a specific step in the contract generation workflow.
"""
from .detect_input_node import detect_input_type_node, route_by_input_type
from .update_spec_node import update_spec_from_message_node
from .parse_blocks_node import parse_blocks_node
from .normalize_spec_node import normalize_spec_node
from .validate_spec_node import validate_spec_node, format_validation_report
from .decide_next_step_node import decide_next_step_node, route_by_next_action
from .ask_question_node import ask_question_node
from .generate_contract_node import generate_contract_node
from .explain_contract_node import explain_contract_node

__all__ = [
    # Input detection
    "detect_input_type_node",
    "route_by_input_type",
    # Parsing
    "update_spec_from_message_node",
    "parse_blocks_node",
    # Processing
    "normalize_spec_node",
    "validate_spec_node",
    "format_validation_report",
    # Decision
    "decide_next_step_node",
    "route_by_next_action",
    "ask_question_node",
    # Generation
    "generate_contract_node",
    "explain_contract_node",
]
