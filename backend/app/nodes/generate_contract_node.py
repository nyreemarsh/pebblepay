"""
Generate Contract Node
Creates comprehensive contract text with robust legal protections.
Includes failure scenarios, dispute resolution, and clear terms.
"""
import json
from typing import Dict, Any
from datetime import datetime
from ..llm import llm


SYSTEM_PROMPT = """You are an expert contract writer creating professional freelance contracts.

Generate a COMPLETE, ROBUST contract that includes:

1. PARTIES - Full names and contact details (no placeholders)
2. SCOPE OF WORK - Clear deliverables with formats and acceptance criteria
3. PAYMENT TERMS - Amount, schedule, late payment penalties
4. TIMELINE - Deadlines and milestones
5. REVISIONS - How many included, cost for extras
6. QUALITY STANDARDS - What constitutes acceptable work
7. FAILURE SCENARIOS (CRITICAL):
   - Late delivery: What happens, any penalties
   - Non-delivery: Refund policy
   - Client rejection: Process for handling disputes
   - Cancellation by either party: Terms and refunds
8. DISPUTE RESOLUTION - Step-by-step process
9. LIABILITY - Limitations and exclusions
10. INTELLECTUAL PROPERTY - Who owns the work and when
11. CONFIDENTIALITY - If applicable
12. TERMINATION - How either party can end the contract
13. GENERAL PROVISIONS - Force majeure, amendments, entire agreement

CRITICAL FORMATTING RULES:
- Output PLAIN TEXT ONLY - NO markdown formatting whatsoever
- Do NOT use asterisks (*) for bold or bullet points
- Do NOT use underscores (_) for emphasis
- Do NOT use hash symbols (#) for headings
- Use regular dashes (-) for bullet points, not asterisks
- Section headings should be numbered: "1. PARTIES" not "**1. PARTIES**"
- Just write clean, plain text

IMPORTANT:
- Use the ACTUAL names provided, not placeholders like [Name]
- If a date is "in 2 weeks", calculate the actual date
- Include specific amounts and currencies
- Write in clear, professional language (not heavy legalese)
- Make failure scenarios fair to both parties
- Today's date is: {today}

Output the complete contract as PLAIN TEXT with numbered section headings.
Do NOT use markdown, asterisks, underscores, or any special formatting."""


async def generate_contract_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads: state["contract_spec"].
    Uses LLM to generate a comprehensive contract_text.
    Writes: "contract_text".
    """
    spec = state.get("contract_spec") or {}
    today = datetime.now().strftime("%B %d, %Y")
    
    # Format the spec for the LLM
    formatted_spec = format_spec_for_generation(spec, today)
    
    prompt = f"""Generate a complete freelance service contract based on this specification:

{formatted_spec}

Today's date: {today}

Create a professional, legally-sound contract that:
1. Uses the actual names provided (no placeholders)
2. Includes all the failure scenarios and protections specified
3. Has clear, enforceable terms
4. Protects both the freelancer and client fairly
5. Is written in professional but accessible language

