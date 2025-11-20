import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
import os


# 1. Page Config

st.set_page_config(page_title="ChatSQL Agent", page_icon="💬", layout="wide")
st.title("💬 SQL Chat Agent")
st.write("Chat with your database using natural language.")



# 2. OpenAI Key Input

openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key



# 3. Load Database

db_path = "Chinook.db"

if not os.path.exists(db_path):
    st.error("Chinook.db not found in this directory.")
    st.stop()

db = SQLDatabase.from_uri(f"sqlite:///{db_path}")


# 4. Load the SQL Agent (cached)

@st.cache_resource
def load_agent():
    llm = ChatOpenAI(model="gpt-4.1", temperature=0)

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True
    )

    return agent


if openai_api_key:
    agent = load_agent()



# 5. Initialize Chat History

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": "user/assistant", "content": "..."}
    


# 6. Display Past Chat Messages
#
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 7. Accept New User Query
user_msg = st.chat_input("Ask something about your database...")

if user_msg:

    # Store user message
    st.session_state.chat_history.append({"role": "user", "content": user_msg})

    # Display user message
    with st.chat_message("user"):
        st.write(user_msg)

    # Process through SQL Agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = agent.invoke({"input": user_msg})
                answer = response["output"]

                st.write(answer)

                # Store assistant response
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_message = f"Error: {str(e)}"
                st.error(error_message)

                st.session_state.chat_history.append({"role": "assistant", "content": error_message})
