import os

from dotenv import load_dotenv

load_dotenv()

from langchain_google_community import GmailToolkit

from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials
)

def get_gmail_tools():

    credentials = get_gmail_credentials(

        token_file="token_gmail.json",

        scopes=[
            "https://mail.google.com/"
        ],

        client_sercret_file="credentials.json"

    )

    api_resource = build_resource_service(
        credentials=credentials
    )

    toolkit = GmailToolkit(
        api_resource=api_resource
    )

    return toolkit.get_tools()