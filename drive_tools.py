import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client
from langchain_core.tools import tool

load_dotenv()

def get_secret(key: str, default: str = None) -> str:
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

def get_supabase_client():
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None

BUCKET_NAME = "cap_bucket"

@tool
def upload_file(file_path: str) -> str:
    """
    Upload a PDF file to Supabase Storage.
    """
    client = get_supabase_client()
    if not client:
        return "Supabase client is not configured. Please add SUPABASE_URL and SUPABASE_KEY to Secrets."

    file_name = os.path.basename(file_path)

    try:
        with open(file_path, "rb") as file:
            client.storage.from_(BUCKET_NAME).upload(
                file_name,
                file,
                {
                    "content-type": "application/pdf"
                }
            )
        return f"Uploaded successfully: {file_name}"
    except Exception as e:
        return f"Upload to Supabase failed: {str(e)}"

@tool
def list_files() -> str:
    """
    List files stored in Supabase Storage.
    """
    client = get_supabase_client()
    if not client:
        return "Supabase client is not configured. Please add SUPABASE_URL and SUPABASE_KEY to Secrets."

    try:
        files = client.storage.from_(BUCKET_NAME).list()
        if not files:
            return "No files found."

        output = ""
        for file in files:
            output += f"{file['name']}\n"
        return output
    except Exception as e:
        return f"Failed to list Supabase files: {str(e)}"

drive_tools = [
    upload_file,
    list_files
]