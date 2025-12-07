"""
SpoonOS Integration Adapter
Provides integration with SpoonOS agent protocol while maintaining compatibility.
"""
from typing import Dict, Any, Optional, Callable, Awaitable
import asyncio

# Try multiple import paths for SpoonOS
SPOONOS_AVAILABLE = False
SpoonStateGraph = None
SpoonGraphAgent = None
SpoonState = None

# Try different import paths
import_paths = [
    ("spoon_core.graph", "StateGraph"),
    ("spoon_core.agent", "GraphAgent"),
    ("spoon_core.types", "State"),
    ("spoon_ai.graph", "StateGraph"),
    ("spoon_ai.agent", "GraphAgent"),
    ("spoon_ai.types", "State"),
    ("spoon.graph", "StateGraph"),
    ("spoon.agent", "GraphAgent"),
    ("spoon.types", "State"),
]

for module_path, class_name in import_paths:
    try:
        module = __import__(module_path, fromlist=[class_name])
        if class_name == "StateGraph":
            SpoonStateGraph = getattr(module, class_name, None)
        elif class_name == "GraphAgent":
            SpoonGraphAgent = getattr(module, class_name, None)
        elif class_name == "State":
            SpoonState = getattr(module, class_name, None)
        
        if SpoonStateGraph and SpoonGraphAgent:
            SPOONOS_AVAILABLE = True
            break
    except ImportError:
        continue

if not SPOONOS_AVAILABLE:
    print("=" * 60)
    print("WARNING: SpoonOS not found!")
    print("=" * 60)
    print("To use SpoonOS, install it with:")
    print("  pip install git+https://github.com/XSpoonAi/spoon-core.git@main")
    print("")
    print("Or if available on PyPI:")
    print("  pip install spoon-ai")
    print("=" * 60)
    print("Falling back to custom implementation.")
    print("")


def create_spoonos_graph():
    """
    Create a SpoonOS StateGraph if available, otherwise return None.
    """
    if SPOONOS_AVAILABLE and SpoonStateGraph:
        try:
            # Try to create a SpoonOS graph
            # Note: Actual API may differ - adjust based on SpoonOS documentation
            return SpoonStateGraph()
        except Exception as e:
            print(f"Error creating SpoonOS graph: {e}")
            return None
    return None


def create_spoonos_agent(name: str, description: str, graph, initial_state: Optional[Dict[str, Any]] = None):
    """
    Create a SpoonOS GraphAgent if available.
    
    Args:
        name: Agent name
        description: Agent description
        graph: Compiled graph
        initial_state: Initial state dictionary
        
    Returns:
        SpoonOS agent if available, None otherwise
    """
    if SPOONOS_AVAILABLE and SpoonGraphAgent:
        try:
            # Try to create a SpoonOS agent
            # Note: Actual API may differ - adjust based on SpoonOS documentation
            return SpoonGraphAgent(
                name=name,
                description=description,
                graph=graph,
                initial_state=initial_state or {}
            )
        except Exception as e:
            print(f"Error creating SpoonOS agent: {e}")
            print("Falling back to custom implementation.")
            return None
    return None


# Export availability flag
__all__ = [
    "SPOONOS_AVAILABLE",
    "SpoonStateGraph",
    "SpoonGraphAgent",
    "create_spoonos_graph",
    "create_spoonos_agent",
]


