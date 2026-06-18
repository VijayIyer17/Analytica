from pydantic import BaseModel
from typing import Optional, Dict, Any

class WorkflowState(BaseModel):
    """
    Pydantic model representing the State in LangGraph.
    """
    raw_schema: Dict[str, Any]
    user_query: str
    data_strategy: Optional[str] = None
    plan: Optional[str] = None
    generated_code: Optional[str] = None
    execution_error: Optional[str] = None
    final_output: Optional[str] = None
