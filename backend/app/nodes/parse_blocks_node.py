"""
Parse Blocks Node
Converts visual block/node graph into a structured contract spec.
"""
from typing import Dict, Any, List
from ..contract_schema import get_empty_contract_spec


async def parse_blocks_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads: state["raw_input"] (blocks JSON)
    Parses block graph into contract_spec format.
    Writes: "contract_spec", "parse_notes"
    
    Expected blocks format:
    {
        "nodes": [
            {"id": "1", "type": "party", "data": {"role": "freelancer", "name": "...", "email": "..."}},
            {"id": "2", "type": "party", "data": {"role": "client", "name": "...", "email": "..."}},
            {"id": "3", "type": "deliverable", "data": {"item": "...", "description": "..."}},
            {"id": "4", "type": "payment", "data": {"amount": 500, "currency": "USD", "schedule": "..."}},
            {"id": "5", "type": "timeline", "data": {"deadline": "...", "start_date": "..."}},
            {"id": "6", "type": "terms", "data": {"revisions": 3, "late_policy": "..."}},
            ...
        ],
        "edges": [
            {"from": "1", "to": "3"},
            ...
        ]
    }
    """
    blocks = state.get("raw_input") or {}
    nodes = blocks.get("nodes", [])
    
    # Start with empty spec
    spec = get_empty_contract_spec()
    parse_notes = []
    
    for node in nodes:
        node_type = node.get("type", "").lower()
        data = node.get("data", {})
        
        if node_type == "party":
            role = data.get("role", "").lower()
            if role == "freelancer":
                spec["freelancer"] = {
                    "name": data.get("name"),
                    "business_name": data.get("business_name"),
                    "email": data.get("email"),
                    "phone": data.get("phone"),
                    "address": data.get("address"),
                }
                parse_notes.append(f"Parsed freelancer: {data.get('name')}")
            elif role == "client":
                spec["client"] = {
                    "name": data.get("name"),
                    "business_name": data.get("business_name"),
                    "email": data.get("email"),
                    "phone": data.get("phone"),
                    "address": data.get("address"),
                }
                parse_notes.append(f"Parsed client: {data.get('name')}")
        
        elif node_type == "deliverable":
            deliverable = {
                "item": data.get("item") or data.get("name"),
                "description": data.get("description"),
                "format": data.get("format"),
                "quantity": data.get("quantity"),
            }
            spec["deliverables"].append(deliverable)
            parse_notes.append(f"Parsed deliverable: {deliverable['item']}")
        
        elif node_type == "payment":
            spec["payment"] = {
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "schedule": data.get("schedule"),
                "deposit_percentage": data.get("deposit_percentage"),
                "milestones": data.get("milestones", []),
            }
            parse_notes.append(f"Parsed payment: {data.get('amount')} {data.get('currency')}")
        
        elif node_type == "timeline":
            spec["timeline"] = {
                "start_date": data.get("start_date"),
                "deadline": data.get("deadline"),
                "milestones": data.get("milestones", []),
            }
            parse_notes.append(f"Parsed timeline: deadline {data.get('deadline')}")
        
        elif node_type == "terms" or node_type == "quality":
            spec["quality_standards"] = {
                "acceptance_criteria": data.get("acceptance_criteria", []),
                "revision_policy": data.get("revision_policy"),
                "max_revisions": data.get("revisions") or data.get("max_revisions"),
                "approval_process": data.get("approval_process"),
            }
            parse_notes.append(f"Parsed quality terms: {data.get('revisions')} revisions")
        
        elif node_type == "failure" or node_type == "protection":
            spec["failure_scenarios"] = {
                "late_delivery": {
                    "penalty_type": data.get("late_policy") or data.get("penalty_type"),
                    "penalty_amount": data.get("late_penalty"),
                    "grace_period_days": data.get("grace_period"),
                },
                "non_delivery": {
                    "refund_percentage": data.get("non_delivery_refund", 100),
                    "conditions": data.get("refund_conditions", []),
                },
                "client_rejection": {
                    "process": data.get("rejection_process"),
                    "refund_policy": data.get("rejection_refund"),
                },
                "freelancer_cancellation": {
                    "refund_policy": data.get("freelancer_cancel_refund"),
                    "notice_period_days": data.get("notice_days"),
                },
                "client_cancellation": {
                    "refund_policy": data.get("client_cancel_refund"),
                    "kill_fee_percentage": data.get("kill_fee"),
                },
            }
            parse_notes.append("Parsed failure scenarios")
        
        elif node_type == "dispute":
            spec["dispute_resolution"] = {
                "method": data.get("method"),
                "location": data.get("location") or data.get("jurisdiction"),
                "process": data.get("process"),
                "governing_law": data.get("governing_law"),
            }
            parse_notes.append(f"Parsed dispute resolution: {data.get('method')}")
        
        elif node_type == "title" or node_type == "project":
            spec["title"] = data.get("title") or data.get("name")
            parse_notes.append(f"Parsed title: {spec['title']}")
    
    return {
        "contract_spec": spec,
        "parse_notes": parse_notes,
    }

