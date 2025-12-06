"""
Decide Next Step Node
Determines whether to ask more questions or generate the contract.
Includes comprehensive validation of contract completeness.
"""
from typing import Dict, Any, List
from ..contract_schema import (
    calculate_missing_fields,
    is_generic_name,
    get_field_priority,
)


# Minimum fields required before we can generate a contract
MINIMUM_REQUIRED = [
    "freelancer_name",
    "client_name",
    "deliverables",
    "payment_amount",
    "deadline",
]

# Fields that make the contract robust (strongly recommended)
RECOMMENDED_FIELDS = [
    "freelancer_email",
    "client_email",
    "acceptance_criteria",
    "max_revisions",
    "late_delivery_policy",
    "non_delivery_refund",
    "dispute_method",
]


async def decide_next_step_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads: state["missing_fields"], state["contract_spec"].
    Determines if we should ask more questions or generate the contract.
    
    Decision logic:
    1. If any MINIMUM_REQUIRED fields are missing → ASK_MORE
    2. If party names are generic (not actual names) → ASK_MORE
    3. If no failure scenarios defined → ASK_MORE (at least once)
    4. Otherwise → GENERATE
    """
    missing = state.get("missing_fields") or []
    spec = state.get("contract_spec") or {}
    questions_asked = state.get("questions_asked", 0)
    
    # Accept whatever names the user gave - don't be pedantic
    freelancer = spec.get("freelancer", {}) or {}
    client = spec.get("client", {}) or {}
    
    # Check minimum required fields
    minimum_missing = [f for f in MINIMUM_REQUIRED if f in missing]
    
    # Check recommended fields for robustness
    recommended_missing = [f for f in RECOMMENDED_FIELDS if f in missing]
    
    # Decision logic
    if minimum_missing:
        # Must ask for minimum required fields
        next_action = "ASK_MORE"
        reason = f"Missing required fields: {', '.join(minimum_missing)}"
    elif recommended_missing and questions_asked < 10:
        # Should ask about recommended fields for a robust contract
        # But don't ask forever - limit to 10 questions
        next_action = "ASK_MORE"
        reason = f"Recommended fields for robust contract: {', '.join(recommended_missing[:3])}"
    else:
        # We have enough to generate
        next_action = "GENERATE"
        reason = "All required fields collected"
    
    return {
        "next_action": next_action,
        "decision_reason": reason,
        "missing_fields": missing,  # Update with any new missing fields
        "questions_asked": questions_asked,
    }


def route_by_next_action(state: Dict[str, Any]) -> str:
    """
    Routing function for conditional edges.
    Returns the next node name based on next_action.
    """
    return state.get("next_action", "ASK_MORE")


def validate_contract_completeness(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive validation of contract completeness.
    Returns validation result with details.
    """
    issues = []
    warnings = []
    
    # Check parties
    freelancer = spec.get("freelancer", {}) or {}
    client = spec.get("client", {}) or {}
    
    if not freelancer.get("name"):
        issues.append("Freelancer name is missing")
    elif is_generic_name(freelancer.get("name", "")):
        issues.append("Freelancer name is generic - need actual legal name")
    
    if not client.get("name"):
        issues.append("Client name is missing")
    elif is_generic_name(client.get("name", "")):
        issues.append("Client name is generic - need actual name/business name")
    
    if not freelancer.get("email"):
        warnings.append("Freelancer email is missing")
    
    if not client.get("email"):
        warnings.append("Client email is missing")
    
    # Check deliverables
    deliverables = spec.get("deliverables", []) or []
    if not deliverables:
        issues.append("No deliverables specified")
    
    # Check payment
    payment = spec.get("payment", {}) or {}
    if not payment.get("amount"):
        issues.append("Payment amount is missing")
    if not payment.get("currency"):
        warnings.append("Payment currency not specified")
    
    # Check timeline
    timeline = spec.get("timeline", {}) or {}
    if not timeline.get("deadline"):
        issues.append("Deadline is missing")
    
    # Check failure scenarios
    failure = spec.get("failure_scenarios", {}) or {}
    if not failure.get("late_delivery", {}).get("penalty_type"):
        warnings.append("No late delivery policy defined")
    if not failure.get("non_delivery", {}).get("refund_percentage"):
        warnings.append("No non-delivery refund policy defined")
    if not failure.get("client_rejection", {}).get("process"):
        warnings.append("No rejection/dispute process defined")
    
    # Check dispute resolution
    dispute = spec.get("dispute_resolution", {}) or {}
    if not dispute.get("method"):
        warnings.append("No dispute resolution method specified")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "can_generate": len(issues) == 0,
    }
