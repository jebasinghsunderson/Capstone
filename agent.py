import os

from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq

from langchain.agents import create_agent

from memory import get_memory

from tools import toolkit

from gmail_tools import get_gmail_tools

from drive_tools import drive_tools


llm = ChatGroq(

    model="openai/gpt-oss-120b",

    api_key=os.getenv("GROQ_API_KEY")

)


memory = get_memory()


all_tools = (

    toolkit

    + get_gmail_tools()

    + drive_tools

)


agent = create_agent(

    model=llm,

    tools=all_tools,

    checkpointer=memory

)


def ask_agent(question, thread_id="hari"):

    events = agent.stream(

        {

            "messages":[

                (

                    "user",

                    question

                )

            ]

        },

        config={

            "configurable":{

                "thread_id":thread_id

            }

        },

        stream_mode="values"

    )

    answer=""

    for event in events:

        answer = event["messages"][-1].content

    return answer