from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import AIMessage, SystemMessage, HumanMessage

import streamlit as st

def config_llm():
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    ss = st.session_state

    model_opt = st.sidebar.selectbox(
        "Select LLM Model",
        ["gpt-4o-mini", "o1-mini"],
        index=0,
        key='model_opt'
    )

    temp_opt = st.sidebar.slider(
        "Select Temperature",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.25,
        key='temp_opt'
    )

    llm = None

    if model_opt in ["gpt-4o-mini", "o1-mini"]:
        llm = ChatOpenAI(
            model=model_opt,
            temperature=temp_opt,
            api_key=OPENAI_API_KEY,
            streaming=True
        )

    return llm

def config_embedding_model():
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=OPENAI_API_KEY
    )

    return embedding_model

def config_llm_simple():
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=OPENAI_API_KEY
    )
    return llm

def config_embedding_model_simple():
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=OPENAI_API_KEY
    )
    return embedding_model