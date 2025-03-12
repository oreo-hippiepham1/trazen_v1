import streamlit as st

from pinecone import Pinecone, ServerlessSpec, Index
from langchain_pinecone import PineconeVectorStore


def config_pinecone(index_name: str='test') -> tuple[Pinecone, Index]:
    PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
    pc = Pinecone(
        api_key=PINECONE_API_KEY
    )
    if index_name not in [index.name for index in pc.list_indexes()]:
        pc.create_index(index_name,
                        dimension=1536,
                        spec=ServerlessSpec(cloud='aws', region='us-east-1')
                        )

    index = pc.Index(index_name)
    return pc, index
