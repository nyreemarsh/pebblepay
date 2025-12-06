"""
Normalize Spec Node
Ensures contract spec has consistent formatting, defaults, and structure.
"""
from typing import Dict, Any
from datetime import datetime, timedelta
import re
from ..contract_schema import get_empty_contract_spec


async def normalize_spec_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads: state["contract_spec"]
    Normalizes the spec: fills defaults, formats dates, validates structure.
    Writes: "contract_spec", "normalization_notes"
    """
    spec = state.get("contract_spec") or get_empty_contract_spec()
    notes = []
    
    # Ensure all required nested structures exist
    spec = ensure_structure(spec)
    
    # Normalize dates
    spec, date_notes = normalize_dates(spec)
    notes.extend(date_notes)
    
    # Normalize payment
    spec, payment_notes = normalize_payment(spec)
    notes.extend(payment_notes)
    
    # Normalize quality standards with defaults
    spec, quality_notes = normalize_quality(spec)
    notes.extend(quality_notes)
    
    # Normalize failure scenarios with sensible defaults
    spec, failure_notes = normalize_failure_scenarios(spec)
    notes.extend(failure_notes)
    
    # Normalize dispute resolution
    spec, dispute_notes = normalize_dispute(spec)
    notes.extend(dispute_notes)
    
    # Generate title if missing
    if not spec.get("title"):
        spec["title"] = generate_title(spec)
        notes.append(f"Generated title: {spec['title']}")
    
    return {
        "contract_spec": spec,
        "normalization_notes": notes,
    }


def ensure_structure(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all required nested structures exist."""
    template = get_empty_contract_spec()
    
    def deep_merge(base: dict, override: dict) -> dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            elif value is not None:
                result[key] = value
        return result
    
    return deep_merge(template, spec)


def normalize_dates(spec: Dict[str, Any]) -> tuple:
    """Normalize date fields to consistent format."""
    notes = []
    timeline = spec.get("timeline", {}) or {}
    today = datetime.now()
    
    # Parse relative dates like "2 weeks" or "in 2 weeks"
    deadline = timeline.get("deadline")
    if deadline and isinstance(deadline, str):
        normalized = parse_relative_date(deadline, today)
        if normalized != deadline:
            timeline["deadline"] = normalized
            notes.append(f"Normalized deadline: '{deadline}' → '{normalized}'")
    
    start_date = timeline.get("start_date")
    if start_date and isinstance(start_date, str):
        normalized = parse_relative_date(start_date, today)
        if normalized != start_date:
            timeline["start_date"] = normalized
            notes.append(f"Normalized start date: '{start_date}' → '{normalized}'")
    
    # Set default start date to today if not specified
    if not timeline.get("start_date"):
        timeline["start_date"] = today.strftime("%B %d, %Y")
        notes.append(f"Set default start date: {timeline['start_date']}")
    
    spec["timeline"] = timeline
    return spec, notes


def parse_relative_date(date_str: str, today: datetime) -> str:
    """Parse relative date strings into actual dates."""
    date_lower = date_str.lower().strip()
    
    # Match patterns like "2 weeks", "in 2 weeks", "1 month"
    patterns = [
        (r"(?:in\s+)?(\d+)\s*weeks?", lambda m: today + timedelta(weeks=int(m.group(1)))),
        (r"(?:in\s+)?(\d+)\s*days?", lambda m: today + timedelta(days=int(m.group(1)))),
        (r"(?:in\s+)?(\d+)\s*months?", lambda m: today + timedelta(days=int(m.group(1)) * 30)),
        (r"next\s+week", lambda m: today + timedelta(weeks=1)),
        (r"end\s+of\s+(?:this\s+)?month", lambda m: (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)),
    ]
    
    for pattern, calc_date in patterns:
        match = re.match(pattern, date_lower)
        if match:
            result_date = calc_date(match)
            return result_date.strftime("%B %d, %Y")
    
    # Return as-is if no pattern matched
    return date_str


