"""
Neo Contract Generation Service
Orchestrates the NeoContractAgent to convert visual blocks into Neo Boa Python code.
"""
from typing import Dict, Any, List, Optional
from ..agents.neo_agent import NeoContractAgent


# Cache the agent instance for reuse
_agent_instance: Optional[NeoContractAgent] = None


def get_agent() -> NeoContractAgent:
    """Get or create the Neo contract generation agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = NeoContractAgent()
    return _agent_instance


async def generate_neo_contract(
    blocks: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    contract_spec: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a Neo Boa Python smart contract from visual blocks.
    
    Args:
        blocks: List of React Flow block objects
        edges: List of React Flow edge objects  
        contract_spec: Optional existing contract specification to enhance the generation
        
    Returns:
        Dictionary containing:
        - neo_python: The generated Neo Boa Python code
        - contractName: Name of the contract
        - explanation: Human-readable explanation
        - functions: List of function names
        - events: List of event names
        - status: "success" or "error"
    """
    try:
        agent = get_agent()
        
        # If we have contract_spec, enhance the blocks with that data
        if contract_spec:
            blocks = _enhance_blocks_with_spec(blocks, contract_spec)
        
        # Generate the Neo Python code
        result = await agent.generate_neo_contract(blocks, edges)
        
        # Add success status
        result["status"] = "success" if "error" not in result else "error"
        
        return result
        
    except Exception as e:
        return {
            "neo_python": f"# Error: {str(e)}",
            "contractName": "ErrorContract",
            "explanation": f"Failed to generate contract: {str(e)}",
            "functions": [],
            "events": [],
            "status": "error",
            "error": str(e),
        }


def _enhance_blocks_with_spec(
    blocks: List[Dict[str, Any]], 
    contract_spec: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Enhance block data with information from contract_spec.
    Same logic as Solidity service for consistency.
    """
    enhanced_blocks = []
    
    for block in blocks:
        enhanced_block = block.copy()
        block_id = block.get("id", "")
        block_data = enhanced_block.get("data", {}).copy()
        
        # Enhance party blocks with freelancer/client info
        if "freelancer" in block_id.lower():
            freelancer = contract_spec.get("freelancer", {})
            if freelancer:
                block_data["subtitle"] = freelancer.get("name", "Freelancer")
                block_data["content"] = f"Address: {freelancer.get('email', 'freelancer@example.com')}"
        
        elif "client" in block_id.lower():
            client = contract_spec.get("client", {})
            if client:
                block_data["subtitle"] = client.get("name", "Client")
                block_data["content"] = f"Address: {client.get('email', 'client@example.com')}"
        
        # Enhance payment blocks
        elif "payment" in block_id.lower():
            payment = contract_spec.get("payment", {})
            if payment:
                amount = payment.get("amount", 0)
                currency = payment.get("currency", "GAS")
                block_data["subtitle"] = f"{amount} {currency}"
                block_data["content"] = f"Schedule: {payment.get('schedule', 'on_completion')}"
        
        # Enhance deliverables blocks
        elif "deliverable" in block_id.lower():
            deliverables = contract_spec.get("deliverables", [])
            if deliverables:
                items = [d.get("item", str(d)) if isinstance(d, dict) else str(d) for d in deliverables]
                block_data["content"] = ", ".join(items[:3])
        
        # Enhance timeline blocks
        elif "timeline" in block_id.lower():
            timeline = contract_spec.get("timeline", {})
            if timeline:
                block_data["subtitle"] = f"Deadline: {timeline.get('deadline', 'TBD')}"
                block_data["content"] = f"Start: {timeline.get('start_date', 'TBD')}"
        
        enhanced_block["data"] = block_data
        enhanced_blocks.append(enhanced_block)
    
    return enhanced_blocks



