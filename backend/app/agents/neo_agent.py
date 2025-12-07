"""
Neo Python Contract Generation Agent
Converts visual contract blocks from React Flow into valid Neo Boa Python smart contract code.
Uses the existing GeminiLLM wrapper for generation.

Based on Neo3-Boa patterns from: https://github.com/CityOfZion/neo3-boa
"""
import json
import re
from typing import Dict, Any, List

from ..llm import GeminiLLM


NEO_SYSTEM_PROMPT = """You are an expert Neo Boa smart contract developer. Your task is to convert visual contract blocks into valid, secure, and deployable Neo Python code using Neo3-Boa compiler patterns.

Based on Neo3-Boa documentation: https://github.com/CityOfZion/neo3-boa

CRITICAL REQUIREMENTS:
1. Generate compilable Neo Boa Python code (Python 3.12+ compatible)
2. Use ONLY Neo Boa supported Python subset - NO f-strings, NO advanced Python features
3. Use proper Neo Boa imports from boa3.builtin
4. Use @public decorator for ALL public methods (imported from boa3.builtin)
5. Use get() and put() from boa3.builtin.interop.storage for persistent storage
6. Use CheckWitness() from boa3.builtin.interop.runtime for authorization (NOT checkwitness)
7. Use Neo-specific types: UInt160, UInt256, ByteString, int
8. Add clear comments explaining each section
9. Include proper error handling with assertions
10. Define events using CreateNewEvent pattern
11. Follow Neo Boa best practices from official examples

REQUIRED IMPORTS (use exact syntax):
```python
from boa3.builtin import CreateNewEvent
from boa3.builtin.interop.storage import get, put
from boa3.builtin.interop.runtime import CheckWitness
from boa3.builtin.type import UInt160
```

STORAGE PATTERN:
- Use: from boa3.builtin.interop.storage import get, put
- put(key, value) to store data
- get(key) to retrieve (returns value or None)
- Keys should be ByteString or str
- Example: put(b'owner', owner_address) or put('balance', amount)

AUTHORIZATION PATTERN:
- Use: from boa3.builtin.interop.runtime import CheckWitness
- CheckWitness(address) returns bool
- Example: assert CheckWitness(owner), "Unauthorized"

EVENT PATTERN:
- Define at module level: TransferEvent = CreateNewEvent([('from', UInt160), ('to', UInt160), ('amount', int)])
- Emit events: TransferEvent(from_addr, to_addr, amount)
- Events are automatically indexed and logged

BLOCK TYPE MAPPINGS:
- "party" blocks → UInt160 address variables with CheckWitness() authorization
- "asset" blocks → token references or GAS/NEO handling (use NEP-17 patterns)
- "amount" blocks → int payment amounts with validation
- "condition" blocks → assertions and CheckWitness() checks
- "trigger" blocks → events (CreateNewEvent)
- "timeout" blocks → time-based checks using runtime.get_time()
- "module" blocks → @public function definitions

CONTRACT STRUCTURE:
1. Imports at top
2. Event definitions
3. Storage keys as constants (optional)
4. @public functions with proper decorators
5. Helper functions (can be private)

EXAMPLE PATTERN:
```python
from boa3.builtin import CreateNewEvent
from boa3.builtin.interop.storage import get, put
from boa3.builtin.interop.runtime import CheckWitness
from boa3.builtin.type import UInt160

# Events
TransferEvent = CreateNewEvent([('from', UInt160), ('to', UInt160), ('amount', int)])

# Storage keys
OWNER_KEY = b'owner'

@public
def _deploy(data: bytes, update: bool):
    if not update:
        owner = CheckWitness(...)  # Get deployer
        put(OWNER_KEY, owner)

@public
def transfer(to: UInt160, amount: int) -> bool:
    assert CheckWitness(get(OWNER_KEY)), "Unauthorized"
    # Transfer logic
    TransferEvent(get(OWNER_KEY), to, amount)
    return True
```

Output Format:
Return a JSON object with:
{
    "neo_python": "# Full Neo Boa Python contract code here",
    "contractName": "ContractName",
    "explanation": "Brief explanation of what the contract does",
    "functions": ["list", "of", "function", "names"],
    "events": ["list", "of", "event", "names"]
}

IMPORTANT: Return ONLY valid JSON, no markdown code blocks or extra text."""


