from langgraph.graph import StateGraph, END
from app.models.workflow_state import WorkflowState
from app.services.agents.analyst import analyst_node
from app.services.agents.planner import planner_node

def build_workflow():
    """
    Builds and compiles the LangGraph workflow for data analysis.
    """
    # Initialize the graph with the Pydantic State model
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("planner", planner_node)
    
    # Add edges
    workflow.set_entry_point("analyst")
    workflow.add_edge("analyst", "planner")
    
    # Temporarily end at planner for Sprint 2
    workflow.add_edge("planner", END)
    
    # Compile the graph
    return workflow.compile()

# Expose a compiled graph instance
compiled_graph = build_workflow()
