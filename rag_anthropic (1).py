# -*- coding: utf-8 -*-
"""RAG_anthropic.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rNJmbV2FnBiFoTqMySqpWNf1xcnXByCP
"""

#!pip install streamlit
#!pip install langchain
#!pip install voyageai
#!pip install pypdf

#!pip install langchain-community
#!pip install voyageai
#!pip install pypdf

#!python --version

#!sudo apt-get update -y
#!sudo apt-get install python3.8 -y
#!sudo update-alternatives --install /usr/local/bin/python3 python3 /usr/bin/python3.8 1
#!sudo update-alternatives --config python3

#!python --version

#!pip install --upgrade  pip
#!pip install -r requirements.txt

# Commented out IPython magic to ensure Python compatibility.
import os
import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter

import psutil  # for process monitoring
import gc  # for garbage collection

# %env VOYAGE_API_KEY="pa-2AE_4A2HCYvnRQWje-kaov6F2Oyz8cDnNsO0qbHGYWI"
#from langchain.embeddings import AnthropicEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import Anthropic
# Set your Anthropic API key
os.environ["ANTHROPIC_API_KEY"] = "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"
@st.cache_resource
def initialize_system(pdf_file):
    # Load PDF
    loader = PyPDFLoader(pdf_file)
    documents = loader.load()

    # Split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents) # Define 'texts' here so it's accessible outside the 'if' block

    import numpy as np

    # Embed the query
    import voyageai

    vo = voyageai.Client()

    # Embed the documents
    embeddings = vo.embed(texts, model="voyage-2", input_type="document").embeddings
    #embeddings = AnthropicEmbeddings()
    # Create vector store
    vectorstore = FAISS.from_documents(texts, embeddings)
    # Initialize Anthropic's Claude for text generation
    llm = Anthropic(model="claude-2", temperature=0.5)

    # Create a conversational chain
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    qa_chain = ConversationalRetrievalChain.from_llm(
            llm,
            retriever=vectorstore.as_retriever(),
            memory=memory
        )

    return qa_chain

# Streamlit UI
st.title("Chat with Your PDF using Claude")
# File uploader
pdf_file = st.file_uploader("Upload your PDF", type="pdf")

if pdf_file is not None:
    # Save the uploaded file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(pdf_file.getvalue())

    # Initialize the system
    qa_chain = initialize_system("temp.pdf")

# Chat interface
if "messages" not in st.session_state:
  st.session_state.messages = []

for message in st.session_state.messages:
  with st.chat_message(message["role"]):
     st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your PDF"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = qa_chain({"question": prompt})
            st.markdown(response['answer'])
        st.session_state.messages.append({"role": "assistant", "content": response['answer']})

else:
    st.write("Please upload a PDF file to begin.")

# Clean up
if os.path.exists("temp.pdf"):
    os.remove("temp.pdf")

# Memory management
gc.collect()
print(f"Memory usage: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")
