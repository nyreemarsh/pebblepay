"""
Ask Question Node
Generates intelligent, contextual follow-up questions to gather missing contract details.
Uses priority-based questioning and follows up on vague answers.
"""
import json
from typing import Dict, Any, List
from ..llm import llm
from ..contract_schema import (
    get_field_question,
    get_field_priority,
    is_generic_name,
    calculate_missing_fields,
)


SYSTEM_PROMPT = """You are Pibble, a friendly and warm contract assistant helping a freelancer create a contract.

IMPORTANT - BE CONVERSATIONAL:
1. FIRST: Briefly acknowledge what the user just told you (e.g., "Great!", "Got it!", "Perfect!")
2. THEN: Ask your next question

IMPORTANT - WHO IS WHO:
- The USER is the FREELANCER (the person providing the service)
- The CLIENT is the person/business HIRING the freelancer

EXAMPLES OF GOOD RESPONSES:
- "Great, nice to meet you Sarah! Now, who's the client you'll be working with?"
- "Got it - a logo design project! Who's the lucky client?"
- "Perfect, £500 it is! When do you need to have this finished by?"
- "Sounds good! How many rounds of revisions do you want to include?"

RULES:
- Be warm, friendly, encouraging
- Keep it brief but personal
- Ask ONE clear question
- Be clear about freelancer vs client when asking for names/emails

Return the full response (acknowledgment + question)."""


QUESTION_TEMPLATES = {
    # Party information - highest priority
    "freelancer_name": {
        "question": "First things first - what's your name?",
        "context": "The freelancer's own name"
    },
    "client_name": {
        "question": "Who's the client you'll be working with?",
        "context": "The person/business hiring them"
    },
    # Project title
    "title": {
        "question": "What should we call this project?",
        "context": "Suggest a name like '[Deliverable] for [Client]' based on what we know"
    },
    "freelancer_email": {
        "question": "What's your email for the contract?",
        "context": "The freelancer's own email"
    },
    "client_email": {
        "question": "What's your client's email?",
        "context": "Where the client will receive the contract"
    },
    
    # Deliverables
    "deliverables": {
        "question": "What will you be delivering? (files, formats, etc.)",
        "context": ""
    },
    
    # Payment
    "payment_amount": {
        "question": "How much are you charging for this?",
        "context": ""
    },
    "payment_currency": {
        "question": "What currency?",
        "context": ""
    },
    "payment_schedule": {
        "question": "How do you want to split the payment? (e.g., 50% upfront, 50% on completion)",
        "context": ""
    },
    
    # Timeline
    "deadline": {
        "question": "When do you need to have this done by?",
        "context": ""
    },
    
    # Quality standards
    "acceptance_criteria": {
        "question": "How will the client know the work is done right?",
        "context": "Helps prevent disagreements"
    },
    "max_revisions": {
        "question": "How many revision rounds are included?",
        "context": ""
    },
    
    # Failure scenarios
    "late_delivery_policy": {
        "question": "What if you deliver late - any penalty or just communicate?",
        "context": "Sets clear expectations"
    },
    "non_delivery_refund": {
        "question": "If you can't complete the work, what refund would you offer? (most say 100%)",
        "context": "Rarely happens but good to have"
    },
    "rejection_process": {
        "question": "What if the client isn't happy after all revisions - partial refund or mediation?",
        "context": "Prevents messy disputes"
    },
    
    # Dispute resolution
    "dispute_method": {
        "question": "Last one! If there's a disagreement you can't resolve - mediation, arbitration, or court?",
        "context": "Hopefully never needed!"
    },
}