class NeoContractAgent:
    """
    Agent that converts visual contract blocks into Neo Boa Python smart contracts.
    Uses the existing GeminiLLM for code generation.
    Based on Neo3-Boa patterns from: https://github.com/CityOfZion/neo3-boa
    """
    
    def __init__(self):
        """Initialize the Neo contract generation agent."""
        self.llm = GeminiLLM()
        self.system_prompt = NEO_SYSTEM_PROMPT
    
    def _parse_blocks(self, blocks: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse React Flow blocks and edges into a structured contract specification.
        Same structure as Solidity agent for consistency.
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
        prompt_parts = ["Generate a Neo Boa Python smart contract based on these visual blocks:\n"]
        
        if spec["parties"]:
            prompt_parts.append("\n## Parties (UInt160 addresses):")
            for party in spec["parties"]:
                prompt_parts.append(f"- {party['label']}: {party.get('subtitle') or party.get('content') or 'address'}")
        
        if spec["assets"]:
            prompt_parts.append("\n## Assets:")
            for asset in spec["assets"]:
                prompt_parts.append(f"- {asset['label']}: {asset.get('content', 'GAS')}")
        
        if spec["amounts"]:
            prompt_parts.append("\n## Payment Amounts:")
            for amount in spec["amounts"]:
                prompt_parts.append(f"- {amount['label']}: {amount.get('subtitle') or amount.get('content') or 'amount'}")
        
        if spec["conditions"]:
            prompt_parts.append("\n## Conditions (checkwitness/assertions):")
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
        
        prompt_parts.append("\n\nGenerate a complete, secure Neo Boa Python contract implementing this logic.")
        prompt_parts.append("Include proper imports, storage operations (get/put), events, checkwitness() for authorization,")
        prompt_parts.append("and all necessary @public functions following Neo Boa patterns.")
        prompt_parts.append("Return the result as a JSON object with 'neo_python', 'contractName', 'explanation', 'functions', and 'events' keys.")
        
        return "\n".join(prompt_parts)
    
    async def generate_neo_contract(
        self, 
        blocks: List[Dict[str, Any]], 
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate Neo Boa Python code from visual blocks and edges.
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
            if not result or not result.get("neo_python"):
                # If JSON parsing failed or no neo_python field, try plain chat and extract manually
                print("[NeoAgent] JSON parsing failed or incomplete, trying plain chat extraction")
                response = await self.llm.chat(
                    prompt=prompt,
                    system_prompt=self.system_prompt,
                    temperature=0.3,
                )
                # Try to extract JSON from the response
                extracted_json = self._try_extract_json_from_text(response)
                if extracted_json and extracted_json.get("neo_python"):
                    result = extracted_json
                else:
                    # Fallback: extract just the Python code
                    python_code = self._extract_python_code(response)
                    result = {
                        "neo_python": python_code,
                        "contractName": "GeneratedContract",
                        "explanation": "Neo smart contract generated from visual blocks",
                        "functions": self._extract_functions(python_code),
                        "events": self._extract_events(python_code),
                    }
            
            if "contractName" not in result:
                result["contractName"] = "GeneratedContract"
            if "explanation" not in result:
                result["explanation"] = "Neo smart contract generated from visual blocks"
            if "functions" not in result:
                result["functions"] = self._extract_functions(result.get("neo_python", ""))
            if "events" not in result:
                result["events"] = self._extract_events(result.get("neo_python", ""))
            
            return result
            
        except Exception as e:
            print(f"[NeoAgent] Error: {e}")
            return {
                "neo_python": f"# Error generating contract: {str(e)}",
                "contractName": "ErrorContract",
                "explanation": f"Failed to generate contract: {str(e)}",
                "functions": [],
                "events": [],
                "error": str(e),
            }
    
    def _try_extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Try to extract JSON object from text that might have markdown."""
        import json
        import re
        
        # Remove markdown code blocks
        text = text.strip()
        if text.startswith("```"):
            # Find the JSON code block
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
        
        # Try to find JSON object directly
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return None
    
    def _extract_python_code(self, text: str) -> str:
        """Extract Python code from response text."""
        # Try to find code blocks
        if "```python" in text:
            start = text.find("```python") + len("```python")
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
        
        # Look for Neo Boa imports as start of code
        if "from boa3.builtin" in text:
            start = text.find("from boa3.builtin")
            if start >= 0:
                return text[start:].strip()
        
        return text.strip()
    
    def _extract_functions(self, python_code: str) -> List[str]:
        """Extract function names from Neo Boa Python code."""
        # Look for @public decorator followed by def
        pattern = r'@public\s+def\s+(\w+)\s*\('
        matches = re.findall(pattern, python_code, re.MULTILINE)
        # Also look for regular def (in case decorator is on previous line)
        pattern2 = r'def\s+(\w+)\s*\('
        matches2 = re.findall(pattern2, python_code)
        # Combine and deduplicate
        all_matches = list(set(matches + matches2))
        # Filter out common Python built-ins
        filtered = [m for m in all_matches if not m.startswith('_')]
        return filtered
    
    def _extract_events(self, python_code: str) -> List[str]:
        """Extract event names from Neo Boa Python code."""
        # Look for CreateNewEvent assignments
        pattern = r'(\w+)\s*=\s*CreateNewEvent'
        matches = re.findall(pattern, python_code)
        return list(set(matches))


