import os

from langchain.chains.llm import LLMChain
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import (
    AzureChatOpenAI,
    AzureOpenAIEmbeddings,
)


def retrieve_doc(
    prompt: str, index_name: str = "rag-prototype-streamlit"
) -> list[Document]:
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    api_version = os.environ["AZURE_OPENAI_API_VERSION"]

    search_service_api_key = os.environ["AZURE_AI_SEARCH_SERVICE_API_KEY"]
    search_service_endpoint = os.environ["AZURE_AI_SEARCH_SERVICE_ENDPOINT"]
    search_service_api_version = os.environ["AZURE_AI_SEARCH_SERVICE_API_VERSION"]

    azure_deployment_model = os.environ["AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT_NAME"]

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=azure_deployment_model,
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

    retriever = vector_store.as_retriever()

    return retriever.get_relevant_documents(prompt, search_kwargs={"k", 3})


def ask_question(
    prompt_template: PromptTemplate,
    input_str: str,
    docs: list[Document],
) -> str:
    api_version = os.environ["AZURE_OPENAI_API_VERSION"]
    azure_deployment_model = os.environ["AZURE_OPENAI_API_MODEL_NAME"]

    llm = AzureChatOpenAI(
        azure_deployment=azure_deployment_model, api_version=api_version
    )

    chain = LLMChain(llm=llm, prompt=prompt_template)

    context_str: str = ""
    for doc in docs:
        context_str += doc.page_content + "\n\n"

    res = chain.invoke(input={"input": input_str, "context": context_str})

    return res["text"]