async def ask_question_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads: state["contract_spec"], state["missing_fields"].
    Generates ONE intelligent follow-up question.
    Writes: "assistant_message", "questions_asked".
    """
    contract_spec = state.get("contract_spec") or {}
    missing_fields = state.get("missing_fields") or []
    questions_asked = state.get("questions_asked", 0)
    last_input = state.get("input", "")
    
    # Sort missing fields by priority
    sorted_missing = sorted(missing_fields, key=get_field_priority)
    
    if not sorted_missing:
        # No missing fields - this shouldn't happen, but handle gracefully
        return {
            "assistant_message": "I think we have everything we need! Let me generate your contract.",
            "questions_asked": questions_asked,
        }
    
    # Get the highest priority missing field
    target_field = sorted_missing[0]
    
    # Check if we need to follow up on a generic name
    needs_name_clarification = check_generic_name_issue(contract_spec, target_field, last_input)
    
    # Try to generate a smart question
    try:
        question = await generate_smart_question(
            contract_spec, 
            target_field, 
            sorted_missing,
            needs_name_clarification,
            last_input
        )
    except Exception as e:
        print(f"[ask_question_node] LLM error: {e}")
        # Fallback to template question
        question = get_fallback_question(target_field, needs_name_clarification, contract_spec)
    
    return {
        "assistant_message": question,
        "questions_asked": questions_asked + 1,
        "current_question_field": target_field,
    }


def check_generic_name_issue(spec: Dict[str, Any], field: str, last_input: str) -> bool:
    """Check if we need to ask for clarification on a generic name."""
    # Be less strict - accept most names
    return False


def generate_title_suggestion(spec: Dict[str, Any]) -> str:
    """Generate a suggested project title based on known info."""
    client = spec.get("client", {}) or {}
    deliverables = spec.get("deliverables", []) or []
    
    client_name = client.get("name", "")
    
    # Get the first deliverable
    deliverable = ""
    if deliverables:
        first = deliverables[0]
        if isinstance(first, dict):
            deliverable = first.get("item", "")
        else:
            deliverable = str(first)
    
    # Generate a suggestion
    if client_name and deliverable:
        # "Logo Design for Adam Smith" or "Adam Smith Commission"
        return f"{deliverable.title()} for {client_name}"
    elif client_name:
        return f"{client_name} Commission"
    elif deliverable:
        return f"{deliverable.title()} Project"
    
    return ""


async def generate_smart_question(
    spec: Dict[str, Any],
    target_field: str,
    all_missing: List[str],
    needs_clarification: bool,
    last_input: str
) -> str:
    """Generate a context-aware question using the LLM."""
    
    # Build context about what we already know
    context_parts = []
    
    freelancer = spec.get("freelancer", {}) or {}
    client = spec.get("client", {}) or {}
    
    if freelancer.get("name"):
        context_parts.append(f"Freelancer: {freelancer['name']}")
    if client.get("name"):
        context_parts.append(f"Client: {client['name']}")
    if spec.get("deliverables"):
        items = [d.get("item", d) if isinstance(d, dict) else d for d in spec["deliverables"]]
        context_parts.append(f"Deliverables: {', '.join(str(i) for i in items[:3])}")
    if spec.get("payment", {}).get("amount"):
        context_parts.append(f"Payment: {spec['payment']['amount']} {spec['payment'].get('currency', '')}")
    if spec.get("timeline", {}).get("deadline"):
        context_parts.append(f"Deadline: {spec['timeline']['deadline']}")
    
    context = "\n".join(context_parts) if context_parts else "Just starting - no details yet"
    
    # Get the template for this field
    template = QUESTION_TEMPLATES.get(target_field, {})
    base_question = template.get("question", get_field_question(target_field))
    extra_context = template.get("context", "")
    
    # Special handling for title - suggest one!
    if target_field == "title":
        suggested_title = generate_title_suggestion(spec)
        if suggested_title:
            base_question = f"How about calling this '{suggested_title}'? Or pick your own name."
            extra_context = ""
    
    # Handle generic name clarification (but be less aggressive about it)
    if needs_clarification and target_field in ["freelancer_name", "client_name"]:
        # Just ask once, don't be pushy
        pass  # Use the default question
    
    prompt = f"""Current contract info:
{context}

User just said: "{last_input}"

Next question needed about: {target_field}
Suggested question: {base_question}

Generate a FRIENDLY response that:
1. FIRST - Briefly acknowledge/react to what they just said (be warm! use their name if you know it)
2. THEN - Ask about {target_field}

Examples:
- "Nice to meet you, [name]! Now, who's the client you'll be working with?"
- "A logo design, nice! Who's the lucky client?"
- "Got it! And how much are you charging for this?"

Keep it casual and friendly. One response with acknowledgment + question."""

    response = await llm.chat(prompt, system_prompt=SYSTEM_PROMPT)
    return response.strip()


def get_fallback_question(field: str, needs_clarification: bool, spec: Dict[str, Any]) -> str:
    """Get a fallback question when LLM fails."""
    template = QUESTION_TEMPLATES.get(field, {})
    freelancer = spec.get("freelancer", {}) or {}
    freelancer_name = freelancer.get("name", "")
    
    # Add a friendly prefix based on context
    prefix = ""
    if freelancer_name:
        prefix = f"Great stuff, {freelancer_name}! "
    else:
        prefix = "Got it! "
    
    if needs_clarification:
        if field == "client_name":
            return f"{prefix}Now, who's the client you'll be working with?"
        elif field == "freelancer_name":
            return "Let's start with the basics - what's your name?"
    
    if "question" in template:
        return prefix + template["question"]
    
    return prefix + get_field_question(field)
