from regex import F
import streamlit as st
import tempfile
import os
import time

from langchain_community.document_loaders import PyPDFLoader
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from torch import batch_norm

from utils import ChapterExtractor, config_pinecone, config_embedding_model_simple
from utils import process_book, extract_chapter


st.set_page_config(
    page_title="Test - Upload",
    page_icon="📚",
    layout='wide'
)

st.header("Upload Your Book Here!")


class Uploader():
    def __init__(self):
        self.filepath = None
        # Initialize session state
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Centralized session state initialization"""
        if 'book_upload' not in st.session_state:
            st.session_state.book_upload = None
        if 'chapter_extracted' not in st.session_state:
            st.session_state.chapter_extracted = None

        # States for chapter selection
        if 'selected_chapter' not in st.session_state:
            st.session_state.selected_chapter = None
        if 'chapter_page_range' not in st.session_state:
            st.session_state.chapter_page_range = None

    def upload_section(self) -> tuple[str, list]:
        """Handle PDF upload and processing

        Returns:
            tuple[str, list]: Tuple containing temporary file path and extracted pages
        """
        uploaded_pdf = st.sidebar.file_uploader(
            "Upload your book here (PDF)",
            type=['pdf'],
            key='pdf_uploader'  # Add key for better state management
        )

        if not uploaded_pdf:
            st.sidebar.warning("Please upload a book to continue!")
            st.stop()

        pages = []
        temp_pdf_path = ""

        try:
            with st.spinner("Processing book..."):
                temp_pdf_path, pages = process_book(uploaded_pdf)
                st.session_state.book_upload = pages
                self.filepath = temp_pdf_path

        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return "", []

        return (temp_pdf_path, pages)


    def _display_toc(self, toc: list[dict]):
        """Display table of contents with proper formatting

        Args:
            toc: List of chapter dictionaries containing nest level and title
        """
        for content in toc:
            indent = '--' * (content['nest']**2)
            st.markdown(
                f"**{indent}{content['title']}** - Page {content['page']}\n\n"
            )

    def _handle_chapter_selection(self):
        """Handle chapter selection and update session state"""
        ss = st.session_state
        # Get the selected chapter data from the selectbox
        selected_title = ss.chapter_selector # mapped to widget in main()

        if selected_title:
            # Find the matching chapter data
            selected_data = next(
                (ch for ch in ss.chapter_extracted if ch['title'] == selected_title),
                None
            )
            if selected_data:
                ss.selected_chapter = selected_data
                ss.chapter_page_range = {
                    'start': selected_data['start'],
                    'end': selected_data['end']
                }
                st.success(f"Selected chapter: {selected_data['title']} (Pages {selected_data['start']}-{selected_data['end']})")

    def display_toc(self):
        """Process and display the table of contents"""
        try:
            chaps_dict = extract_chapter(self.filepath)
            toc = chaps_dict['toc']
            if not toc:
                st.warning("Could not successfully parse and extract book chapters!")
                return
            prange = chaps_dict['prange']
            st.session_state.chapter_extracted = prange  # Store all chapter data
            max_nest = chaps_dict['max_nest']

            st.subheader("Chapter Information by Nesting Level")
            nest_choice = st.selectbox(
                label="Select chapter nesting level",
                options=range(1, max_nest + 1),
                format_func=lambda x: f"Level {x}",
                key="nest_level"
            )

            filtered_chapters = [pr for pr in prange if pr['nest'] == nest_choice]
            if filtered_chapters:
                st.table(filtered_chapters)
            else:
                st.info(f"No chapters found at nesting level {nest_choice}")

            st.subheader("Chapter Selection")
            # Only show chapters from the selected nesting level
            chapter_options = [ch['title'] for ch in prange if ch['nest'] == nest_choice]
            if chapter_options:
                chapter_opt = st.selectbox(
                    "Select a chapter to process",
                    options=chapter_options,
                    key="chapter_selector",
                    on_change=self._handle_chapter_selection
                )

                # Display selected chapter information
                if st.session_state.selected_chapter:
                    st.write("Selected Chapter Information:")
                    st.json(st.session_state.selected_chapter)
            else:
                st.info("No chapters available at this nesting level")


        except Exception as e:
            st.error(f"Error processing table of contents: {str(e)}")


    def embed_chapter(self):
        """Embed and store selected chapter in vector store"""
        try:
            if not st.session_state.get('selected_chapter'):
                st.warning("Please select a chapter first!")
                return

            chapter_id = st.session_state.selected_chapter['id']

            if 'uploaded_namespaces' not in st.session_state:
                st.session_state['uploaded_namespaces'] = []
            if chapter_id in st.session_state['uploaded_namespaces']:
                st.warning(f"Chapter ID {chapter_id} already exists in the vector store. Please select a different chapter.")

            if st.button("Embed Selected Chapter"):
                # check if chapter_id already exists in the vector store
                pc, index = config_pinecone()
                ns = index.describe_index_stats()['namespaces']
                if chapter_id in ns:
                    st.warning(f"Chapter ID {chapter_id} already exists in the vector store. Please select a different chapter.")
                    return

                if chapter_id in st.session_state.uploaded_namespaces:
                    st.warning(f"Chapter ID {chapter_id} already exists in the vector store. Please select a different chapter.")
                    return

                start_total = time.time()

                ## PAGE EXTRACTION
                start = time.time()
                # Get page range for selected chapter
                start_page = st.session_state.selected_chapter['start']
                end_page = st.session_state.selected_chapter['end']
                chapter_id = st.session_state.selected_chapter['id']

                # Get relevant pages from book upload
                chapter_pages = st.session_state.book_upload[start_page-1:end_page]

                # Extract text from pages
                texts, metadatas = [page.page_content for page in chapter_pages], [page.metadata for page in chapter_pages]
                st.write(f"**Extracted {len(texts)} pages from chapter: {st.session_state.selected_chapter['title']}**")
                st.write(f"Time taken: {time.time() - start:.2f} seconds")

                ## TEXT SPLITTING
                start = time.time()
                # Split into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    length_function=len
                )
                chunks = text_splitter.create_documents(texts, metadatas)
                st.write(f"**Split into {len(chunks)} chunks**")
                st.write(f"Time taken: {time.time() - start:.2f} seconds")

                ## METADATA
                start = time.time()
                # Add chapter metadata to chunks
                for chunk in chunks:
                    chunk.metadata['chapter_title'] = st.session_state.selected_chapter['title']
                    chunk.metadata['chapter_id'] = chapter_id
                    chunk.metadata['chapter_start_page'] = start_page
                    chunk.metadata['chapter_end_page'] = end_page
                st.write(f"**Added metadata to {len(chunks)} chunks**")
                st.write(f"Time taken: {time.time() - start:.2f} seconds")

                ## VECTOR STORE
                start = time.time()
                # Initialize components
                embeddings = config_embedding_model_simple()

                # Create vector store
                vectorstore = PineconeVectorStore(
                    index=index,
                    embedding=embeddings,
                    namespace=chapter_id
                )
                st.write(f"**Vector store created.**")
                st.write(f"Time taken: {time.time() - start:.2f} seconds")

                ## EMBEDDING
                start = time.time()
                # Embed and store chunks
                # with st.spinner(f"Embedding chapter, appox. {st.session_state.selected_chapter['end'] - st.session_state.selected_chapter['start'] + 1} pages"):
                #     for chunk in chunks:
                #         vectorstore.add_documents([chunk])
                batch_size = 100 # Pinecone recommends 100
                total_chunks = len(chunks)

                with st.spinner(f"Embedding {total_chunks} chunks..."):
                    for i in range(0, total_chunks, batch_size):
                        batch = chunks[i:i + batch_size]
                        vectorstore.add_documents(batch)
                        st.write(f'**Processed {min(i + batch_size, total_chunks)} of {total_chunks} chunks.**')

                st.write(f"Embedded {total_chunks} chunks")
                st.write(f"Time taken: {time.time() - start:.2f} seconds")
                st.write(f"Total time taken: {time.time() - start_total:.2f} seconds")
                st.success(f"Successfully embedded chapter: {st.session_state.selected_chapter['title']} -- ID {chapter_id}")

                st.session_state.uploaded_namespaces.append(chapter_id)

        except Exception as e:
            st.error(f"Error embedding chapter: {str(e)}")


    def main(self):
        """Main application flow"""
        self.upload_section()
        self.display_toc()
        self.embed_chapter()

if __name__ == '__main__':
    agent = Uploader()
    agent.main()
