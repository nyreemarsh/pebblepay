"""
FastAPI routes for Neo smart contract generation and compilation.
"""
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..agents.neo_contract_generator_agent import NeoContractGeneratorAgent

router = APIRouter(prefix="/api/neo", tags=["neo-contracts"])

# Initialize the agent
agent = NeoContractGeneratorAgent()


class ContractSpecRequest(BaseModel):
    """Request model for contract generation."""
    contract_name: str
    actions: list
    additional_config: Optional[Dict[str, Any]] = None


class ContractGenerationResponse(BaseModel):
    """Response model for contract generation."""
    status: str
    contract_name: str
    file_path: str
    source_code: Optional[str] = None
    error: Optional[str] = None


class CompileContractRequest(BaseModel):
    """Request model for contract compilation."""
    contract_name: str


class CompileContractResponse(BaseModel):
    """Response model for contract compilation."""
    status: str
    contract_name: str
    nef_path: Optional[str] = None
    manifest_path: Optional[str] = None
    error: Optional[str] = None
    compiler_output: Optional[str] = None


@router.post("/generate_contract", response_model=ContractGenerationResponse)
async def generate_contract(request: ContractSpecRequest):
    """
    Generate a Neo smart contract from a JSON specification.
    
    Accepts a structured JSON description and generates a valid Neo Python contract
    that can be compiled with the Boa compiler.
    """
    try:
        # Convert request to JSON spec format
        json_spec = {
            "contract_name": request.contract_name,
            "actions": request.actions,
        }
        if request.additional_config:
            json_spec.update(request.additional_config)
        
        # Generate contract source code
        source_code = await agent.generate_contract_source(json_spec)
        
        # Save contract to file
        file_path = agent.save_contract(request.contract_name, source_code)
        
        return ContractGenerationResponse(
            status="success",
            contract_name=request.contract_name,
            file_path=str(file_path),
            source_code=source_code,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract generation failed: {str(e)}")


@router.post("/compile_contract", response_model=CompileContractResponse)
async def compile_contract(request: CompileContractRequest):
    """
    Compile a generated Neo contract using the Boa compiler.
    
    Runs `neo-boa contract.build` on the generated Python file and returns
    the resulting .nef and .manifest.json file paths.
    """
    try:
        # Find the contract file
        contracts_dir = agent.contracts_dir
        contract_file = contracts_dir / f"{request.contract_name}.py"
        
        if not contract_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Contract file not found: {contract_file}"
            )
        
        # Compile using neo-boa
        # Note: neo-boa CLI command is typically: boa3 build path/to/contract.py
        compile_command = [
            "python", "-m", "boa3", "build",
            str(contract_file)
        ]
        
        try:
            result = subprocess.run(
                compile_command,
                capture_output=True,
                text=True,
                cwd=str(contracts_dir),
                timeout=30,
            )
            
            compiler_output = result.stdout + result.stderr
            
            if result.returncode != 0:
                return CompileContractResponse(
                    status="error",
                    contract_name=request.contract_name,
                    error="Compilation failed",
                    compiler_output=compiler_output,
                )
            
            # Find generated files
            # Boa typically outputs: {name}.nef and {name}.manifest.json in the same directory
            nef_path = contract_file.with_suffix('.nef')
            manifest_path = contract_file.with_suffix('.manifest.json')
            
            # Check if files exist
            if not nef_path.exists():
                return CompileContractResponse(
                    status="error",
                    contract_name=request.contract_name,
                    error=f"Compilation succeeded but .nef file not found at {nef_path}",
                    compiler_output=compiler_output,
                )
            
            return CompileContractResponse(
                status="success",
                contract_name=request.contract_name,
                nef_path=str(nef_path) if nef_path.exists() else None,
                manifest_path=str(manifest_path) if manifest_path.exists() else None,
                compiler_output=compiler_output,
            )
        
        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=500,
                detail="Compilation timed out after 30 seconds"
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=500,
                detail="neo-boa compiler not found. Make sure boa3 is installed and in PATH."
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Compilation failed: {str(e)}"
        )


@router.get("/contracts")
async def list_contracts():
    """List all generated contract files."""
    contracts_dir = agent.contracts_dir
    contracts = []
    
    for file_path in contracts_dir.glob("*.py"):
        contracts.append({
            "name": file_path.stem,
            "file_path": str(file_path),
            "exists": file_path.exists(),
            "nef_exists": file_path.with_suffix('.nef').exists(),
            "manifest_exists": file_path.with_suffix('.manifest.json').exists(),
        })
    
    return {"contracts": contracts}


@router.get("/contracts/{contract_name}")
async def get_contract(contract_name: str):
    """Get the source code of a generated contract."""
    contracts_dir = agent.contracts_dir
    contract_file = contracts_dir / f"{contract_name}.py"
    
    if not contract_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Contract not found: {contract_name}"
        )
    
    with open(contract_file, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    return {
        "contract_name": contract_name,
        "source_code": source_code,
        "file_path": str(contract_file),
    }


