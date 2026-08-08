import os

from langchain_chroma import Chroma

from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter


DB_PATH = "chroma_db"

UPLOAD_FOLDER = "uploads"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def create_vector_database(pdf_path):

    loader = PyPDFLoader(pdf_path)

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=800,

        chunk_overlap=100

    )

    chunks = splitter.split_documents(documents)

    db = Chroma.from_documents(

        documents=chunks,

        embedding=embedding_model,

        persist_directory=DB_PATH

    )

    return db


def load_database():

    return Chroma(

        persist_directory=DB_PATH,

        embedding_function=embedding_model

    )


def get_retriever():

    db = load_database()

    return db.as_retriever(
        search_kwargs={"k":3}
    )