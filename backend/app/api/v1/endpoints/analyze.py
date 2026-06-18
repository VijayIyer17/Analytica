import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.workflow import compiled_graph
from app.services.duckdb_service import extract_schema

router = APIRouter()

class AnalyzeRequest(BaseModel):
    table_name: str
    user_query: str

async def generate_workflow_stream(table_name: str, user_query: str):
    try:
        # Extract schema from DuckDB to feed to the state
        schema_info = extract_schema(table_name)
        raw_schema = schema_info.model_dump()
        
        initial_state = {
            "raw_schema": raw_schema,
            "user_query": user_query,
            "retry_count": 0
        }
        
        # Stream the workflow execution asynchronously
        async for event in compiled_graph.astream(initial_state):
            # event is a dict mapping node_name to state_updates
            for node_name, state_update in event.items():
                payload = {
                    "node": node_name,
                    "status": "completed",
                }
                
                # Send partial state back selectively
                if node_name == "synthesizer" and "final_output" in state_update:
                    payload["final_output"] = state_update["final_output"]
                elif node_name == "executor" and state_update.get("execution_error"):
                    payload["error"] = state_update["execution_error"]
                    payload["status"] = "error"
                    
                yield f"data: {json.dumps(payload)}\n\n"
                
        # Send a final complete event
        yield f"data: {json.dumps({'node': 'workflow', 'status': 'complete'})}\n\n"
        
    except Exception as e:
        error_payload = {"node": "system", "status": "error", "error": str(e)}
        yield f"data: {json.dumps(error_payload)}\n\n"

@router.post("/analyze")
async def analyze_data(request: AnalyzeRequest):
    """
    Triggers the Agentic workflow via Server-Sent Events (SSE).
    """
    if not request.table_name or not request.user_query:
        raise HTTPException(status_code=400, detail="Table name and query are required.")
        
    return StreamingResponse(
        generate_workflow_stream(request.table_name, request.user_query),
        media_type="text/event-stream"
    )