Generate the COMPLETE contract document."""

    system = SYSTEM_PROMPT.format(today=today)
    
    try:
        contract_text = await llm.chat(prompt, system_prompt=system)
        
        # Clean up any markdown artifacts
        contract_text = clean_contract_text(contract_text)
        
        return {
            "contract_text": contract_text.strip(),
        }
    
    except Exception as e:
        print(f"[generate_contract_node] Error: {e}")
        # Generate a template-based contract as fallback
        contract_text = generate_fallback_contract(spec, today)
        return {"contract_text": contract_text}


def format_spec_for_generation(spec: Dict[str, Any], today: str) -> str:
    """Format the contract spec into a clear prompt for the LLM."""
    sections = []
    
    # Title
    title = spec.get("title") or "Freelance Service Agreement"
    sections.append(f"CONTRACT TITLE: {title}")
    
    # Parties
    freelancer = spec.get("freelancer", {}) or {}
    client = spec.get("client", {}) or {}
    
    sections.append("\n## PARTIES")
    sections.append(f"FREELANCER:")
    sections.append(f"  Name: {freelancer.get('name', 'Not provided')}")
    if freelancer.get("business_name"):
        sections.append(f"  Business Name: {freelancer['business_name']}")
    sections.append(f"  Email: {freelancer.get('email', 'Not provided')}")
    if freelancer.get("phone"):
        sections.append(f"  Phone: {freelancer['phone']}")
    if freelancer.get("address"):
        sections.append(f"  Address: {freelancer['address']}")
    
    sections.append(f"\nCLIENT:")
    sections.append(f"  Name: {client.get('name', 'Not provided')}")
    if client.get("business_name"):
        sections.append(f"  Business Name: {client['business_name']}")
    sections.append(f"  Email: {client.get('email', 'Not provided')}")
    if client.get("phone"):
        sections.append(f"  Phone: {client['phone']}")
    if client.get("address"):
        sections.append(f"  Address: {client['address']}")
    
    # Deliverables
    sections.append("\n## DELIVERABLES")
    deliverables = spec.get("deliverables", []) or []
    if deliverables:
        for i, d in enumerate(deliverables, 1):
            if isinstance(d, dict):
                sections.append(f"  {i}. {d.get('item', 'Item')}")
                if d.get("description"):
                    sections.append(f"     Description: {d['description']}")
                if d.get("format"):
                    sections.append(f"     Format: {d['format']}")
            else:
                sections.append(f"  {i}. {d}")
    else:
        sections.append("  No specific deliverables listed")
    
    # Payment
    sections.append("\n## PAYMENT")
    payment = spec.get("payment", {}) or {}
    sections.append(f"  Amount: {payment.get('amount', 'Not specified')} {payment.get('currency', '')}")
    sections.append(f"  Schedule: {payment.get('schedule', 'On completion')}")
    if payment.get("deposit_percentage"):
        sections.append(f"  Deposit: {payment['deposit_percentage']}% upfront")
    
    # Timeline
    sections.append("\n## TIMELINE")
    timeline = spec.get("timeline", {}) or {}
    sections.append(f"  Deadline: {timeline.get('deadline', 'Not specified')}")
    if timeline.get("start_date"):
        sections.append(f"  Start Date: {timeline['start_date']}")
    
    # Quality Standards
    sections.append("\n## QUALITY STANDARDS")
    quality = spec.get("quality_standards", {}) or {}
    if quality.get("acceptance_criteria"):
        sections.append(f"  Acceptance Criteria: {', '.join(quality['acceptance_criteria'])}")
    sections.append(f"  Max Revisions: {quality.get('max_revisions', '2')} rounds included")
    if quality.get("revision_policy"):
        sections.append(f"  Extra Revisions: {quality['revision_policy']}")
    
    # Failure Scenarios
    sections.append("\n## FAILURE SCENARIOS")
    failure = spec.get("failure_scenarios", {}) or {}
    
    late = failure.get("late_delivery", {}) or {}
    sections.append(f"  Late Delivery:")
    sections.append(f"    Policy: {late.get('penalty_type', 'No penalty')}")
    if late.get("penalty_amount"):
        sections.append(f"    Amount: {late['penalty_amount']}")
    if late.get("grace_period_days"):
        sections.append(f"    Grace Period: {late['grace_period_days']} days")
    
    non_del = failure.get("non_delivery", {}) or {}
    sections.append(f"  Non-Delivery:")
    sections.append(f"    Refund: {non_del.get('refund_percentage', '100')}%")
    if non_del.get("conditions"):
        sections.append(f"    Conditions: {', '.join(non_del['conditions'])}")
    
    rejection = failure.get("client_rejection", {}) or {}
    sections.append(f"  If Client Rejects Work:")
    sections.append(f"    Process: {rejection.get('process', 'Discussion and mediation')}")
    sections.append(f"    Refund Policy: {rejection.get('refund_policy', '50% refund after good faith effort')}")
    
    cancel_f = failure.get("freelancer_cancellation", {}) or {}
    sections.append(f"  Freelancer Cancellation:")
    sections.append(f"    Refund: {cancel_f.get('refund_policy', 'Full refund of unused deposit')}")
    
    cancel_c = failure.get("client_cancellation", {}) or {}
    sections.append(f"  Client Cancellation:")
    sections.append(f"    Kill Fee: {cancel_c.get('kill_fee_percentage', '25')}% of total for work done")
    
    # Dispute Resolution
    sections.append("\n## DISPUTE RESOLUTION")
    dispute = spec.get("dispute_resolution", {}) or {}
    sections.append(f"  Method: {dispute.get('method', 'Negotiation first, then mediation')}")
    if dispute.get("location"):
        sections.append(f"  Jurisdiction: {dispute['location']}")
    if dispute.get("governing_law"):
        sections.append(f"  Governing Law: {dispute['governing_law']}")
    
    # IP Ownership
    sections.append("\n## INTELLECTUAL PROPERTY")
    ip = spec.get("ip_ownership", {}) or {}
    sections.append(f"  Final Work Owned By: {ip.get('final_work', 'Client after full payment')}")
    sections.append(f"  Transfer On: {ip.get('transfer_on', 'Full payment received')}")
    sections.append(f"  Portfolio Rights: {ip.get('portfolio_rights', True)}")
    
    # Liability
    sections.append("\n## LIABILITY")
    liability = spec.get("liability", {}) or {}
    sections.append(f"  Max Liability: {liability.get('max_liability', 'Contract value')}")
    
    # Special Terms
    special = spec.get("special_terms", []) or []
    if special:
        sections.append("\n## SPECIAL TERMS")
        for term in special:
            sections.append(f"  - {term}")
    
    return "\n".join(sections)


def clean_contract_text(text: str) -> str:
    """Clean up any markdown or formatting artifacts from the contract text."""
    import re
    
    # Remove markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    
    # Remove any remaining triple backticks
    text = text.replace("```", "")
    
    # Remove bold markdown (**text** or __text__)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    
    # Remove italic markdown (*text* or _text_) - be careful not to remove bullet dashes
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_([^_]+)_(?!_)', r'\1', text)
    
    # Remove markdown headers (# ## ### etc)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # Replace asterisk bullet points with dashes
    text = re.sub(r'^\s*\*\s+', '- ', text, flags=re.MULTILINE)
    
    # Clean up any remaining stray asterisks at start of lines
    text = re.sub(r'^\s*\*+\s*', '', text, flags=re.MULTILINE)
    
    # Remove [text](url) markdown links, keep just the text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Clean up multiple consecutive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def generate_fallback_contract(spec: Dict[str, Any], today: str) -> str:
    """Generate a template-based contract when LLM fails."""
    freelancer = spec.get("freelancer", {}) or {}
    client = spec.get("client", {}) or {}
    payment = spec.get("payment", {}) or {}
    timeline = spec.get("timeline", {}) or {}
    quality = spec.get("quality_standards", {}) or {}
    failure = spec.get("failure_scenarios", {}) or {}
    dispute = spec.get("dispute_resolution", {}) or {}
    
    deliverables_list = spec.get("deliverables", []) or []
    deliverables_text = "\n".join(f"  - {d.get('item', d) if isinstance(d, dict) else d}" 
                                   for d in deliverables_list) or "  - As agreed"
    
    contract = f"""
