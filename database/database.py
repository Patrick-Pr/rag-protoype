import os
from typing import TypedDict

import nltk
from bs4 import BeautifulSoup

from langchain_community.document_loaders.directory import DirectoryLoader
from langchain_community.document_loaders.html import UnstructuredHTMLLoader
from langchain_community.document_loaders.html_bs import BSHTMLLoader
from langchain_community.embeddings.azure_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document


class Doc:
    content: str
    file_name: str
    type: str

    def __init__(self, content: str, file_name: str, type: str):
        self.content = content
        self.file_name = file_name
        self.type = type

    def to_document(self) -> Document:
        soup = BeautifulSoup(self.content)
        return Document(
            page_content=soup.get_text(),
            metadata={"file_name": self.file_name, "type": self.type},
        )


def add_to_database(src_docs: list[Doc], index_name: str = "rag-prototype-streamlit"):
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT_NAME"]
    api_version = os.environ["AZURE_OPENAI_API_VERSION"]

    search_service_api_key = os.environ["AZURE_AI_SEARCH_SERVICE_API_KEY"]
    search_service_endpoint = os.environ["AZURE_AI_SEARCH_SERVICE_ENDPOINT"]
    search_service_api_version = os.environ["AZURE_AI_SEARCH_SERVICE_API_VERSION"]

    embedding_model = os.environ["AZURE_OPENAI_API_EMBEDDING_MODEL_NAME"]
    deployment_name = os.environ["AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT_NAME"]

    nltk.download("punkt")

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=deployment_name,
        openai_api_version=api_version,
        azure_endpoint=azure_endpoint,
        api_key=api_key,
    )

    vector_store = AzureSearch(
        azure_search_endpoint=search_service_endpoint,
        azure_search_key=search_service_api_key,
        index_name=index_name,
        embedding_function=embeddings.embed_query,
        search_service_api_version=search_service_api_version,
    )

    # loader = DirectoryLoader(src_directory, glob="**/*.html", loader_cls=BSHTMLLoader)

    text_splitter = CharacterTextSplitter(
        separator=" ",
        chunk_size=1000,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )

    # custom Document loading from Memory
    docs: list[Document] = []
    for doc in src_docs:
        docs.append(doc.to_document())

    docs = text_splitter.split_documents(docs)

    vector_store.add_documents(documents=docs)
