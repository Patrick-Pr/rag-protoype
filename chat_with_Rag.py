import json

import typer
from dotenv import load_dotenv
import streamlit as st
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

from database.database import add_to_database
from search.search import retrieve_doc, ask_question

load_dotenv()


def call_llm(input_str: str) -> tuple[str, list[Document]]:
    docs = retrieve_doc(input_str)

    prompt = "Context:\n{context}\n\nQuestion:\n{input}"
    prompt_template = PromptTemplate(
        input_variables=["input", "context"], template=prompt
    )

    response = ask_question(prompt_template, input_str, docs)

    return response, docs


def main():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your question?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner(text="Generating Answer"):
            response, docs = call_llm(prompt)

        with st.chat_message("assistant"):
            st.markdown(response)
            st.sidebar.header("Used Context")
            for idx, document in enumerate(docs):
                st.sidebar.subheader(
                    f"Chunk from Document {document.metadata['file_name']}"
                )
                st.sidebar.write(document.page_content)
                st.sidebar.code(
                    json.dumps(
                        document.metadata,
                        sort_keys=True,
                        indent=4,
                        separators=(":", ","),
                    ),
                    language="json",
                )
                st.sidebar.caption("Metadata")

        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
