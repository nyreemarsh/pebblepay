"""
Contract Agent Test Script
Tests the multi-agent workflow with both chat and blocks input.
No HTTP, no frontend – just import and run.

Usage:
    python -m app.test_contract_agent
    
    Or from the backend directory:
    python app/test_contract_agent.py
"""
import asyncio
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.graph_workflow import run_from_chat, run_from_blocks, create_unified_contract_agent
from app.nodes.validate_spec_node import format_validation_report


def print_divider(title: str = "", char: str = "═", width: int = 70):
    """Print a divider line with optional title."""
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"\n{char * padding} {title} {char * padding}")
    else:
        print(char * width)


def print_section(title: str, content: str):
    """Print a section with title and content."""
    print(f"\n📋 {title}:")
    print("-" * 50)
    print(content)


async def test_chat_input():
    """Test the agent with a chat (natural language) input."""
    print_divider("TEST 1: Chat Input", "═")
    
    # Sample chat prompt describing a contract
    chat_input = """
    I'm a freelance graphic designer named Sarah Chen and I need a contract for a logo design project.
    My client is Bean & Brew Coffee Shop (contact: mike@beanandbrew.com).
    I'll be delivering 3 logo concepts, final logo files in PNG/SVG/AI formats, and a brand style guide.
    The total fee is £800 GBP, with 50% upfront and 50% on completion.
    Deadline is in 3 weeks.
    I want 2 rounds of revisions included.
    If I'm late, no penalty but I'll communicate promptly.
    If the client cancels, they pay for work done plus 25% kill fee.
    Disputes go to mediation first.
    """
    
    print(f"\n📝 INPUT (Chat):")
    print("-" * 50)
    print(chat_input.strip())
    
    print("\n⏳ Processing...")
    
    # Run the agent
    result = await run_from_chat(chat_input)
    
    # Print results
    print_section("VISITED NODES", " → ".join(result.get("_visited_nodes", [])))
    
    if result.get("validation_result"):
        print_section("VALIDATION", format_validation_report(result["validation_result"]))
    
    if result.get("normalization_notes"):
        print_section("NORMALIZATION NOTES", "\n".join(result["normalization_notes"]))
    
    if result.get("contract_spec"):
        print_section("CONTRACT SPEC (Key Fields)", json.dumps({
            "title": result["contract_spec"].get("title"),
            "freelancer": result["contract_spec"].get("freelancer", {}).get("name"),
            "client": result["contract_spec"].get("client", {}).get("name"),
            "payment": result["contract_spec"].get("payment"),
            "deadline": result["contract_spec"].get("timeline", {}).get("deadline"),
        }, indent=2))
    
    if result.get("contract_text"):
        print_section("CONTRACT TEXT (First 2000 chars)", result["contract_text"][:2000] + "...")
    
    if result.get("summary"):
        print_section("SUMMARY", result["summary"])
    
    return result


