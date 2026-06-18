import streamlit as st
import requests
import json

BACKEND_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Auto-Analytica", page_icon="📊", layout="wide")

st.title("📊 Auto-Analytica")
st.markdown("Your Agentic AI-powered Data Analysis Assistant.")

# Initialize session state
if "table_name" not in st.session_state:
    st.session_state.table_name = None
if "schema_info" not in st.session_state:
    st.session_state.schema_info = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar: File Upload ---
with st.sidebar:
    st.header("1. Upload Data")
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xls", "xlsx"])
    
    if uploaded_file is not None and st.button("Upload"):
        with st.spinner("Uploading and analyzing schema..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post(f"{BACKEND_URL}/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.table_name = data["table_name"]
                st.session_state.schema_info = data["schema_info"]
                st.success("File successfully uploaded and loaded into DuckDB!")
            else:
                st.error(f"Error uploading file: {response.text}")
                
    if st.session_state.schema_info:
        st.subheader("Data Schema")
        st.json(st.session_state.schema_info["columns"])
        
        st.subheader("Sample Data")
        st.json(st.session_state.schema_info["sample_data"])

# --- Main Area: Chat Interface ---
st.header("2. Ask Questions & Analyze")

# Display Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your data..."):
    if not st.session_state.table_name:
        st.warning("Please upload a dataset first using the sidebar.")
    else:
        # Append to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            status_text = st.empty()
            response_container = st.empty()
            
            # Context window logic for "Chat with Chart"
            context = ""
            if len(st.session_state.chat_history) > 1:
                context = "Previous Conversation Context:\n"
                for msg in st.session_state.chat_history[-3:-1]:
                    context += f"{msg['role'].capitalize()}: {msg['content']}\n"
                
            full_query = f"{context}\nCurrent Query: {prompt}" if context else prompt
            
            payload = {
                "table_name": st.session_state.table_name,
                "user_query": full_query
            }
            
            status_text.markdown("🔄 Initializing Agents...")
            
            try:
                # Stream the SSE response
                with requests.post(f"{BACKEND_URL}/analyze", json=payload, stream=True) as r:
                    r.raise_for_status()
                    
                    final_md = ""
                    for line in r.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith("data: "):
                                data_str = decoded_line[6:]
                                try:
                                    event_data = json.loads(data_str)
                                    node = event_data.get("node", "")
                                    status = event_data.get("status", "")
                                    
                                    if status == "error":
                                        status_text.error(f"Error in {node}: {event_data.get('error')}")
                                    else:
                                        # Visual Agent Feedback
                                        emoji_map = {
                                            "analyst": "🧠",
                                            "planner": "📋",
                                            "coder": "💻",
                                            "executor": "⚙️",
                                            "reviewer": "👀",
                                            "synthesizer": "✍️"
                                        }
                                        emoji = emoji_map.get(node, "🤖")
                                        
                                        status_text.markdown(f"{emoji} **Agent Active:** `{node.capitalize()}` is working...")
                                        
                                        if node == "synthesizer" and "final_output" in event_data:
                                            final_md = event_data["final_output"]
                                            response_container.markdown(final_md)
                                            
                                        if node == "workflow" and status == "complete":
                                            status_text.empty()
                                            
                                except json.JSONDecodeError:
                                    pass
                                    
                    if final_md:
                        st.session_state.chat_history.append({"role": "assistant", "content": final_md})
                    else:
                        st.error("The workflow ended without generating a final output.")
                        
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to backend: {e}")
