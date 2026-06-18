from app.models.workflow_state import WorkflowState
from app.core.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate

def analyst_node(state: WorkflowState) -> dict:
    """
    Analyst Agent: Takes the schema and query, and generates a data strategy.
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Data Analyst. Your job is to analyze the provided database schema and the user's query, and output a detailed data strategy explaining how to approach answering the query."),
        ("human", "Schema:\n{raw_schema}\n\nUser Query:\n{user_query}\n\nProvide the data strategy:")
    ])
    
    chain = prompt | llm
    
    # Use standard dict access if state is passed as a dict, or attribute access if passed as a BaseModel
    # Depending on LangGraph version, it might be passed as a dict or object. We'll handle both.
    raw_schema = state.raw_schema if hasattr(state, "raw_schema") else state.get("raw_schema", {})
    user_query = state.user_query if hasattr(state, "user_query") else state.get("user_query", "")
    
    response = chain.invoke({
        "raw_schema": str(raw_schema),
        "user_query": user_query
    })
    
    return {"data_strategy": response.content}