FREELANCE SERVICE AGREEMENT

Effective Date: {today}

═══════════════════════════════════════════════════════════════════════

1. PARTIES

This Agreement is entered into between:

FREELANCER:
  {freelancer.get('name', '[Freelancer Name]')}
  {f"Business: {freelancer['business_name']}" if freelancer.get('business_name') else ''}
  Email: {freelancer.get('email', '[Email]')}

CLIENT:
  {client.get('name', '[Client Name]')}
  {f"Business: {client['business_name']}" if client.get('business_name') else ''}
  Email: {client.get('email', '[Email]')}

═══════════════════════════════════════════════════════════════════════

2. SCOPE OF WORK

The Freelancer agrees to provide the following deliverables:
{deliverables_text}

═══════════════════════════════════════════════════════════════════════

3. PAYMENT TERMS

Total Fee: {payment.get('amount', '[Amount]')} {payment.get('currency', '')}
Payment Schedule: {payment.get('schedule', 'Upon completion')}

═══════════════════════════════════════════════════════════════════════

4. TIMELINE

Project Deadline: {timeline.get('deadline', '[Deadline]')}

═══════════════════════════════════════════════════════════════════════

5. REVISIONS

Number of revision rounds included: {quality.get('max_revisions', '2')}
Additional revisions will be charged at an agreed hourly rate.

═══════════════════════════════════════════════════════════════════════

6. WHAT HAPPENS IF THINGS GO WRONG

Late Delivery:
  {failure.get('late_delivery', {}).get('penalty_type', 'No penalty, but Freelancer will communicate delays promptly')}

Non-Delivery:
  If Freelancer cannot complete the work: {failure.get('non_delivery', {}).get('refund_percentage', '100')}% refund

Client Rejection:
  {failure.get('client_rejection', {}).get('process', 'Both parties will discuss in good faith. If unresolved, mediation.')}

Cancellation:
  - By Client: Pay for work completed plus {failure.get('client_cancellation', {}).get('kill_fee_percentage', '25')}% kill fee
  - By Freelancer: Full refund of unused deposit; work completed remains with Client

═══════════════════════════════════════════════════════════════════════

7. DISPUTE RESOLUTION

If disputes arise:
1. First, both parties will attempt to resolve through direct discussion
2. If unresolved, {dispute.get('method', 'mediation')} will be used
3. Jurisdiction: {dispute.get('location', 'Local small claims court')}

═══════════════════════════════════════════════════════════════════════

8. INTELLECTUAL PROPERTY

- Final work ownership transfers to Client upon full payment
- Freelancer retains the right to display work in portfolio

═══════════════════════════════════════════════════════════════════════

9. LIABILITY

Freelancer's total liability is limited to the contract value.
Freelancer is not liable for indirect or consequential damages.

═══════════════════════════════════════════════════════════════════════

10. AGREEMENT

By signing below, both parties agree to the terms of this contract.


FREELANCER:

Signature: _________________________ Date: _____________
Name: {freelancer.get('name', '[Name]')}


CLIENT:

Signature: _________________________ Date: _____________
Name: {client.get('name', '[Name]')}

═══════════════════════════════════════════════════════════════════════
"""
    return contract.strip()
