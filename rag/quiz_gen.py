import re
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from utils.storage import config_pinecone
from utils.llm import config_llm, config_embedding_model, config_llm_simple
from utils.stream import StreamHandler
from utils.chat_utils import enable_chat_history, display_single_message
from utils.quiz_format import format_quiz
from .quiz_agent import get_quiz_agent


import random
import time


class QuizGenTab():
    def __init__(self, namespace):
        self.llm: ChatOpenAI = config_llm_simple()
        self.embedding_model = config_embedding_model()
        self.pc, self.index = config_pinecone()
        self.vector_store = PineconeVectorStore(index=self.index, embedding=self.embedding_model, namespace=namespace)

    def get_chap(self) -> tuple[list, list]:
        """
        Get the chapter text and metadata from the selected chapter
        """
        # Retrieve the selected chapter's info from current state
        chapter = st.session_state['selected_chapter']
        c_title = chapter['title']
        c_start = chapter['start']
        c_end = chapter['end']
        c_id = chapter['id']

        # Retrieve text and metadata
        # Get relevant pages from book upload
        chapter_pages = st.session_state['book_upload'][c_start-1:c_end]

        # Extract text from pages
        texts, metadatas = [page.page_content for page in chapter_pages], [page.metadata for page in chapter_pages]

        return texts, metadatas

    def extract_keywords(self, text: str):
        """
        Extract keywords from the text using OpenAI
        """

        prompt = """
        Extract keywords (concepts, terms, phrases) from the following text:
        {text}
        The keywords should be relevant to the content and context of the text, and no more than 2 words long.
        The keywords should be in a comma-separated list format, of exactly 4 items.
        For example:
        machine learning,data science,artificial intelligence, python
        """
        full_prompt = prompt.format(text=text)
        response = self.llm.invoke([HumanMessage(content=full_prompt)])
        response = response.content

        return response


    def _process_chunks(self, max_tokens: int = 10000) -> list:
        """
        Split the chunks into smaller batches to avoid exceeding the token limit,
            and perform an LLM call to extract keywords from each batch.

        Args:
            max_tokens (int): The maximum number of tokens to process in a single batch.

        Returns:
            list: A list of lists containing the extracted keywords from each batch.
        """
        # Get the chapter text and metadata
        chunks = st.session_state['selected_chapter_chunks'] # get the current chapter's chunks

        ## START
        total_start = time.time()
        st.write("Total number of chunks: ", len(chunks))
        st.write("Approx. total #tokens: ", sum(len(chunk.page_content) // 4 for chunk in chunks))

        available_tokens = max_tokens - 1000 # reserve 1000 tokens for LLM overhead and prompt\

        current_batch = []
        current_tokens = 0
        results = []

        for chunk in chunks:
            chunk_tokens = len(chunk.page_content) // 4 # rough estimation from char to token
            start = time.time()

            if current_tokens + chunk_tokens > available_tokens:
                # Process the current batch
                combined_text = "\n\n".join(c.page_content for c in current_batch)
                keywords = self.extract_keywords(combined_text)

                if isinstance(keywords, str):
                    if len(keywords.split(',')) == 4:
                        keywords = keywords.split(',')
                        results.extend(keywords)
                    else:
                        st.warning("Invalid keyword length. Please try again.")
                        st.write(keywords)
                else:
                    st.warning("Invalid keyword format. Please try again.")
                    st.write(keywords)

                st.write(f"Processed batch - Chunks: {len(current_batch)} - Tokens: {current_tokens} - Time: {time.time() - start:.2f}s.")

                # Reset for next batch
                current_batch = [chunk] # start with current chunk
                current_tokens = chunk_tokens

            else:
                # Add the chunk to the current batch
                current_batch.append(chunk)
                current_tokens += chunk_tokens

        # Process the last remaining batch
        if current_batch:
            combined_text = "\n\n".join(c.page_content for c in current_batch)
            keywords = self.extract_keywords(combined_text)
            if isinstance(keywords, str):
                if len(keywords.split(',')) == 4:
                    keywords = keywords.split(',')
                    results.extend(keywords)
                else:
                    st.warning("Invalid keyword length. Please try again.")
                    st.write(keywords)
            else:
                st.warning("Invalid keyword format. Please try again.")
                st.write(keywords)

            st.write(f"Processed last batch - Chunks: {len(current_batch)} - Tokens: {current_tokens}")

        total_end = time.time()
        st.write("Total processing time (secs): ", total_end - total_start)
        st.write("--------------------------------------------------")
        return results


    def clean_keywords(self, n_quiz: int=10) -> list:
        keywords = self._process_chunks()
        keywords = list(set(keywords)) # remove duplicates
        for k in keywords:
            k = k.lstrip().rstrip() # remove leading and trailing spaces
            k = k.strip(",\"") # remove quotes
            k = k.replace("'", "") # remove single quotes

        keywords = list(set(keywords)) # remove duplicates
        keywords = [k for k in keywords if len(k) > 0] # remove empty strings
        if (len(keywords) < n_quiz):
            return keywords # return all keywords if less than n_quiz

        keywords = random.sample(keywords, n_quiz) # shuffle the keywords

        return keywords


    def generate(self, n_quiz: int=10) -> list:
        """
        Generate quiz using the chain
        """
        # Get the chapter text and metadata
        texts, metadatas = self.get_chap()

        # Process the chunks
        keywords = self.clean_keywords(n_quiz)

        # Set up the agent for quiz
        quiz_agent = get_quiz_agent(self.llm, self.vector_store)

        bank = []
        ### Generate quiz
        with st.spinner("Generating quiz..."):
            rem = len(keywords)
            for k in keywords:
                current_q = {}
                st.write(f"Generating quiz for keyword: {k}. Remaining keywords: {rem - 1}")

                response = quiz_agent.invoke({
                    'keyword': k,
                })

                current_q['quiz'] = response['answer']
                current_q['quiz_src'] = response['answer_src']
                current_q['quiz_formatted'] = format_quiz(response['answer'])
                bank.append(current_q)
                rem -= 1

        st.write("Quiz generation completed.")
        st.write("Total quizzes: ", len(bank))
        return bank