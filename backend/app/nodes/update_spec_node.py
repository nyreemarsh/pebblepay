"""
Update Spec Node
Extracts comprehensive contract details from user messages and updates the contract spec.
"""
import json
from typing import Dict, Any
from ..llm import llm
from ..contract_schema import (
    get_empty_contract_spec,
    calculate_missing_fields,
)


SYSTEM_PROMPT = """You are a contract information extractor. 

YOUR JOB:
1. Read what field was being asked about
2. Extract the user's answer and put it in the CORRECT field

IMPORTANT - WHO IS WHO:
- FREELANCER = the person PROVIDING the service (the user of this app)
- CLIENT = the person/business HIRING the freelancer (paying for the work)

If the field being asked was "freelancer_name" → put the answer in freelancer.name
If the field being asked was "client_name" → put the answer in client.name
DO NOT MIX THESE UP!

HANDLING RESPONSES:
- If user says "yes", "ok", "yep" → they're CONFIRMING what was asked/suggested
- If user has typos → interpret the correct word
- Accept names exactly as given

The contract spec schema:
- freelancer: {name, business_name, email, phone, address} - THE SERVICE PROVIDER
- client: {name, business_name, email, phone, address} - THE PERSON PAYING
- title: project name
- deliverables: [{item, description, format, quantity}]
- payment: {amount, currency, schedule, deposit_percentage, milestones}
- timeline: {start_date, deadline, milestones}
- quality_standards: {acceptance_criteria, revision_policy, max_revisions, approval_process}
- failure_scenarios: {...}
- dispute_resolution: {...}

Return JSON with:
{
  "updated_spec": { ... complete updated spec ... },
  "extracted_info": { ... what was extracted ... },
  "notes": ""
}

Return ONLY valid JSON."""


async def update_spec_from_message_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads: state["input"], state["contract_spec"] (may be None).
    Uses LLM to extract new details and merge into contract_spec.
    Writes: "contract_spec", "missing_fields", "extraction_notes".
    """
    user_input = state.get("input", "")
    current_spec = state.get("contract_spec") or get_empty_contract_spec()
    
    # Get conversation context
    last_assistant_message = state.get("assistant_message", "")
    current_question_field = state.get("current_question_field", "")
    
    # Tell the LLM exactly which field we were asking about
    field_hint = ""
    if current_question_field:
        if current_question_field == "freelancer_name":
            field_hint = "THE FIELD BEING ASKED: freelancer_name (the user's own name - they are the freelancer)"
        elif current_question_field == "client_name":
            field_hint = "THE FIELD BEING ASKED: client_name (the name of the person/business hiring them)"
        elif current_question_field == "freelancer_email":
            field_hint = "THE FIELD BEING ASKED: freelancer_email (the user's own email)"
        elif current_question_field == "client_email":
            field_hint = "THE FIELD BEING ASKED: client_email (the client's email)"
        else:
            field_hint = f"THE FIELD BEING ASKED: {current_question_field}"
    
    prompt = f"""Current contract spec:
{json.dumps(current_spec, indent=2, default=str)}

{field_hint}

CONVERSATION:
Assistant asked: "{last_assistant_message}"
User replied: "{user_input}"

The user is answering the assistant's question.
Put their answer in the CORRECT field based on what was being asked.
- freelancer = the person providing the service (the app user)
- client = the person paying for the work

Return the updated spec with the new information."""

    try:
        result = await llm.chat_json(prompt, system_prompt=SYSTEM_PROMPT)
        
        updated_spec = result.get("updated_spec", current_spec)
        extraction_notes = result.get("notes", "")
        
        # Ensure we have the basic structure
        if not updated_spec:
            updated_spec = get_empty_contract_spec()
        
        # Ensure all required nested structures exist
        updated_spec = ensure_spec_structure(updated_spec)
        
        # Calculate what's still missing
        missing_fields = calculate_missing_fields(updated_spec)
        
        return {
            "contract_spec": updated_spec,
            "missing_fields": missing_fields,
            "extraction_notes": extraction_notes,
        }
    
    except Exception as e:
        print(f"[update_spec_node] Error: {e}")
        # Return current state with full missing fields on error
        missing_fields = calculate_missing_fields(current_spec)
        return {
            "contract_spec": current_spec,
            "missing_fields": missing_fields,
            "extraction_notes": f"Error during extraction: {str(e)}",
        }


def ensure_spec_structure(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all required nested structures exist in the spec."""
    template = get_empty_contract_spec()
    
    # Merge with template to ensure all keys exist
    def deep_merge(base: dict, override: dict) -> dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            elif value is not None:
                result[key] = value
        return result
    
    return deep_merge(template, spec)
