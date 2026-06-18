from langgraph.graph import StateGraph, END
from app.models.workflow_state import WorkflowState
from app.services.agents.analyst import analyst_node
from app.services.agents.planner import planner_node
from app.services.agents.coder import coder_node
from app.services.agents.executor import executor_node
from app.services.agents.reviewer import reviewer_node
from app.services.agents.synthesizer import synthesizer_node

MAX_RETRIES = 3

def route_execution(state: WorkflowState):
    """
    Conditional edge logic after execution.
    """
    execution_error = state.execution_error if hasattr(state, "execution_error") else state.get("execution_error")
    retry_count = state.retry_count if hasattr(state, "retry_count") else state.get("retry_count", 0)
    
    if not execution_error:
        # Success!
        return "synthesizer"
    
    if retry_count >= MAX_RETRIES:
        # Too many retries, stop to avoid infinite loops
        return END
        
    return "reviewer"

def build_workflow():
    """
    Builds and compiles the LangGraph workflow for data analysis.
    """
    # Initialize the graph with the Pydantic State model
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("synthesizer", synthesizer_node)
    
    # Add edges
    workflow.set_entry_point("analyst")
    workflow.add_edge("analyst", "planner")
    workflow.add_edge("planner", "coder")
    workflow.add_edge("coder", "executor")
    
    # Conditional routing based on execution success
    workflow.add_conditional_edges(
        "executor",
        route_execution,
        {
            "synthesizer": "synthesizer",
            "reviewer": "reviewer",
            END: END
        }
    )
    
    # Loop back to coder after reviewer feedback
    workflow.add_edge("reviewer", "coder")
    
    # End at Synthesizer
    workflow.add_edge("synthesizer", END)
    
    # Compile the graph
    return workflow.compile()

# Expose a compiled graph instance
compiled_graph = build_workflow()
