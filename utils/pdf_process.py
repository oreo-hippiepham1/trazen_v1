from pypdf import PdfReader
import os

import tempfile
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader

@st.cache_data
def process_book(uploaded_pdf) -> tuple[str, list]:
    """Process the uploaded PDF file and extract text
    Args:
        uploaded_pdf: Uploaded PDF file
    Returns:
        tuple[str, list]: Tuple containing temporary file path and extracted pages
    """
    pages = []
    temp_pdf_path = ""
    # Create new temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        temp_pdf.write(uploaded_pdf.getvalue())
        temp_pdf_path = temp_pdf.name

        # Load and process PDF
        loader = PyPDFLoader(temp_pdf_path)
        pages.extend(loader.load())

    return (temp_pdf_path, pages)

@st.cache_data
def extract_chapter(filepath) -> dict:
    extractor = ChapterExtractor(filepath)
    toc = extractor.get_chapters()

    if not toc:
        st.warning("Could not successfully parse and extract book chapters!")
        return {}

    # Get page ranges
    prange = extractor.get_page_range_from_dict()
    max_nest = extractor.get_nest()

    return {
        'toc': toc,
        'prange': prange,
        'max_nest': max_nest
    }

class ChapterExtractor():
    def __init__(self, filepath):
        try:
            self.reader = PdfReader(filepath)
        except Exception as e:
            raise ValueError(f"Failed to read PDF file: {str(e)}")

        if len(self.reader.pages) == 0:
            raise ValueError("PDF file is empty")

        self.max_nest = 0
        self.chapters = self.extract_toc()
        self.n_pages = self.reader.get_num_pages()

    def get_chapters(self):
        return self.chapters

    def get_n_pages(self):
        return self.n_pages

    def get_nest(self):
        return self.max_nest

    def _recursive_nested_chapter_flat(self, node, nest_level: int=0) -> list:
        """
        Recursively extracts chapter information from PDF outline.

        Args:
            node: A pypdf outline node or list of nodes
            nest_level: Current nesting level (default: 0)

        Returns:
            list: List of chapter dictionaries with title, page number, and nesting level

        Raises:
            ValueError: If node structure is invalid
        """
        if node is None:
            return []

        chapters = []

        if isinstance(node, list):
            cur_nest_level = nest_level + 1

            if cur_nest_level >= self.max_nest:
                self.max_nest = cur_nest_level

            # Handle nested list of chapters
            for sub_node in node:
                chapters.extend(self._recursive_nested_chapter_flat(sub_node, cur_nest_level))
            return chapters

        else: # BASE BASE
            # Single chapter node
            title = node.title
            try:
                page = self.reader.get_destination_page_number(node)  # 1-based indexing
            except:
                page = 1  # Fallback to first page if page number extraction fails

            chapter_data = {
                'title': title,
                'page': page,
                'nest': nest_level,
            }

            return [chapter_data]  # Return as list for consistent typing


    def _nested_chapter_dict(self, node: list):
        """
        Transforms a flat list of nested chapter (with 'nest' level)
            to a tree dictionary of hierarchy
        """
        chapter_dict = {}
        for i in range(self.max_nest):
            chapter_dict[i] = []
            chapter_dict[i].extend([n for n in node if n['nest']==i])

        return chapter_dict


    def extract_toc(self) -> list:
        """
        Given a file_path to a Book PDF, extract the book's table of content (if possible by bare minimum).
        """
        chapters = []

        if not self.reader.outline:
            chapters = [] # Cannot find Table of Contents

        else:
            chapters.extend(self._recursive_nested_chapter_flat(self.reader.outline, nest_level=0))

        return chapters


    def get_page_range_from_dict(self) -> list[dict]:
        """
        Calculates page ranges for each chapter in the table of contents.

        Returns:
            list[dict]: List of dictionaries containing:
                - title: Chapter title
                - nest: Nesting level
                - start: Starting page number
                - end: Ending page number (exclusive)
                - id: Unique identifier for the chapter
        """
        if not self.chapters:
            return []

        pagerange = []
        chapters = self.chapters
        total_pages = self.get_n_pages()

        for i, current_chapter in enumerate(chapters):
            range_info = {
                'title': current_chapter['title'],
                'nest': current_chapter['nest'],
                'start': current_chapter['page']
            }

            # Find the end page by looking at the next chapter at same or lower nesting level
            end_page = total_pages  # Default to last page
            for next_chapter in chapters[i + 1:]:
                if next_chapter['nest'] <= current_chapter['nest']:
                    end_page = next_chapter['page']
                    break

            range_info['end'] = end_page
            range_info['id'] = f"ch_{current_chapter['nest']}_{current_chapter['page']}_{end_page}"
            pagerange.append(range_info)

        return pagerange