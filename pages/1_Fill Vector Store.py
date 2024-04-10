from io import StringIO

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from database.database import Doc, add_to_database

index_name = st.text_input(label="Index Name", value="rag-prototype-streamlit")
index_name = index_name.lower().strip().replace(" ", "_")

uploaded_files: list[UploadedFile] = st.file_uploader(
    "choose a file", accept_multiple_files=True, type="html"
)

if st.button("Upload", type="primary"):
    docs: list[Doc] = []
    for uploaded_file in uploaded_files:
        bytes_read = uploaded_file.getvalue()
        string_io = StringIO(bytes_read.decode("utf-8"))
        text = string_io.read()
        docs.append(
            Doc(content=text, file_name=uploaded_file.name, type=uploaded_file.type)
        )

    with st.spinner(text="Document Upload"):
        add_to_database(docs, index_name)
