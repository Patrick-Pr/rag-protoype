import typer
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import PromptTemplate

from database.database import add_to_database
from search.search import retrieve_doc, ask_question

load_dotenv()

# app = typer.Typer()
#
#
# @app.command()
# def add(src_directory: str):
#     add_to_database(src_directory)
#
#
# @app.command()
# def search(promt: st):
#     res = ask_question(promt)
#     print(res)


def call_llm(input_str: str) -> str:
    # TODO: do the LLM call here
    docs = retrieve_doc(input_str)

    prompt = "Context:\n{context}\n\nQuestion:\n{input}"
    prompt_template = PromptTemplate(
        input_variables=["input", "context"], template=prompt
    )

    return ask_question(prompt_template, input_str, docs)
    # return prompt


def main():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your question?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = call_llm(prompt)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    # app()
    main()
