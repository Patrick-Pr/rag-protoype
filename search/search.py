import os

from langchain.chains.llm import LLMChain
from langchain_community.embeddings.azure_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureOpenAI, ChatOpenAI, AzureChatOpenAI


def retrieve_doc(prompt: str) -> list[Document]:
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT_NAME"]
    api_version = os.environ["AZURE_OPENAI_API_VERSION"]

    search_service_api_key = os.environ["AZURE_AI_SEARCH_SERVICE_API_KEY"]
    search_service_endpoint = os.environ["AZURE_AI_SEARCH_SERVICE_ENDPOINT"]
    search_service_api_version = os.environ["AZURE_AI_SEARCH_SERVICE_API_VERSION"]

    embedding_model = os.environ["AZURE_OPENAI_API_EMBEDDING_MODEL_NAME"]
    deployment_name = os.environ["AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT_NAME"]

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=deployment_name,
        openai_api_version=api_version,
        azure_endpoint=azure_endpoint,
        api_key=api_key,
    )

    index_name = "rag-prototype-streamlit"

    vector_store = AzureSearch(
        azure_search_endpoint=search_service_endpoint,
        azure_search_key=search_service_api_key,
        index_name=index_name,
        embedding_function=embeddings.embed_query,
        search_service_api_version=search_service_api_version,
    )

    retriever = vector_store.as_retriever()

    docs = retriever.get_relevant_documents(prompt, search_kwargs={"k", 3})
    print(docs)
    return docs


def ask_question(prompt_template: PromptTemplate, input_str: str, docs: list[Document]):
    api_version = os.environ["AZURE_OPENAI_API_VERSION"]

    llm = AzureChatOpenAI(azure_deployment="gpt-35-turbo-16k", api_version=api_version)

    chain = LLMChain(llm=llm, prompt=prompt_template)

    context_str: str = ""
    for doc in docs:
        context_str += doc.page_content + "\n\n"

    res = chain.invoke(input={"input": input_str, "context": context_str})

    return res["text"]
