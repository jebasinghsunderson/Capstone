import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from memory import get_memory
from tools import toolkit
from gmail_tools import get_gmail_tools
from drive_tools import drive_tools

def get_secret(key: str, default: str = None) -> str:
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

def get_agent():
    groq_api_key = get_secret("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not configured in Streamlit Secrets or environment variables.")

    model_name = get_secret("GROQ_MODEL", "llama-3.3-70b-versatile")

    llm = ChatGroq(
        model=model_name,
        api_key=groq_api_key
    )

    memory = get_memory()

    all_tools = (
        toolkit
        + get_gmail_tools()
        + drive_tools
    )

    return create_agent(
        model=llm,
        tools=all_tools,
        checkpointer=memory
    )

def ask_agent(question, thread_id="hari"):
    try:
        agent = get_agent()
        events = agent.stream(
            {
                "messages": [
                    (
                        "user",
                        question
                    )
                ]
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            },
            stream_mode="values"
        )

        answer = ""
        for event in events:
            answer = event["messages"][-1].content
        return answer
    except Exception as e:
        return f"⚠️ Agent Error: {str(e)}"