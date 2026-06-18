from app.models.workflow_state import WorkflowState
from app.core.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate

def planner_node(state: WorkflowState) -> dict:
    """
    Planner Agent: Takes the data strategy and creates step-by-step instructions for the Coder.
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Technical Planner. Convert the provided Data Strategy into clear, step-by-step Python coding instructions for a Coder Agent. The code will be executed in a sandboxed environment using DuckDB and Pandas. Do not write the code yourself, just provide the logical steps."),
        ("human", "Data Strategy:\n{data_strategy}\n\nProvide the step-by-step plan:")
    ])
    
    chain = prompt | llm
    
    # Handle state either as dict or object depending on LangGraph version
    data_strategy = state.data_strategy if hasattr(state, "data_strategy") else state.get("data_strategy", "")
    
    response = chain.invoke({
        "data_strategy": data_strategy
    })
    
    return {"plan": response.content}
