"""
Validate Spec Node
Validates the contract spec and produces a list of issues/warnings.
"""
from typing import Dict, Any, List
from ..contract_schema import calculate_missing_fields, is_generic_name


async def validate_spec_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads: state["contract_spec"]
    Validates the spec and identifies any issues.
    Writes: "validation_result", "is_valid", "issues", "warnings"
    """
    spec = state.get("contract_spec") or {}
    
    issues = []  # Blocking issues
    warnings = []  # Non-blocking warnings
    
    # === PARTY VALIDATION ===
    freelancer = spec.get("freelancer", {}) or {}
    client = spec.get("client", {}) or {}
    
    if not freelancer.get("name"):
        issues.append("Freelancer name is required")
    elif is_generic_name(freelancer.get("name", "")):
        warnings.append(f"Freelancer name '{freelancer['name']}' seems generic")
    
    if not client.get("name"):
        issues.append("Client name is required")
    elif is_generic_name(client.get("name", "")):
        warnings.append(f"Client name '{client['name']}' seems generic")
    
    if not freelancer.get("email"):
        warnings.append("Freelancer email is recommended for official correspondence")
    
    if not client.get("email"):
        warnings.append("Client email is recommended for official correspondence")
    
    # === DELIVERABLES VALIDATION ===
    deliverables = spec.get("deliverables", []) or []
    if not deliverables:
        issues.append("At least one deliverable must be specified")
    else:
        for i, d in enumerate(deliverables):
            if isinstance(d, dict):
                if not d.get("item"):
                    issues.append(f"Deliverable {i+1} is missing an item name")
            elif not d:
                issues.append(f"Deliverable {i+1} is empty")
    
    # === PAYMENT VALIDATION ===
    payment = spec.get("payment", {}) or {}
    if not payment.get("amount"):
        issues.append("Payment amount is required")
    elif isinstance(payment.get("amount"), (int, float)) and payment["amount"] <= 0:
        issues.append("Payment amount must be greater than 0")
    
    if not payment.get("currency"):
        warnings.append("Currency not specified, defaulting to USD")
    
    if not payment.get("schedule"):
        warnings.append("Payment schedule not specified")
    
    # === TIMELINE VALIDATION ===
    timeline = spec.get("timeline", {}) or {}
    if not timeline.get("deadline"):
        issues.append("Project deadline is required")
    
    # === QUALITY STANDARDS VALIDATION ===
    quality = spec.get("quality_standards", {}) or {}
    if quality.get("max_revisions") is None:
        warnings.append("Number of revisions not specified, defaulting to 2")
    
    # === FAILURE SCENARIOS VALIDATION ===
    failure = spec.get("failure_scenarios", {}) or {}
    
    late = failure.get("late_delivery", {}) or {}
    if not late.get("penalty_type"):
        warnings.append("Late delivery policy not specified")
    
    non_del = failure.get("non_delivery", {}) or {}
    if non_del.get("refund_percentage") is None:
        warnings.append("Non-delivery refund not specified")
    
    rejection = failure.get("client_rejection", {}) or {}
    if not rejection.get("process"):
        warnings.append("Client rejection process not specified")
    
    # === DISPUTE RESOLUTION VALIDATION ===
    dispute = spec.get("dispute_resolution", {}) or {}
    if not dispute.get("method"):
        warnings.append("Dispute resolution method not specified")
    
    # === RESULT ===
    is_valid = len(issues) == 0
    
    validation_result = {
        "is_valid": is_valid,
        "issues": issues,
        "warnings": warnings,
        "can_generate": is_valid,
        "issue_count": len(issues),
        "warning_count": len(warnings),
    }
    
    return {
        "validation_result": validation_result,
        "is_valid": is_valid,
        "issues": issues,
        "warnings": warnings,
    }


def format_validation_report(validation_result: Dict[str, Any]) -> str:
    """Format validation result as a readable report."""
    lines = []
    
    if validation_result["is_valid"]:
        lines.append("✅ Contract specification is valid!")
    else:
        lines.append("❌ Contract specification has issues:")
    
    issues = validation_result.get("issues", [])
    if issues:
        lines.append("\n🚫 BLOCKING ISSUES:")
        for issue in issues:
            lines.append(f"   • {issue}")
    
    warnings = validation_result.get("warnings", [])
    if warnings:
        lines.append("\n⚠️ WARNINGS:")
        for warning in warnings:
            lines.append(f"   • {warning}")
    
    if validation_result["is_valid"]:
        lines.append("\n✨ Ready to generate contract!")
    else:
        lines.append(f"\n📋 Fix {len(issues)} issue(s) before generating.")
    
    return "\n".join(lines)

