FROM python:3
LABEL authors="psydow"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY chat_with_Rag.py ./
COPY database ./database/
COPY search ./search/
COPY pages ./pages/

EXPOSE 8501

CMD [ "streamlit", "run", "./chat_with_Rag.py", "--server.port=8501", "--server.address=0.0.0.0"]