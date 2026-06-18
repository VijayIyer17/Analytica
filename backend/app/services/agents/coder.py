from app.models.workflow_state import WorkflowState
from app.core.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate

def coder_node(state: WorkflowState) -> dict:
    """
    Coder Agent: Generates Python/Pandas/DuckDB code.
    """
    llm = get_llm()
    
    system_msg = """You are an Expert Python Coder. 
Your job is to write Python code using Pandas and DuckDB based on the Planner's instructions.
The code will be executed in a Docker sandbox.
The DuckDB database is located at `/data/data.duckdb` and the table name is provided in the schema.
Only output the raw Python code. Do not include markdown formatting like ```python. Do not output anything other than code. Make sure your code prints the final analytical output to stdout.
Remember to indent everything correctly as it will be placed inside a try-except block."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "Plan:\n{plan}\n\nSchema:\n{raw_schema}\n\nReviewer Feedback (if any):\n{reviewer_feedback}\n\nWrite the Python code:")
    ])
    
    chain = prompt | llm
    
    plan = state.plan if hasattr(state, "plan") else state.get("plan", "")
    raw_schema = state.raw_schema if hasattr(state, "raw_schema") else state.get("raw_schema", {})
    reviewer_feedback = state.reviewer_feedback if hasattr(state, "reviewer_feedback") else state.get("reviewer_feedback", "None")
    
    response = chain.invoke({
        "plan": plan,
        "raw_schema": str(raw_schema),
        "reviewer_feedback": reviewer_feedback
    })
    
    # Strip markdown if LLM includes it
    code = response.content
    if code.startswith("```python"):
        code = code[9:]
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
        
    # Indent code by 4 spaces so it fits in the try block of the sandbox script
    indented_code = "\n".join(["    " + line for line in code.strip().split("\n")])
    
    return {"generated_code": indented_code}
