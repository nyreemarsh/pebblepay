"""
Interactive Contract Assistant Test Loop
Tests the multi-agent workflow from the terminal.
"""
import asyncio
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.graph_workflow import create_contract_graph_agent, get_opening_message


def print_divider(char: str = "-", width: int = 60):
    """Print a divider line."""
    print(char * width)


def print_header():
    """Print the welcome header."""
    print_divider("=")
    print("🤝 CONTRACT ASSISTANT - Interactive Test")
    print_divider("=")
    print()
    print("Welcome! I'm your contract assistant. I'll help you create a")
    print("ROBUST freelance contract by asking important questions.")
    print()
    print("I'll gather:")
    print("  ✓ Party names and contact info")
    print("  ✓ Deliverables and payment details")
    print("  ✓ Timeline and revision policy")
    print("  ✓ What happens if things go wrong")
    print("  ✓ Dispute resolution process")
    print()
    print("Commands:")
    print("  - Type your responses naturally")
    print("  - Type 'debug' to see the current state")
    print("  - Type 'spec' to see the contract specification")
    print("  - Type 'contract' to see the generated contract (if ready)")
    print("  - Type 'summary' to see the summary (if ready)")
    print("  - Type 'missing' to see what info is still needed")
    print("  - Type 'quit' or 'exit' to leave")
    print()
    print("Let's get started!")
    print()
    print_divider()


def print_debug(state: dict):
    """Print debug information about the current state."""
    print("\n" + "=" * 60)
    print("DEBUG: Current State")
    print("=" * 60)
    
    # Show key state values
    print(f"\n📊 Questions asked: {state.get('questions_asked', 0)}")
    print(f"📋 Next action: {state.get('next_action', 'None')}")
    print(f"📝 Decision reason: {state.get('decision_reason', 'None')}")
    
    # Show missing fields
    missing = state.get("missing_fields", [])
    if missing:
        print(f"\n❓ Missing fields ({len(missing)}):")
        for field in missing[:10]:
            print(f"   - {field}")
        if len(missing) > 10:
            print(f"   ... and {len(missing) - 10} more")
    else:
        print("\n✅ No missing fields!")
    
    # Show if contract is ready
    if state.get("contract_text"):
        print("\n✅ Contract has been generated")
    if state.get("summary"):
        print("✅ Summary has been generated")
    
    print()
    print_divider("=")


def print_spec(state: dict):
    """Print the current contract specification."""
    spec = state.get("contract_spec", {})
    print("\n" + "=" * 60)
    print("CONTRACT SPECIFICATION")
    print("=" * 60)
    print(json.dumps(spec, indent=2, default=str))
    print("=" * 60 + "\n")


def print_contract(state: dict):
    """Print the generated contract."""
    contract = state.get("contract_text")
    if contract:
        print("\n" + "=" * 60)
        print("GENERATED CONTRACT")
        print("=" * 60)
        print(contract)
        print("=" * 60 + "\n")
    else:
        print("\n⚠️ Contract not yet generated. Keep answering questions!\n")


def print_summary(state: dict):
    """Print the contract summary."""
    summary = state.get("summary")
    if summary:
        print(f"\n📋 SUMMARY:\n{summary}\n")
    else:
        print("\n⚠️ Summary not yet generated.\n")


def print_missing(state: dict):
    """Print missing fields with their questions."""
    from app.contract_schema import get_field_question, get_field_priority
    
    missing = state.get("missing_fields", [])
    if not missing:
        print("\n✅ All required information has been gathered!\n")
        return
    
    print("\n" + "=" * 60)
    print(f"MISSING INFORMATION ({len(missing)} fields)")
    print("=" * 60)
    
    # Sort by priority
    sorted_missing = sorted(missing, key=get_field_priority)
    
    for i, field in enumerate(sorted_missing, 1):
        priority = get_field_priority(field)
        question = get_field_question(field)
        print(f"\n{i}. [{field}] (Priority: {priority})")
        print(f"   Q: {question}")
    
    print("\n" + "=" * 60 + "\n")


async def main():
    """Main chat loop."""
    print_header()
    
    # Create the agent
    agent = create_contract_graph_agent()
    
    # Print opening message
    print(f"\nA: {get_opening_message()}\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in {"quit", "exit", "q"}:
                print("\nGoodbye! 👋\n")
                break
            
            if user_input.lower() == "debug":
                print_debug(agent.state)
                continue
            
            if user_input.lower() == "spec":
                print_spec(agent.state)
                continue
            
            if user_input.lower() == "contract":
                print_contract(agent.state)
                continue
            
            if user_input.lower() == "summary":
                print_summary(agent.state)
                continue
            
            if user_input.lower() == "missing":
                print_missing(agent.state)
                continue
            
            # Run the agent with the user's message
            state = await agent.run(user_input)
            
            # Get the assistant's response
            assistant_msg = state.get("assistant_message", "")
            
            if assistant_msg:
                print(f"\nA: {assistant_msg}\n")
            else:
                # Fallback if no message
                if state.get("contract_text"):
                    print("\n✅ Contract generated! Type 'contract' to see it.\n")
                else:
                    print("\n(Processing...)\n")
            
            # Show hints
            if state.get("contract_text") and not state.get("_contract_shown"):
                print("[✓ Contract generated! Type 'contract' to see it, or 'summary' for a quick overview.]\n")
                agent.state["_contract_shown"] = True
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