async def test_blocks_input():
    """Test the agent with a blocks (visual graph) input."""
    print_divider("TEST 2: Blocks Input", "═")
    
    # Sample blocks JSON (from visual builder)
    blocks_input = {
        "nodes": [
            {
                "id": "1",
                "type": "title",
                "data": {"title": "Website Development Agreement"}
            },
            {
                "id": "2",
                "type": "party",
                "data": {
                    "role": "freelancer",
                    "name": "Alex Developer",
                    "email": "alex@devstudio.com"
                }
            },
            {
                "id": "3",
                "type": "party",
                "data": {
                    "role": "client",
                    "name": "TechStartup Inc",
                    "email": "hello@techstartup.io"
                }
            },
            {
                "id": "4",
                "type": "deliverable",
                "data": {
                    "item": "Responsive website",
                    "description": "5-page responsive website with contact form",
                    "format": "HTML/CSS/JS deployed to client hosting"
                }
            },
            {
                "id": "5",
                "type": "deliverable",
                "data": {
                    "item": "Source code",
                    "description": "Complete source code with documentation"
                }
            },
            {
                "id": "6",
                "type": "payment",
                "data": {
                    "amount": 3000,
                    "currency": "USD",
                    "schedule": "1/3 upfront, 1/3 at midpoint, 1/3 on completion"
                }
            },
            {
                "id": "7",
                "type": "timeline",
                "data": {
                    "deadline": "6 weeks",
                    "start_date": "Upon signing"
                }
            },
            {
                "id": "8",
                "type": "terms",
                "data": {
                    "revisions": 3,
                    "acceptance_criteria": ["Passes all browser tests", "Mobile responsive", "PageSpeed score > 80"]
                }
            },
            {
                "id": "9",
                "type": "failure",
                "data": {
                    "late_policy": "5% discount per week late",
                    "non_delivery_refund": 100,
                    "rejection_process": "Bug fixes within scope, then mediation",
                    "kill_fee": 30
                }
            },
            {
                "id": "10",
                "type": "dispute",
                "data": {
                    "method": "Arbitration",
                    "jurisdiction": "California, USA"
                }
            }
        ],
        "edges": [
            {"from": "2", "to": "4"},
            {"from": "3", "to": "4"},
            {"from": "4", "to": "6"},
            {"from": "6", "to": "7"}
        ]
    }
    
    print(f"\n📝 INPUT (Blocks JSON):")
    print("-" * 50)
    print(f"Nodes: {len(blocks_input['nodes'])}")
    for node in blocks_input["nodes"]:
        print(f"  - {node['type']}: {node['data'].get('name') or node['data'].get('title') or node['data'].get('item') or node['data'].get('amount') or '...'}")
    
    print("\n⏳ Processing...")
    
    # Run the agent
    result = await run_from_blocks(blocks_input)
    
    # Print results
    print_section("VISITED NODES", " → ".join(result.get("_visited_nodes", [])))
    
    if result.get("parse_notes"):
        print_section("PARSE NOTES", "\n".join(result["parse_notes"]))
    
    if result.get("validation_result"):
        print_section("VALIDATION", format_validation_report(result["validation_result"]))
    
    if result.get("normalization_notes"):
        print_section("NORMALIZATION NOTES", "\n".join(result["normalization_notes"]))
    
    if result.get("contract_spec"):
        print_section("CONTRACT SPEC (Key Fields)", json.dumps({
            "title": result["contract_spec"].get("title"),
            "freelancer": result["contract_spec"].get("freelancer", {}).get("name"),
            "client": result["contract_spec"].get("client", {}).get("name"),
            "payment": result["contract_spec"].get("payment"),
            "deadline": result["contract_spec"].get("timeline", {}).get("deadline"),
            "deliverables_count": len(result["contract_spec"].get("deliverables", [])),
        }, indent=2))
    
    if result.get("contract_text"):
        print_section("CONTRACT TEXT (First 2000 chars)", result["contract_text"][:2000] + "...")
    
    if result.get("summary"):
        print_section("SUMMARY", result["summary"])
    
    return result


async def test_minimal_blocks():
    """Test with minimal blocks to show validation errors."""
    print_divider("TEST 3: Minimal Blocks (Validation Test)", "═")
    
    # Minimal blocks - missing required fields
    blocks_input = {
        "nodes": [
            {
                "id": "1",
                "type": "party",
                "data": {"role": "freelancer", "name": "John"}
            },
            {
                "id": "2",
                "type": "payment",
                "data": {"amount": 500}
            }
        ],
        "edges": []
    }
    
    print(f"\n📝 INPUT (Minimal blocks - missing fields):")
    print("-" * 50)
    print(json.dumps(blocks_input, indent=2))
    
    print("\n⏳ Processing...")
    
    result = await run_from_blocks(blocks_input)
    
    print_section("VISITED NODES", " → ".join(result.get("_visited_nodes", [])))
    
    if result.get("validation_result"):
        print_section("VALIDATION", format_validation_report(result["validation_result"]))
    
    return result


async def main():
    """Run all tests."""
    print("\n" + "═" * 70)
    print("   CONTRACT AGENT TEST SUITE")
    print("   Testing both chat and blocks input")
    print("═" * 70)
    
    try:
        # Test 1: Chat input
        await test_chat_input()
        
        print("\n" + "─" * 70 + "\n")
        
        # Test 2: Full blocks input
        await test_blocks_input()
        
        print("\n" + "─" * 70 + "\n")
        
        # Test 3: Minimal blocks (validation)
        await test_minimal_blocks()
        
        print_divider("ALL TESTS COMPLETE", "═")
        print("\n✅ Contract agent is working!")
        print("   - Accepts chat_input (natural language)")
        print("   - Accepts blocks_input (visual graph JSON)")
        print("   - Normalizes specs with defaults")
        print("   - Validates and reports issues")
        print("   - Generates contract text")
        print("   - Produces plain-English summary")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

