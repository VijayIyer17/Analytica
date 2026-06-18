from app.models.workflow_state import WorkflowState
from app.services.docker_sandbox import execute_code_in_sandbox
import os

def executor_node(state: WorkflowState) -> dict:
    """
    Executor Node: Runs the generated code inside the Docker sandbox.
    """
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data.duckdb'))
    
    generated_code = state.generated_code if hasattr(state, "generated_code") else state.get("generated_code", "")
    retry_count = (state.retry_count if hasattr(state, "retry_count") else state.get("retry_count", 0)) + 1
    
    # Run the code
    result = execute_code_in_sandbox(generated_code, db_path)
    
    if result["success"]:
        return {
            "final_output": result["stdout"],
            "execution_error": None,
            "retry_count": retry_count
        }
    else:
        return {
            "execution_error": result["stderr"],
            "retry_count": retry_count
        }
