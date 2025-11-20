import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents import AgentExecutor
import os

# -----------------------------
# 1. Page Configuration
# -----------------------------
st.set_page_config(page_title="SQL Agent Demo", page_icon="💡", layout="wide")

st.title("SQL Agent - Natural Language to SQL")
st.write("Ask questions about your database in plain English.")

# -----------------------------
# 2. Environment Variables
# -----------------------------
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key

# -----------------------------
# 3. Load Database
# -----------------------------
db_path = "Chinook.db"

if not os.path.exists(db_path):
    st.error("Chinook.db not found in this directory.")
else:
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# -----------------------------
# 4. Build LLM + SQL Agent
# -----------------------------
@st.cache_resource
def load_agent():
    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0
    )

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True
    )
    return agent

if openai_api_key:
    agent = load_agent()

# -----------------------------
# 5. User Query Input
# -----------------------------
query = st.text_input("Ask your question:", placeholder="e.g., How many tracks are there?")

if st.button("Run Query"):
    if not openai_api_key:
        st.error("Please enter your OpenAI API key.")
    elif not query:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = agent.invoke({"input": query})
                st.success("Answer:")
                st.write(response["output"])
            except Exception as e:
                st.error(f"Error: {str(e)}")
