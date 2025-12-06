"""
Contract Specification Schema
Defines the comprehensive structure for contract information.
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class PaymentSchedule(str, Enum):
    UPFRONT = "upfront"
    ON_COMPLETION = "on_completion"
    MILESTONE = "milestone"
    SPLIT = "split"  # e.g., 50% upfront, 50% on completion


class DisputeMethod(str, Enum):
    MEDIATION = "mediation"
    ARBITRATION = "arbitration"
    COURT = "court"
    NEGOTIATION = "negotiation"


# Required fields that must have actual values (not generic placeholders)
REQUIRED_FIELDS = [
    "freelancer_name",
    "client_name", 
    "freelancer_email",
    "client_email",
    "deliverables",
    "payment_amount",
    "deadline",
    "quality_standards",
    "failure_scenarios",
    "dispute_resolution",
]

# Fields where generic terms like "Designer", "Client", "Café" are not acceptable
NAME_FIELDS = ["freelancer_name", "client_name", "freelancer_business", "client_business"]

# Generic terms that should be replaced with actual names
GENERIC_TERMS = [
    "designer", "client", "freelancer", "café", "cafe", "customer",
    "the client", "the designer", "the freelancer", "company", "business",
    "buyer", "seller", "contractor", "vendor", "provider"
]


def is_generic_name(name: str) -> bool:
    """Check if a name is a generic placeholder rather than an actual name."""
    if not name:
        return True
    # Be lenient - accept most names. Only reject very generic single words.
    name_lower = name.lower().strip()
    very_generic = ["client", "freelancer", "designer", "customer"]
    return name_lower in very_generic and " " not in name_lower


def get_empty_contract_spec() -> Dict[str, Any]:
    """Return an empty contract specification with all fields initialized."""
    return {
        "title": None,
        
        # Freelancer (service provider) details
        "freelancer": {
            "name": None,  # Full legal name
            "business_name": None,  # Optional business/trading name
            "email": None,
            "phone": None,
            "address": None,
        },
        
        # Client (customer) details
        "client": {
            "name": None,  # Full legal name or business name
            "business_name": None,  # Optional secondary business name
            "email": None,
            "phone": None,
            "address": None,
        },
        
        # What will be delivered
        "deliverables": [],  # List of {item, description, format, quantity}
        
        # Payment terms
        "payment": {
            "amount": None,
            "currency": None,
            "schedule": None,  # upfront, on_completion, milestone, split
            "deposit_percentage": None,  # e.g., 50 for 50% upfront
            "milestones": [],  # List of {description, amount, due_date}
        },
        
        # Timeline
        "timeline": {
            "start_date": None,
            "deadline": None,
            "milestones": [],  # List of {description, date}
        },
        
        # Quality and acceptance criteria
        "quality_standards": {
            "acceptance_criteria": [],  # What constitutes acceptable work
            "revision_policy": None,  # How revisions work
            "max_revisions": None,  # Number of included revisions
            "approval_process": None,  # How client approves work
        },
        
        # What happens when things go wrong
        "failure_scenarios": {
            "late_delivery": {
                "penalty_type": None,  # "percentage", "daily_fee", "none"
                "penalty_amount": None,
                "grace_period_days": None,
            },
            "non_delivery": {
                "refund_percentage": None,
                "conditions": [],
            },
            "client_rejection": {
                "process": None,  # What happens if client rejects final work
                "refund_policy": None,
            },
            "freelancer_cancellation": {
                "refund_policy": None,
                "notice_period_days": None,
            },
            "client_cancellation": {
                "refund_policy": None,
                "kill_fee_percentage": None,  # Fee for work done
            },
        },
        
        # How disputes are handled
        "dispute_resolution": {
            "method": None,  # mediation, arbitration, court, negotiation
            "location": None,  # Jurisdiction
            "process": None,  # Description of steps
            "governing_law": None,  # Which country/state law applies
        },
        
        # Liability limitations
        "liability": {
            "max_liability": None,  # Usually limited to contract value
            "exclusions": [],  # What's not covered
            "insurance_required": False,
        },
        
        # Additional terms
        "special_terms": [],
        
        # Intellectual property
        "ip_ownership": {
            "final_work": None,  # "client" or "freelancer" or "shared"
            "transfer_on": None,  # "full_payment", "delivery", etc.
            "portfolio_rights": True,  # Can freelancer show in portfolio
        },
        
        # Confidentiality
        "confidentiality": {
            "required": False,
            "duration": None,  # How long confidentiality lasts
            "scope": None,  # What's confidential
        },
    }


def calculate_missing_fields(spec: Dict[str, Any]) -> List[str]:
    """
    Calculate which required fields are still missing.
    Returns a list of field identifiers with priority ordering.
    """
    missing = []
    
    # Priority 1: Party names - just check if they exist, accept whatever they gave
    freelancer = spec.get("freelancer", {}) or {}
    client = spec.get("client", {}) or {}
    
    if not freelancer.get("name"):
        missing.append("freelancer_name")
    
    if not client.get("name"):
        missing.append("client_name")
    
    # Priority 2: Contact information
    if not freelancer.get("email"):
        missing.append("freelancer_email")
    
    if not client.get("email"):
        missing.append("client_email")
    
    # Priority 3: Project basics
    if not spec.get("title"):
        missing.append("title")
    
    deliverables = spec.get("deliverables", []) or []
    if not deliverables or len(deliverables) == 0:
        missing.append("deliverables")
    
    # Priority 4: Payment
    payment = spec.get("payment", {}) or {}
    if not payment.get("amount"):
        missing.append("payment_amount")
    if not payment.get("currency"):
        missing.append("payment_currency")
    if not payment.get("schedule"):
        missing.append("payment_schedule")
    
    # Priority 5: Timeline
    timeline = spec.get("timeline", {}) or {}
    if not timeline.get("deadline"):
        missing.append("deadline")
    
    # Priority 6: Quality standards
    quality = spec.get("quality_standards", {}) or {}
    if not quality.get("acceptance_criteria") or len(quality.get("acceptance_criteria", [])) == 0:
        missing.append("acceptance_criteria")
    if quality.get("max_revisions") is None:
        missing.append("max_revisions")
    
    # Priority 7: Failure scenarios (critical for robustness)
    failure = spec.get("failure_scenarios", {}) or {}
    
    late_delivery = failure.get("late_delivery", {}) or {}
    if late_delivery.get("penalty_type") is None:
        missing.append("late_delivery_policy")
    
    non_delivery = failure.get("non_delivery", {}) or {}
    if non_delivery.get("refund_percentage") is None:
        missing.append("non_delivery_refund")
    
    client_rejection = failure.get("client_rejection", {}) or {}
    if not client_rejection.get("process"):
        missing.append("rejection_process")
    
    # Priority 8: Dispute resolution
    dispute = spec.get("dispute_resolution", {}) or {}
    if not dispute.get("method"):
        missing.append("dispute_method")
    
    return missing


def get_field_question(field: str) -> str:
    """Get a user-friendly question for a specific missing field."""
    questions = {
        # Party names
        "freelancer_name": "What's your full legal name (or your business name if you're a company)?",
        "client_name": "What's your client's full name or their business name?",
        "freelancer_email": "What's your email address for this contract?",
        "client_email": "What's your client's email address?",
        
        # Project basics
        "title": "What would you like to call this project or contract?",
        "deliverables": "What exactly will you be delivering? (Be specific about formats, quantities, etc.)",
        
        # Payment
        "payment_amount": "How much will you be paid for this work?",
        "payment_currency": "What currency will you be paid in?",
        "payment_schedule": "How will payment be structured? (e.g., 50% upfront and 50% on completion, or all at the end?)",
        
        # Timeline
        "deadline": "When does this work need to be completed by?",
        
        # Quality
        "acceptance_criteria": "How will the client know the work is acceptable? What are the quality standards?",
        "max_revisions": "How many rounds of revisions are included in this price?",
        
        # Failure scenarios
        "late_delivery_policy": "What happens if you deliver late? Should there be a penalty, grace period, or no penalty?",
        "non_delivery_refund": "If you can't complete the work at all, what percentage should be refunded?",
        "rejection_process": "What happens if the client isn't happy with the final work after all revisions are used?",
        
        # Dispute
        "dispute_method": "If there's a disagreement, how should it be resolved? (e.g., discuss first, then mediation, or go straight to small claims court?)",
    }
    return questions.get(field, f"Could you tell me more about {field.replace('_', ' ')}?")


def get_field_priority(field: str) -> int:
    """Get priority level for a field (lower = higher priority)."""
    priorities = {
        "freelancer_name": 1,
        "client_name": 1,
        "freelancer_email": 2,
        "client_email": 2,
        "title": 3,
        "deliverables": 3,
        "payment_amount": 4,
        "payment_currency": 4,
        "payment_schedule": 4,
        "deadline": 5,
        "acceptance_criteria": 6,
        "max_revisions": 6,
        "late_delivery_policy": 7,
        "non_delivery_refund": 7,
        "rejection_process": 7,
        "dispute_method": 8,
    }
    return priorities.get(field, 10)

