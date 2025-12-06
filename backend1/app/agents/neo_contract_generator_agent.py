"""
Neo Contract Generator Agent
Converts structured JSON contract descriptions into valid Neo Python smart contracts using Boa compiler.
"""
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..llm import GeminiLLM


NEO_SYSTEM_PROMPT = """You generate NeoVM smart contracts in Python using Neo Boa (boa3).
Follow the official Neo Boa patterns from https://github.com/CityOfZion/neo3-boa

CRITICAL CONSTRAINTS:
- Output ONLY valid Python code compatible with Neo Boa compiler
- Use ONLY the NeoVM subset of Python supported by Boa
- NO f-strings, NO dynamic imports, NO advanced Python features unsupported by Boa
- NO classes unless absolutely necessary; prefer functional style
- Only use: `from boa3.builtin import ...` and allowed modules
- All public methods MUST use @public decorator (import from boa3.builtin)
- Use get() and put() directly (from boa3.builtin.interop.storage) for persistent storage
- Use call_contract() for NEP-17 token transfers (from boa3.builtin.interop.contract)
- Use CheckWitness() for signature verification (from boa3.builtin.interop.runtime)
- Use UInt160, UInt256, bytes, int types as appropriate

REQUIRED IMPORTS:
from boa3.builtin import public, CreateNewEvent
from boa3.builtin.interop.storage import get, put
from boa3.builtin.interop.runtime import CheckWitness
from boa3.builtin.type import UInt160, UInt256

STORAGE PATTERNS:
- Use: from boa3.builtin.interop.storage import get, put
- put(key, value) to store (NOT Storage.put())
- get(key) to retrieve (returns value or None)
- Keys should be bytes: put(b'key', value) or strings: put('key', value)
- Example: put(b'owner', owner_address)

TOKEN TRANSFERS:
- Use: from boa3.builtin.interop.contract import call_contract
- call_contract(contract_hash: UInt160, method: str, args: list)
- Contract hash should be UInt160

ACCESS CONTROL:
- Use: from boa3.builtin.interop.runtime import CheckWitness
- CheckWitness(address: UInt160) returns bool
- Store owner addresses as UInt160

EVENTS:
- Use: from boa3.builtin import CreateNewEvent
- CreateNewEvent(parameters: list, name: str)
- Example: on_payment = CreateNewEvent([('from', UInt160), ('to', UInt160), ('amount', int)])

OUTPUT FORMAT:
Return ONLY Python code. No explanations, no markdown, no code blocks.
Start directly with imports and code.

Example structure:
from boa3.builtin import public, CreateNewEvent
from boa3.builtin.interop.storage import get, put
from boa3.builtin.interop.runtime import CheckWitness
from boa3.builtin.type import UInt160

# Events
on_payment = CreateNewEvent(
    [('from', UInt160), ('to', UInt160), ('amount', int)]
)

@public
def deposit(sender: UInt160, amount: int) -> bool:
    put(b'sender', sender)
    put(b'amount', amount)
    return True

@public
def withdraw(recipient: UInt160) -> bool:
    amount = get(b'amount')
    if amount:
        put(b'recipient', recipient)
        return True
    return False
"""


