import os
import requests
import wikipedia
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key: str, default: str = None) -> str:
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain_experimental.tools import PythonREPLTool

search_tool = DuckDuckGoSearchRun(
    description="Search current information"
)

wikipedia.set_user_agent(
    "AgenticAITraining"
)

wiki_api = WikipediaAPIWrapper()

wiki_tool = WikipediaQueryRun(
    api_wrapper=wiki_api
)

@tool
def weather_tool(city: str) -> str:
    """
    Returns weather information.
    """
    api_key = get_secret("OPENWEATHER_API_KEY")

    if not api_key:
        return "OpenWeather API Key is not configured in environment or Streamlit Secrets."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return "Weather Not Found"

        data = response.json()
        return f"""
City : {city}

Temperature : {data["main"]["temp"]}°C

Humidity : {data["main"]["humidity"]}%

Condition : {data["weather"][0]["description"]}

Wind Speed : {data["wind"]["speed"]} m/s
"""
    except Exception as e:
        return f"Error retrieving weather: {str(e)}"

python_tool = PythonREPLTool(
    description="Execute Python Code"
)

from rag import get_retriever

@tool
def pdf_search(question: str) -> str:
    """
    Search uploaded PDFs.
    """
    try:
        retriever = get_retriever()
        docs = retriever.invoke(question)
        if not docs:
            return "No relevant information found in the uploaded documents."
        return "\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        return f"No document indexed yet or error searching PDF: {str(e)}"

toolkit = [
    search_tool,
    wiki_tool,
    weather_tool,
    python_tool,
    pdf_search
]