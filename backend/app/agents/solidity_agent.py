"""
Solidity Generation Agent
Converts visual contract blocks from React Flow into valid Solidity smart contract code.
Uses the existing GeminiLLM wrapper for generation.
"""
import json
from typing import Dict, Any, List

from ..llm import GeminiLLM


SOLIDITY_SYSTEM_PROMPT = """You are an expert Solidity smart contract developer. Your task is to convert visual contract blocks into valid, secure, and deployable Solidity code.

You MUST:
1. Generate compilable Solidity code (version ^0.8.19)
2. Include SPDX license identifier and pragma statement
3. Follow security best practices (checks-effects-interactions pattern)
4. Add clear comments explaining each section
5. Use require() statements for input validation
6. Add events for all state changes
7. Include proper access control modifiers
8. Handle edge cases and potential reentrancy

Block Type Mappings:
- "party" blocks → address variables with access control (onlyOwner, onlySender, onlyRecipient)
- "asset" blocks → token references or native ETH handling
- "amount" blocks → uint256 payment amounts with validation
- "condition" blocks → require() statements and modifiers
- "trigger" blocks → events and state transitions
- "timeout" blocks → time-based modifiers (block.timestamp checks)
- "module" blocks → function definitions

Output Format:
Return a JSON object with:
{
    "solidity": "// Full Solidity contract code here",
    "contractName": "ContractName",
    "explanation": "Brief explanation of what the contract does",
    "functions": ["list", "of", "function", "names"],
    "events": ["list", "of", "event", "names"]
}

IMPORTANT: Return ONLY valid JSON, no markdown code blocks or extra text."""


