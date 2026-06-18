from app.models.workflow_state import WorkflowState
from app.core.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate

def synthesizer_node(state: WorkflowState) -> dict:
    """
    Synthesizer Agent: Formats the final execution output into a professional markdown summary.
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an Expert Data Communicator. The user asked a question, and the data was analyzed using Python. Summarize the analytical results clearly and professionally in Markdown format. Focus on answering the user's question directly and concisely."),
        ("human", "User Query:\n{user_query}\n\nExecution Output:\n{final_output}\n\nProvide the final Markdown summary:")
    ])
    
    chain = prompt | llm
    
    user_query = state.user_query if hasattr(state, "user_query") else state.get("user_query", "")
    final_output = state.final_output if hasattr(state, "final_output") else state.get("final_output", "")
    
    response = chain.invoke({
        "user_query": user_query,
        "final_output": final_output
    })
    
    # Overwrite final_output with the synthesized markdown
    return {"final_output": response.content}