def normalize_payment(spec: Dict[str, Any]) -> tuple:
    """Normalize payment information."""
    notes = []
    payment = spec.get("payment", {}) or {}
    
    # Extract currency from amount if combined (e.g., "$500", "£300")
    amount = payment.get("amount")
    if amount and isinstance(amount, str):
        # Try to extract currency symbol
        currency_match = re.match(r"([£$€])?\s*([\d,]+(?:\.\d{2})?)\s*([A-Z]{3})?", amount.strip())
        if currency_match:
            symbol, number, code = currency_match.groups()
            payment["amount"] = float(number.replace(",", ""))
            if symbol and not payment.get("currency"):
                currency_map = {"$": "USD", "£": "GBP", "€": "EUR"}
                payment["currency"] = currency_map.get(symbol, symbol)
                notes.append(f"Extracted currency: {payment['currency']}")
            elif code and not payment.get("currency"):
                payment["currency"] = code
    
    # Default currency
    if not payment.get("currency"):
        payment["currency"] = "USD"
        notes.append("Set default currency: USD")
    
    # Default payment schedule
    if not payment.get("schedule"):
        payment["schedule"] = "50% upfront, 50% on completion"
        notes.append("Set default payment schedule: 50/50")
    
    spec["payment"] = payment
    return spec, notes


def normalize_quality(spec: Dict[str, Any]) -> tuple:
    """Normalize quality standards with sensible defaults."""
    notes = []
    quality = spec.get("quality_standards", {}) or {}
    
    # Default max revisions
    if quality.get("max_revisions") is None:
        quality["max_revisions"] = 2
        notes.append("Set default revisions: 2 rounds")
    
    # Handle "unlimited" revisions
    if quality.get("max_revisions") in ["unlimited", "Unlimited", "UNLIMITED"]:
        quality["max_revisions"] = "unlimited"
    
    # Default approval process
    if not quality.get("approval_process"):
        quality["approval_process"] = "Client has 5 business days to review and approve each deliverable"
    
    spec["quality_standards"] = quality
    return spec, notes


def normalize_failure_scenarios(spec: Dict[str, Any]) -> tuple:
    """Normalize failure scenarios with sensible defaults."""
    notes = []
    failure = spec.get("failure_scenarios", {}) or {}
    
    # Late delivery defaults
    late = failure.get("late_delivery", {}) or {}
    if not late.get("penalty_type"):
        late["penalty_type"] = "none"
        late["grace_period_days"] = 3
        notes.append("Set default late policy: no penalty with 3-day grace period")
    failure["late_delivery"] = late
    
    # Non-delivery defaults
    non_del = failure.get("non_delivery", {}) or {}
    if non_del.get("refund_percentage") is None:
        non_del["refund_percentage"] = 100
        notes.append("Set default non-delivery refund: 100%")
    failure["non_delivery"] = non_del
    
    # Client rejection defaults
    rejection = failure.get("client_rejection", {}) or {}
    if not rejection.get("process"):
        rejection["process"] = "Discussion and one additional revision attempt, then mediation if unresolved"
        notes.append("Set default rejection process")
    failure["client_rejection"] = rejection
    
    # Cancellation defaults
    f_cancel = failure.get("freelancer_cancellation", {}) or {}
    if not f_cancel.get("refund_policy"):
        f_cancel["refund_policy"] = "Full refund of unused deposit"
    failure["freelancer_cancellation"] = f_cancel
    
    c_cancel = failure.get("client_cancellation", {}) or {}
    if c_cancel.get("kill_fee_percentage") is None:
        c_cancel["kill_fee_percentage"] = 25
        notes.append("Set default kill fee: 25%")
    failure["client_cancellation"] = c_cancel
    
    spec["failure_scenarios"] = failure
    return spec, notes


def normalize_dispute(spec: Dict[str, Any]) -> tuple:
    """Normalize dispute resolution with defaults."""
    notes = []
    dispute = spec.get("dispute_resolution", {}) or {}
    
    if not dispute.get("method"):
        dispute["method"] = "negotiation, then mediation, then small claims court"
        notes.append("Set default dispute method: negotiation → mediation → court")
    
    if not dispute.get("process"):
        dispute["process"] = (
            "1. Direct discussion between parties (7 days)\n"
            "2. Written mediation request if unresolved\n"
            "3. Mediation with agreed third party\n"
            "4. Small claims court as last resort"
        )
    
    spec["dispute_resolution"] = dispute
    return spec, notes


def generate_title(spec: Dict[str, Any]) -> str:
    """Generate a contract title from available info."""
    client = spec.get("client", {}) or {}
    deliverables = spec.get("deliverables", []) or []
    
    client_name = client.get("name", "")
    
    if deliverables:
        first = deliverables[0]
        item = first.get("item", "") if isinstance(first, dict) else str(first)
        if item and client_name:
            return f"{item} Agreement - {client_name}"
        elif item:
            return f"{item} Service Agreement"
    
    if client_name:
        return f"Service Agreement - {client_name}"
    
    return "Freelance Service Agreement"

