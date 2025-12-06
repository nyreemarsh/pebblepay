"""
State Graph and Graph Agent Implementation
A simplified implementation inspired by LangGraph/SpoonOS patterns.
"""
from typing import Dict, Any, Callable, Optional, List, Awaitable
import asyncio


NodeFunction = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
ConditionFunction = Callable[[Dict[str, Any]], str]


class StateGraph:
    """
    A state machine graph for defining agent workflows.
    
    Nodes are async functions that take state and return state updates.
    Edges define the flow between nodes.
    Conditional edges allow dynamic routing based on state.
    """
    
    def __init__(self):
        self.nodes: Dict[str, NodeFunction] = {}
        self.edges: Dict[str, str] = {}  # source -> destination
        self.conditional_edges: Dict[str, tuple] = {}  # source -> (condition_fn, mapping)
        self.entry_point: Optional[str] = None
        self.terminal_nodes: set = set()
    
    def add_node(self, name: str, func: NodeFunction) -> None:
        """Add a node to the graph."""
        self.nodes[name] = func
    
    def add_edge(self, source: str, destination: str) -> None:
        """Add a direct edge between nodes."""
        self.edges[source] = destination
    
    def add_conditional_edges(
        self,
        source: str,
        condition: ConditionFunction,
        mapping: Dict[str, str],
    ) -> None:
        """Add conditional edges from a node."""
        self.conditional_edges[source] = (condition, mapping)
    
    def set_entry_point(self, node: str) -> None:
        """Set the starting node."""
        self.entry_point = node
    
    def mark_terminal(self, node: str) -> None:
        """Mark a node as terminal (ends execution)."""
        self.terminal_nodes.add(node)
    
    def compile(self) -> "CompiledGraph":
        """Compile the graph for execution."""
        return CompiledGraph(
            nodes=self.nodes.copy(),
            edges=self.edges.copy(),
            conditional_edges=self.conditional_edges.copy(),
            entry_point=self.entry_point,
            terminal_nodes=self.terminal_nodes.copy(),
        )


class CompiledGraph:
    """A compiled graph ready for execution."""
    
    def __init__(
        self,
        nodes: Dict[str, NodeFunction],
        edges: Dict[str, str],
        conditional_edges: Dict[str, tuple],
        entry_point: Optional[str],
        terminal_nodes: set,
    ):
        self.nodes = nodes
        self.edges = edges
        self.conditional_edges = conditional_edges
        self.entry_point = entry_point
        self.terminal_nodes = terminal_nodes
    
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the graph starting from the entry point.
        
        Args:
            state: The initial state dictionary
            
        Returns:
            The final state after execution
        """
        if not self.entry_point:
            raise ValueError("No entry point defined")
        
        current_node = self.entry_point
        visited = []  # Track visited nodes to prevent infinite loops
        max_iterations = 20  # Safety limit
        
        for _ in range(max_iterations):
            if current_node not in self.nodes:
                raise ValueError(f"Node '{current_node}' not found in graph")
            
            visited.append(current_node)
            
            # Execute the current node
            node_func = self.nodes[current_node]
            try:
                updates = await node_func(state)
                
                # Merge updates into state
                if updates:
                    state.update(updates)
            
            except Exception as e:
                print(f"[Graph] Error in node '{current_node}': {e}")
                # Continue execution but note the error
                state["_last_error"] = str(e)
            
            # Determine next node
            next_node = self._get_next_node(current_node, state)
            
            if next_node is None:
                # No next node - we're done
                break
            
            current_node = next_node
        
        state["_visited_nodes"] = visited
        return state
    
    def _get_next_node(self, current: str, state: Dict[str, Any]) -> Optional[str]:
        """Determine the next node to execute."""
        # Check for direct edge first
        if current in self.edges:
            return self.edges[current]
        
        # Check for conditional edge
        if current in self.conditional_edges:
            condition_fn, mapping = self.conditional_edges[current]
            result = condition_fn(state)
            if result in mapping:
                return mapping[result]
            else:
                print(f"[Graph] Condition returned '{result}' but no mapping found")
                return None
        
        # No edge found - terminal node
        return None


class GraphAgent:
    """
    An agent that executes a state graph with persistent state across turns.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        graph: CompiledGraph,
        initial_state: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.description = description
        self.graph = graph
        self.state = initial_state.copy() if initial_state else {}
        self.turn_count = 0
    
    async def run(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user message through the graph.
        
        Args:
            user_input: The user's message
            
        Returns:
            The updated state after processing
        """
        # Update state with new input
        self.state["input"] = user_input
        self.turn_count += 1
        self.state["_turn"] = self.turn_count
        
        # Run the graph
        self.state = await self.graph.run(self.state)
        
        return self.state
    
    def reset(self, initial_state: Optional[Dict[str, Any]] = None) -> None:
        """Reset the agent state."""
        self.state = initial_state.copy() if initial_state else {}
        self.turn_count = 0
