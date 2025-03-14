import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from utils.storage import config_pinecone
from utils.llm import config_llm, config_embedding_model
from utils.stream import StreamHandler
from utils.chat_utils import enable_chat_history, display_single_message

import os

st.set_page_config(
    page_title="QnA Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("QnA Chatbot")

class RAGTest:
    def __init__(self):
        self.llm = config_llm()
        self.embedding_model = config_embedding_model()
        self.pc, self.index = config_pinecone()

    def _get_vectorstore(self, namespace: str):
        return PineconeVectorStore(index=self.index, embedding=self.embedding_model, namespace=namespace)

    def save_file(self, file):
        """
        Save the uploaded file to a tmp folder
        Returns the file path
        """
        folder = 'tmp'
        if not os.path.exists(folder):
            os.makedirs(folder)

        file_name = os.path.basename(file)
        file_path = os.path.join(folder, file_name)

        with open(file_path, 'wb') as f:
            f.write(file.getvalue())

        return file_path

    @st.spinner("Analyzing the document...")
    def set_up_chain(self, namespace):
        """
        Set up the chain
        """
        vector_store = self._get_vectorstore(namespace)
        retriever = vector_store.as_retriever(search_type='mmr', search_kwargs={"k": 5})

        template = """
        Given the following conversation respond to the best of your ability.
        Answer straight to the point, that is, do not include phrases like "According to the context, ..." or similar.
        If you don't know the answer, or the context provided does not have sufficient information, just say so. Do not hallucinate information or use information outside the context.
        Your answer should be as detailed and informative as possible, try to keep it between 3-7 sentences.

        Context: {context}
        Chat History: {chat_history}
        Follow Up Input: {question}
        Standalone question:"""

        PROMPT = PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template=template
        )

        memory = ConversationBufferMemory(
            memory_key='chat_history',
            output_key='answer',
            return_messages=True
        )
        chain = ConversationalRetrievalChain.from_llm(
            self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": PROMPT},
            verbose=False
        )
        return chain


    def _initialize_session_state(self):
        # """Initialize session state variables for RAG"""
        # if 'vectorstore' not in st.session_state:
        #     st.session_state.vectorstore = None
        # if 'chat_history' not in st.session_state:
        #     st.session_state.chat_history = []
        # if 'chain' not in st.session_state:
        #     st.session_state.chain = None
        pass

    @enable_chat_history
    def main(self):
        # Initialize session state
        self._initialize_session_state()

        ## INITIAL CHECK BEFORE BEGIN CHATTING
        # Make sure the user has uploaded a file from other page
        if 'book_upload' not in st.session_state or st.session_state['book_upload'] is None:
            st.warning("Please upload a book first!")
            st.stop()

        if 'chapter_extracted' not in st.session_state or st.session_state['chapter_extracted'] is None:
            st.warning("Please select a chapter first!")
            st.stop()

        st.sidebar.write("Selected Chapter:")
        st.sidebar.json(st.session_state['selected_chapter'])

        chapter_id = st.session_state['selected_chapter']['id']
        if chapter_id not in st.session_state['uploaded_namespaces']:
            st.warning(f"Chapter ID {chapter_id} is not in the vector store. Please embed first (Page 2)")
            st.stop()
        # pc, index = config_pinecone()
        # ns = index.describe_index_stats()['namespaces']
        # if chapter_id not in ns:
        #     st.warning(f"Chapter ID {chapter_id} is not in the vector store. Please embed first (Page 2)")
        #     return

        ## CHAT UI
        user_input = st.chat_input(placeholder="Ask a question:")

        if user_input:
            # Display user message and stores in session state
            display_single_message(user_input, 'user')

            chain = self.set_up_chain(namespace=chapter_id)

            result = chain.invoke(
                {'question': user_input,},
                {'callbacks': [StreamHandler(st.empty())],}
            )

            response = result['answer']
            st.session_state['messages'].append(
                {
                    'role': 'assistant',
                    'content': response
                }
            )

            # References
            for idx, doc in enumerate(result['source_documents'], 1):
                # st.json(doc.metadata)
                page = doc.metadata['page']
                chapter = doc.metadata['chapter_title']
                reference = f"Chapter: {chapter}, Page: {page}"
                with st.popover(label=f"Reference {idx} - {reference}"):
                    st.caption(doc.page_content)

if __name__ == "__main__":
    rag = RAGTest()
    rag.main()