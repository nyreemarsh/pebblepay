"""
Explain Contract Node
Generates a comprehensive plain-English summary highlighting key protections.
"""
import json
from typing import Dict, Any
from ..llm import llm


SYSTEM_PROMPT = """You are a friendly contract explainer helping freelancers understand their contracts.

Create a summary that:
1. Explains the key points in plain English (no jargon)
2. Highlights the PROTECTIONS for the freelancer
3. Explains what happens if things go wrong
4. Notes any important deadlines or amounts
5. Is warm, reassuring, and easy to scan

Structure your summary with clear sections:
- Quick Overview (1-2 sentences)
- The Basics (who, what, when, how much)
- Your Protections (what happens if things go wrong)
- Key Dates & Deadlines
- Anything to Watch Out For

Keep it under 300 words but be thorough on the important points."""


async def explain_contract_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads: state["contract_spec"], state["contract_text"].
    Uses LLM to generate a comprehensive summary.
    Writes: "summary" and "assistant_message".
    """
    contract_spec = state.get("contract_spec") or {}
    contract_text = state.get("contract_text") or ""
    
    # Extract key info for the summary
    key_info = extract_key_info(contract_spec)
    
    prompt = f"""Create a friendly, comprehensive summary of this contract for the freelancer:

Contract Specification:
{json.dumps(contract_spec, indent=2, default=str)}

Key Information:
{key_info}

Full Contract (first 3000 chars):
{contract_text[:3000]}

Create a clear summary that:
1. Explains what the contract says in plain English
2. Highlights what protections the freelancer has
3. Explains what happens if things go wrong
4. Notes important amounts and dates
5. Mentions anything the freelancer should be aware of"""

    try:
        summary = await llm.chat(prompt, system_prompt=SYSTEM_PROMPT)
        summary = summary.strip()
        
        # Create a celebratory closing message
        final_message = create_final_message(summary, contract_spec)
        
        return {
            "summary": summary,
            "assistant_message": final_message,
        }
    
    except Exception as e:
        print(f"[explain_contract_node] Error: {e}")
        # Generate a basic summary from the spec
        summary = generate_fallback_summary(contract_spec)
        final_message = create_final_message(summary, contract_spec)
        
        return {
            "summary": summary,
            "assistant_message": final_message,
        }


def extract_key_info(spec: Dict[str, Any]) -> str:
    """Extract key information for the summary."""
    parts = []
    
    freelancer = spec.get("freelancer", {}) or {}
    client = spec.get("client", {}) or {}
    payment = spec.get("payment", {}) or {}
    timeline = spec.get("timeline", {}) or {}
    failure = spec.get("failure_scenarios", {}) or {}
    quality = spec.get("quality_standards", {}) or {}
    
    parts.append(f"Freelancer: {freelancer.get('name', 'Not specified')}")
    parts.append(f"Client: {client.get('name', 'Not specified')}")
    parts.append(f"Payment: {payment.get('amount', '?')} {payment.get('currency', '')}")
    parts.append(f"Deadline: {timeline.get('deadline', 'Not specified')}")
    parts.append(f"Revisions included: {quality.get('max_revisions', '2')}")
    
    # Failure scenarios
    late = failure.get("late_delivery", {}) or {}
    non_del = failure.get("non_delivery", {}) or {}
    rejection = failure.get("client_rejection", {}) or {}
    
    parts.append(f"\nIf late: {late.get('penalty_type', 'No penalty')}")
    parts.append(f"If can't complete: {non_del.get('refund_percentage', '100')}% refund")
    parts.append(f"If client rejects: {rejection.get('process', 'Discussion first')}")
    
    return "\n".join(parts)


def create_final_message(summary: str, spec: Dict[str, Any]) -> str:
    """Create the final celebratory message."""
    freelancer = spec.get("freelancer", {}) or {}
    client = spec.get("client", {}) or {}
    payment = spec.get("payment", {}) or {}
    
    freelancer_name = freelancer.get("name", "there")
    client_name = client.get("name", "your client")
    amount = payment.get("amount", "")
    currency = payment.get("currency", "")
    
    # Simpler message - details available via buttons (no markdown formatting)
    return f"""🎉 Your contract is ready, {freelancer_name}!

I've created a professional contract for your work with {client_name}.

Use the buttons below to:
• Download PDF - Get your contract as a professionally formatted PDF
• Explain Contract - See a plain-English breakdown of what you're agreeing to

Need any changes? Just let me know what you'd like to adjust!"""


def generate_fallback_summary(spec: Dict[str, Any]) -> str:
    """Generate a fallback summary when LLM fails."""
    freelancer = spec.get("freelancer", {}) or {}
    client = spec.get("client", {}) or {}
    payment = spec.get("payment", {}) or {}
    timeline = spec.get("timeline", {}) or {}
    quality = spec.get("quality_standards", {}) or {}
    failure = spec.get("failure_scenarios", {}) or {}
    
    deliverables = spec.get("deliverables", []) or []
    deliverables_text = ", ".join(
        d.get("item", str(d)) if isinstance(d, dict) else str(d) 
        for d in deliverables[:3]
    ) or "as agreed"
    
    late = failure.get("late_delivery", {}) or {}
    non_del = failure.get("non_delivery", {}) or {}
    
    summary = f"""📋 QUICK OVERVIEW
This is a contract between you ({freelancer.get('name', 'Freelancer')}) and {client.get('name', 'Client')} for {deliverables_text}.

💰 THE BASICS
• You'll be paid: {payment.get('amount', '?')} {payment.get('currency', '')}
• Payment schedule: {payment.get('schedule', 'On completion')}
• Deadline: {timeline.get('deadline', 'As agreed')}
• Revisions included: {quality.get('max_revisions', '2')}

🛡️ YOUR PROTECTIONS
• If you're late: {late.get('penalty_type', 'No penalty, just communicate')}
• If you can't complete: Refund {non_del.get('refund_percentage', '100')}%
• If client cancels: They pay for work done plus a kill fee

⚠️ IMPORTANT
• Full ownership transfers after payment
• You can show this work in your portfolio
• Disputes go to mediation first"""

    return summary
