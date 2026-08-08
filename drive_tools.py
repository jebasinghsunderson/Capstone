import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_core.tools import tool

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

BUCKET_NAME = "cap_bucket"


@tool
def upload_file(file_path: str) -> str:
    """
    Upload a PDF file to Supabase Storage.
    """

    file_name = os.path.basename(file_path)

    with open(file_path, "rb") as file:
        supabase.storage.from_(BUCKET_NAME).upload(
            file_name,
            file,
            {
                "content-type": "application/pdf"
            }
        )

    return f"Uploaded successfully: {file_name}"


@tool
def list_files() -> str:
    """
    List files stored in Supabase Storage.
    """

    files = supabase.storage.from_(BUCKET_NAME).list()

    if not files:
        return "No files found."

    output = ""

    for file in files:
        output += f"{file['name']}\n"

    return output


drive_tools = [
    upload_file,
    list_files
]