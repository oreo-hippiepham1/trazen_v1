import streamlit as st
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from utils import ChapterExtractor

st.set_page_config(
    page_title="Test - Upload",
    page_icon="📚",
    layout='wide'
)

st.header("Test for uploads")

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
        if 'temp_files' not in st.session_state:
            st.session_state.temp_files = []

    def _cleanup_temp_files(self):
        """Clean up temporary files from previous sessions"""
        for temp_file in st.session_state.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                st.error(f"Error cleaning up temporary file: {str(e)}")
        st.session_state.temp_files = []

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
                # Clean up previous temp files
                self._cleanup_temp_files()

                # Create new temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                    temp_pdf.write(uploaded_pdf.getvalue())
                    temp_pdf_path = temp_pdf.name

                    # Add to temp files list for cleanup
                    st.session_state.temp_files.append(temp_pdf_path)

                    # Load and process PDF
                    loader = PyPDFLoader(temp_pdf_path)
                    self.filepath = temp_pdf_path
                    pages.extend(loader.load())

                st.session_state.book_upload = pages

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

    def display_toc(self):
        """Process and display the table of contents"""
        try:
            extractor = ChapterExtractor(self.filepath)
            toc = extractor.get_chapters()

            if not toc:
                st.warning("Could not successfully parse and extract book chapters!")
                return

            # Display TOC
            st.subheader("Table of Contents")
            self._display_toc(toc)

            # Get page ranges
            prange = extractor.get_page_range_from_dict()
            max_nest = extractor.get_nest()

            # Only show nest selection if we have nested chapters
            if max_nest > 1:
                st.subheader("Chapter Information by Nesting Level")
                nest_choice = st.selectbox(
                    label="Select chapter nesting level",
                    options=range(1, max_nest + 1),
                    format_func=lambda x: f"Level {x}"
                )

                filtered_chapters = [pr for pr in prange if pr['nest'] == nest_choice]
                if filtered_chapters:
                    st.table(filtered_chapters)
                else:
                    st.info(f"No chapters found at nesting level {nest_choice}")

        except Exception as e:
            st.error(f"Error processing table of contents: {str(e)}")

    def main(self):
        """Main application flow"""
        self.upload_section()
        self.display_toc()

if __name__ == '__main__':
    agent = Uploader()
    agent.main()
