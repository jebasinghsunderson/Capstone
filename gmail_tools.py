import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials
)

def get_gmail_tools():
    try:
        # Load from st.secrets if present and files do not exist locally
        if hasattr(st, "secrets"):
            if not os.path.exists("credentials.json") and "GMAIL_CREDENTIALS_JSON" in st.secrets:
                with open("credentials.json", "w", encoding="utf-8") as f:
                    f.write(st.secrets["GMAIL_CREDENTIALS_JSON"])
            if not os.path.exists("token_gmail.json") and "GMAIL_TOKEN_JSON" in st.secrets:
                with open("token_gmail.json", "w", encoding="utf-8") as f:
                    f.write(st.secrets["GMAIL_TOKEN_JSON"])

        token_file = "token_gmail.json"
        secret_file = "credentials.json"

        if not (os.path.exists(token_file) or os.path.exists(secret_file)):
            print("Gmail credentials or token file not found. Skipping Gmail tools.")
            return []

        credentials = get_gmail_credentials(
            token_file=token_file,
            scopes=["https://mail.google.com/"],
            client_sercret_file=secret_file if os.path.exists(secret_file) else None
        )

        api_resource = build_resource_service(credentials=credentials)
        toolkit = GmailToolkit(api_resource=api_resource)
        return toolkit.get_tools()
    except Exception as e:
        print(f"Skipping Gmail tools: {e}")
        return []