class SolidityGenerationAgent:
    """
    Agent that converts visual contract blocks into Solidity smart contracts.
    Uses the existing GeminiLLM for code generation.
    """
    
    def __init__(self):
        """Initialize the Solidity generation agent."""
        self.llm = GeminiLLM()
        self.system_prompt = SOLIDITY_SYSTEM_PROMPT
    
    def _parse_blocks(self, blocks: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse React Flow blocks and edges into a structured contract specification.
        """
        spec = {
            "parties": [],
            "assets": [],
            "amounts": [],
            "conditions": [],
            "triggers": [],
            "timeouts": [],
            "modules": [],
            "connections": [],
        }
        
        for block in blocks:
            block_type = block.get("type") or block.get("data", {}).get("type", "unknown")
            block_data = block.get("data", {})
            block_id = block.get("id", "")
            
            block_info = {
                "id": block_id,
                "label": block_data.get("label", block_type),
                "content": block_data.get("content", ""),
                "title": block_data.get("title", ""),
                "subtitle": block_data.get("subtitle", ""),
                "filled": block_data.get("filled", False),
            }
            
            if block_type == "party":
                spec["parties"].append(block_info)
            elif block_type == "asset":
                spec["assets"].append(block_info)
            elif block_type == "amount":
                spec["amounts"].append(block_info)
            elif block_type == "condition":
                spec["conditions"].append(block_info)
            elif block_type == "trigger":
                spec["triggers"].append(block_info)
            elif block_type == "timeout":
                spec["timeouts"].append(block_info)
            elif block_type == "module":
                spec["modules"].append(block_info)
            else:
                # Handle custom blocks based on ID
                if "freelancer" in block_id.lower() or "client" in block_id.lower():
                    spec["parties"].append(block_info)
                elif "payment" in block_id.lower():
                    spec["amounts"].append(block_info)
                elif "deliverable" in block_id.lower():
                    spec["modules"].append(block_info)
        
        for edge in edges:
            spec["connections"].append({
                "from": edge.get("from") or edge.get("source", ""),
                "to": edge.get("to") or edge.get("target", ""),
            })
        
        return spec
    
    def _build_prompt(self, spec: Dict[str, Any]) -> str:
        """Build the LLM prompt from the parsed specification."""
        prompt_parts = ["Generate a Solidity smart contract based on these visual blocks:\n"]
        
        if spec["parties"]:
            prompt_parts.append("\n## Parties (addresses):")
            for party in spec["parties"]:
                prompt_parts.append(f"- {party['label']}: {party.get('subtitle') or party.get('content') or 'address'}")
        
        if spec["assets"]:
            prompt_parts.append("\n## Assets:")
            for asset in spec["assets"]:
                prompt_parts.append(f"- {asset['label']}: {asset.get('content', 'ETH')}")
        
        if spec["amounts"]:
            prompt_parts.append("\n## Payment Amounts:")
            for amount in spec["amounts"]:
                prompt_parts.append(f"- {amount['label']}: {amount.get('subtitle') or amount.get('content') or 'amount'}")
        
        if spec["conditions"]:
            prompt_parts.append("\n## Conditions (require statements):")
            for condition in spec["conditions"]:
                prompt_parts.append(f"- {condition['label']}: {condition.get('content', 'condition check')}")
        
        if spec["triggers"]:
            prompt_parts.append("\n## Triggers (events):")
            for trigger in spec["triggers"]:
                prompt_parts.append(f"- {trigger['label']}: {trigger.get('content', 'event trigger')}")
        
        if spec["timeouts"]:
            prompt_parts.append("\n## Timeouts (time-based conditions):")
            for timeout in spec["timeouts"]:
                prompt_parts.append(f"- {timeout['label']}: {timeout.get('content', 'time condition')}")
        
        if spec["modules"]:
            prompt_parts.append("\n## Modules (functions/deliverables):")
            for module in spec["modules"]:
                prompt_parts.append(f"- {module['label']}: {module.get('subtitle') or module.get('content') or 'function'}")
        
        if spec["connections"]:
            prompt_parts.append("\n## Flow Connections:")
            for conn in spec["connections"]:
                prompt_parts.append(f"- {conn['from']} → {conn['to']}")
        
        prompt_parts.append("\n\nGenerate a complete, secure Solidity contract implementing this logic.")
        prompt_parts.append("Include constructor, state variables, modifiers, events, and all necessary functions.")
        prompt_parts.append("Return the result as a JSON object with 'solidity', 'contractName', 'explanation', 'functions', and 'events' keys.")
        
        return "\n".join(prompt_parts)
    
    async def generate_solidity(
        self, 
        blocks: List[Dict[str, Any]], 
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate Solidity code from visual blocks and edges.
        """
        # Parse blocks into structured spec
        spec = self._parse_blocks(blocks, edges)
        
        # Build the prompt
        prompt = self._build_prompt(spec)
        
        try:
            # Use chat_json for structured response
            result = await self.llm.chat_json(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,  # Lower temperature for more consistent code
            )
            
            # Ensure required fields exist
            if not result.get("solidity"):
                # If JSON parsing worked but no solidity field, try plain chat
                response = await self.llm.chat(
                    prompt=prompt,
                    system_prompt=self.system_prompt,
                    temperature=0.3,
                )
                result = {
                    "solidity": self._extract_solidity(response),
                    "contractName": "GeneratedContract",
                    "explanation": "Smart contract generated from visual blocks",
                    "functions": [],
                    "events": [],
                }
            
            if "contractName" not in result:
                result["contractName"] = "GeneratedContract"
            if "explanation" not in result:
                result["explanation"] = "Smart contract generated from visual blocks"
            if "functions" not in result:
                result["functions"] = self._extract_functions(result.get("solidity", ""))
            if "events" not in result:
                result["events"] = self._extract_events(result.get("solidity", ""))
            
            # Generate ABI stub
            result["abi"] = self._generate_abi_stub(result)
            
            return result
            
        except Exception as e:
            print(f"[SolidityAgent] Error: {e}")
            return {
                "solidity": f"// Error generating contract: {str(e)}",
                "contractName": "ErrorContract",
                "explanation": f"Failed to generate contract: {str(e)}",
                "functions": [],
                "events": [],
                "abi": "[]",
                "error": str(e),
            }
    
    def _extract_solidity(self, text: str) -> str:
        """Extract Solidity code from response text."""
        # Try to find code blocks
        if "```solidity" in text:
            start = text.find("```solidity") + len("```solidity")
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        
        if "```" in text:
            start = text.find("```") + 3
            # Skip language identifier if present
            newline = text.find("\n", start)
            if newline > start and newline - start < 20:
                start = newline + 1
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        
        # Look for SPDX license as start of Solidity code
        if "SPDX-License-Identifier" in text:
            start = text.find("//")
            if start >= 0:
                return text[start:].strip()
        
        return text.strip()
    
    def _extract_functions(self, solidity: str) -> List[str]:
        """Extract function names from Solidity code."""
        import re
        pattern = r'function\s+(\w+)\s*\('
        matches = re.findall(pattern, solidity)
        return list(set(matches))
    
    def _extract_events(self, solidity: str) -> List[str]:
        """Extract event names from Solidity code."""
        import re
        pattern = r'event\s+(\w+)\s*\('
        matches = re.findall(pattern, solidity)
        return list(set(matches))
    
    def _generate_abi_stub(self, result: Dict[str, Any]) -> str:
        """Generate a simple ABI stub from the result."""
        abi = []
        
        abi.append({
            "type": "constructor",
            "inputs": [],
            "stateMutability": "nonpayable"
        })
        
        for func_name in result.get("functions", []):
            abi.append({
                "type": "function",
                "name": func_name,
                "inputs": [],
                "outputs": [],
                "stateMutability": "nonpayable"
            })
        
        for event_name in result.get("events", []):
            abi.append({
                "type": "event",
                "name": event_name,
                "inputs": []
            })
        
        return json.dumps(abi, indent=2)
