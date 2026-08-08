import os

import requests

import wikipedia

from dotenv import load_dotenv

load_dotenv()

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


API_KEY = os.getenv("OPENWEATHER_API_KEY")


@tool
def weather_tool(city:str)->str:
    """
    Returns weather information.
    """

    url="https://api.openweathermap.org/data/2.5/weather"

    params={
        "q":city,
        "appid":API_KEY,
        "units":"metric"
    }

    response=requests.get(url,params=params)

    if response.status_code!=200:
        return "Weather Not Found"

    data=response.json()

    return f"""
City : {city}

Temperature : {data["main"]["temp"]}

Humidity : {data["main"]["humidity"]}

Condition : {data["weather"][0]["description"]}

Wind Speed : {data["wind"]["speed"]}
"""

python_tool = PythonREPLTool(
    description="Execute Python Code"
)


from rag import get_retriever

retriever = get_retriever()


@tool
def pdf_search(question:str)->str:
    """
    Search uploaded PDFs.
    """

    docs = retriever.invoke(question)

    return "\n\n".join(
        [doc.page_content for doc in docs]
    )


toolkit = [

    search_tool,

    wiki_tool,

    weather_tool,

    python_tool,

    pdf_search

]