# SpoonOS Conversion Guide

This document explains the conversion to SpoonOS agent protocol and what may need adjustment.

## Status

The backend has been converted to **attempt to use SpoonOS** when available. The code will:
1. Try to import SpoonOS from multiple possible paths
2. Use SpoonOS if found
3. Fall back to custom implementation if SpoonOS is not available

## Installation

To use SpoonOS, install it with:

```bash
pip install git+https://github.com/XSpoonAi/spoon-core.git@main
```

Or if available on PyPI:

```bash
pip install spoon-ai
```

## What Was Changed

### 1. `state_graph.py`
- Now attempts to import SpoonOS classes
- Falls back to custom implementation if not available
- Maintains backward compatibility with existing code

### 2. `graph_workflow.py`
- Updated to work with SpoonOS when available
- Maintains same API for agent creation

### 3. `requirements.txt`
- Already includes spoon-core from GitHub

## Potential Adjustments Needed

Since the exact SpoonOS API structure is not fully known, you may need to adjust:

### Import Paths
The code tries these import paths:
- `spoon_core.graph.StateGraph`
- `spoon_core.agent.GraphAgent`
- `spoon_ai.graph.StateGraph`
- `spoon_ai.agent.GraphAgent`
- `spoon.graph.StateGraph`
- `spoon.agent.GraphAgent`

**If SpoonOS uses different import paths**, update `state_graph.py` accordingly.

### Graph API
The code assumes SpoonOS has:
- `StateGraph()` constructor
- `add_node(name, func)` method
- `add_edge(source, destination)` method
- `add_conditional_edges(source, condition, mapping)` method
- `set_entry_point(node)` method
- `compile()` method that returns a compiled graph

**If SpoonOS uses different methods**, update the code in `state_graph.py` and `graph_workflow.py`.

### Agent API
The code assumes SpoonOS agents have:
- Constructor: `GraphAgent(name, description, graph, initial_state)`
- Method: `async def run(user_input) -> state`

**If SpoonOS uses different agent API**, update `state_graph.py` and `graph_workflow.py`.

### State Management
The code assumes state is a `Dict[str, Any]` that flows through nodes.

**If SpoonOS uses a different state type** (e.g., Pydantic models), you'll need to:
1. Update node functions to work with SpoonOS state type
2. Convert between dict and SpoonOS state type as needed

## Testing

After installing SpoonOS:

1. Check if it's detected:
   ```python
   from app.state_graph import SPOONOS_AVAILABLE
   print(f"SpoonOS available: {SPOONOS_AVAILABLE}")
   ```

2. Test agent creation:
   ```python
   from app.graph_workflow import create_chat_contract_agent
   agent = create_chat_contract_agent()
   print(f"Agent created: {agent.name}")
   ```

3. Test agent execution:
   ```python
   state = await agent.run("I'm designing a logo for a client")
   print(f"Contract spec: {state.get('contract_spec')}")
   ```

## Current Implementation

The current code maintains **full backward compatibility**. If SpoonOS is not installed, it uses the custom implementation that was already working.

## Next Steps

1. **Install SpoonOS** from the GitHub repo
2. **Test the imports** - check if SpoonOS is detected
3. **Adjust API calls** if SpoonOS uses different method names
4. **Test agent execution** to ensure it works correctly
5. **Update node functions** if SpoonOS requires different state types

## Getting Help

If you encounter issues:
1. Check the SpoonOS documentation: https://github.com/XSpoonAi/spoon-core
2. Verify the import paths match SpoonOS's actual structure
3. Check SpoonOS examples for correct API usage
4. The fallback implementation will continue to work if SpoonOS integration needs adjustment


