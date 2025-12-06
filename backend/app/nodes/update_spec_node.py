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
3. CLEAN UP and FORMAT the extracted information properly

IMPORTANT - WHO IS WHO:
- FREELANCER = the person PROVIDING the service (the user of this app)
- CLIENT = the person/business HIRING the freelancer (paying for the work)

If the field being asked was "freelancer_name" → put the answer in freelancer.name
If the field being asked was "client_name" → put the answer in client.name
DO NOT MIX THESE UP!

FORMATTING RULES (VERY IMPORTANT):
1. NAMES: Always capitalize properly (Title Case)
   - "john smith" → "John Smith"
   - "JANE DOE" → "Jane Doe"
   - "mcdonald" → "McDonald"
   - "o'brien" → "O'Brien"
   
2. BUSINESS NAMES: Capitalize properly
   - "acme corp" → "Acme Corp"
   - "tech solutions ltd" → "Tech Solutions Ltd"

3. DELIVERABLES & WORK DESCRIPTIONS: Fix grammar and capitalize properly
   - "building a website" → "Building a website"
   - "logo desgn" → "Logo design"
   - "i will make an app" → "Mobile application development"
   - Make descriptions professional and clear
   - Fix spelling errors
   - Use proper sentence case

4. PROJECT TITLES: Make them professional
   - "website for john" → "Website Development Project"
   - "logo work" → "Logo Design Project"

HANDLING RESPONSES:
- If user says "yes", "ok", "yep" → they're CONFIRMING what was asked/suggested
- If user has typos → FIX the typos and use the correct spelling
- Fix grammatical errors in all text

HANDLING CORRECTIONS:
- If user says "sorry", "wrong", "typo", "correction", "actually", "I meant", "I spelt it wrong", "I made a mistake" → they are CORRECTING a previous answer
- When correcting, REPLACE the old value with the new value in the same field
- If user corrects an email/name/etc., look at the current spec to see which field has the wrong value and replace it
- Example: If current spec has freelancer.email = "wrong@email.com" and user says "sorry, it's correct@email.com", replace freelancer.email with "correct@email.com"

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

IMPORTANT - HANDLING CORRECTIONS:
- If the user says "sorry", "wrong", "typo", "correction", "actually", "I meant", "I spelt it wrong", "I made a mistake", "it's actually" → they are CORRECTING a previous value
- When correcting, look at the current spec to identify which field has the wrong value
- The correction might be for a DIFFERENT field than what was just asked about
- Check the spec for fields that match what the user is correcting (e.g., if they mention "email", check both freelancer.email and client.email)
- REPLACE the old value with the new corrected value in the matching field
- Example: If user says "sorry i spelt the email wrong. its correct@email.com" and current spec has freelancer.email = "wrong@email.com", replace freelancer.email with "correct@email.com"
- Example: If user says "actually my name is John" and current spec has freelancer.name = "Jane", replace freelancer.name with "John"
- Example: If user says "the client email is actually client@email.com" and current spec has client.email = "old@email.com", replace client.email with "client@email.com"

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
        
        # Post-process to ensure proper formatting
        updated_spec = format_spec_values(updated_spec)
        
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


def capitalize_name(name: str) -> str:
    """Properly capitalize a person's name."""
    if not name:
        return name
    
    # Handle special prefixes
    special_prefixes = ["mc", "mac", "o'", "d'", "de ", "van ", "von "]
    
    # Split into words
    words = name.strip().split()
    result = []
    
    for word in words:
        word_lower = word.lower()
        
        # Check for special prefixes
        handled = False
        for prefix in special_prefixes:
            if word_lower.startswith(prefix):
                # Capitalize after prefix
                prefix_len = len(prefix)
                if prefix in ["mc", "mac"]:
                    # McDonald, MacArthur
                    result.append(prefix.capitalize() + word[prefix_len:].capitalize())
                elif prefix == "o'":
                    # O'Brien
                    result.append("O'" + word[2:].capitalize())
                else:
                    result.append(word.capitalize())
                handled = True
                break
        
        if not handled:
            # Standard title case
            result.append(word.capitalize())
    
    return " ".join(result)


def format_spec_values(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Post-process spec to ensure proper formatting of names and text."""
    
    # Format freelancer name
    if spec.get("freelancer") and spec["freelancer"].get("name"):
        spec["freelancer"]["name"] = capitalize_name(spec["freelancer"]["name"])
    
    # Format freelancer business name
    if spec.get("freelancer") and spec["freelancer"].get("business_name"):
        spec["freelancer"]["business_name"] = capitalize_name(spec["freelancer"]["business_name"])
    
    # Format client name
    if spec.get("client") and spec["client"].get("name"):
        spec["client"]["name"] = capitalize_name(spec["client"]["name"])
    
    # Format client business name
    if spec.get("client") and spec["client"].get("business_name"):
        spec["client"]["business_name"] = capitalize_name(spec["client"]["business_name"])
    
    # Format title - ensure it's properly capitalized
    if spec.get("title"):
        title = spec["title"].strip()
        # Capitalize first letter of each major word
        if title and not title[0].isupper():
            words = title.split()
            minor_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'by', 'of'}
            result = []
            for i, word in enumerate(words):
                if i == 0 or word.lower() not in minor_words:
                    result.append(word.capitalize())
                else:
                    result.append(word.lower())
            spec["title"] = " ".join(result)
    
    # Format deliverables - ensure proper capitalization
    if spec.get("deliverables"):
        formatted_deliverables = []
        for d in spec["deliverables"]:
            if isinstance(d, dict):
                if d.get("item"):
                    item = d["item"].strip()
                    # Capitalize first letter
                    if item and not item[0].isupper():
                        d["item"] = item[0].upper() + item[1:]
                if d.get("description"):
                    desc = d["description"].strip()
                    if desc and not desc[0].isupper():
                        d["description"] = desc[0].upper() + desc[1:]
                formatted_deliverables.append(d)
            elif isinstance(d, str):
                d = d.strip()
                if d and not d[0].isupper():
                    d = d[0].upper() + d[1:]
                formatted_deliverables.append(d)
        spec["deliverables"] = formatted_deliverables
    
    return spec