class NeoContractGeneratorAgent:
    """
    Agent that converts structured JSON contract descriptions into Neo Python smart contracts.
    Uses GeminiLLM for code generation and validates output.
    """
    
    def __init__(self):
        """Initialize the Neo contract generator agent."""
        self.llm = GeminiLLM()
        # Contracts directory is at backend/contracts
        backend_dir = Path(__file__).parent.parent.parent
        self.contracts_dir = backend_dir / "contracts"
        self.contracts_dir.mkdir(exist_ok=True)
    
    async def generate_contract_source(self, json_spec: Dict[str, Any]) -> str:
        """
        Convert JSON contract specification into Neo Python smart contract source code.
        
        Args:
            json_spec: Dictionary containing contract structure:
                {
                    "contract_name": "EscrowContract",
                    "actions": [
                        {
                            "type": "store_value",
                            "key": "sender",
                            "value_type": "UInt160"
                        },
                        {
                            "type": "release_payment",
                            "from": "sender",
                            "to": "recipient",
                            "amount_key": "amount"
                        }
                    ]
                }
        
        Returns:
            Python source code string for the Neo contract
        """
        # Build user prompt from JSON spec
        user_prompt = self._build_prompt_from_json(json_spec)
        
        # Generate contract code
        contract_code = await self.llm.chat(
            prompt=user_prompt,
            system_prompt=NEO_SYSTEM_PROMPT,
            temperature=0.3,  # Lower temperature for more deterministic code
        )
        
        # Clean up the response (remove markdown if present)
        contract_code = self._clean_code_response(contract_code)
        
        # Validate basic structure
        self._validate_contract_code(contract_code)
        
        return contract_code
    
    def _build_prompt_from_json(self, json_spec: Dict[str, Any]) -> str:
        """Build a user prompt from the JSON specification."""
        contract_name = json_spec.get("contract_name", "Contract")
        actions = json_spec.get("actions", [])
        
        prompt_parts = [
            f"Generate a Neo smart contract named '{contract_name}' with the following actions:",
            ""
        ]
        
        for i, action in enumerate(actions, 1):
            action_type = action.get("type", "unknown")
            prompt_parts.append(f"{i}. {action_type}")
            
            if action_type == "store_value":
                key = action.get("key", "")
                value_type = action.get("value_type", "Any")
                prompt_parts.append(f"   - Store value with key '{key}' of type {value_type}")
            
            elif action_type == "release_payment":
                from_key = action.get("from", "")
                to_key = action.get("to", "")
                amount_key = action.get("amount_key", "")
                prompt_parts.append(
                    f"   - Release payment from '{from_key}' to '{to_key}' "
                    f"using amount stored in '{amount_key}'"
                )
            
            elif action_type == "check_condition":
                condition = action.get("condition", "")
                prompt_parts.append(f"   - Check condition: {condition}")
            
            elif action_type == "transfer_token":
                token_contract = action.get("token_contract", "")
                from_key = action.get("from", "")
                to_key = action.get("to", "")
                amount_key = action.get("amount_key", "")
                prompt_parts.append(
                    f"   - Transfer NEP-17 token from contract '{token_contract}' "
                    f"from '{from_key}' to '{to_key}' using amount in '{amount_key}'"
                )
            
            prompt_parts.append("")
        
        prompt_parts.append(
            "Generate the complete Neo Python contract code with all necessary imports, "
            "events, storage operations, and @public methods."
        )
        
        return "\n".join(prompt_parts)
    
    def _clean_code_response(self, code: str) -> str:
        """Remove markdown code blocks and clean up the response."""
        code = code.strip()
        
        # Remove markdown code blocks
        if code.startswith("```python"):
            code = code[9:].strip()
        elif code.startswith("```"):
            code = code[3:].strip()
        
        if code.endswith("```"):
            code = code[:-3].strip()
        
        return code
    
    def _validate_contract_code(self, code: str) -> None:
        """Basic validation of contract code structure."""
        if not code:
            raise ValueError("Generated contract code is empty")
        
        # Check for required imports
        if "from boa3.builtin" not in code:
            raise ValueError("Contract code must import from boa3.builtin")
        
        # Check for at least one @public method
        if "@public" not in code:
            raise ValueError("Contract must have at least one @public method")
        
        # Check for basic syntax (no f-strings)
        if 'f"' in code or "f'" in code:
            raise ValueError("Contract code contains f-strings, which are not supported by Boa")
    
    def save_contract(self, contract_name: str, source_code: str) -> Path:
        """
        Save the generated contract source code to a file.
        
        Args:
            contract_name: Name of the contract (without .py extension)
            source_code: Python source code string
        
        Returns:
            Path to the saved file
        """
        # Sanitize contract name
        safe_name = "".join(c for c in contract_name if c.isalnum() or c in ('_', '-')).strip()
        if not safe_name:
            safe_name = "Contract"
        
        file_path = self.contracts_dir / f"{safe_name}.py"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(source_code)
        
        return file_path

