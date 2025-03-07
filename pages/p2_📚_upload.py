import streamlit as st

import tempfile

from langchain_community.document_loaders import PyPDFLoader

from utils import extract_toc, get_page_range_from_dict

st.set_page_config(
    page_title="Test - Upload",
    page_icon="📚",
    layout='wide'
)

st.header("Test for uploads")

class Uploader():
    def __init__(self):
        self.filepath = None


    def upload_section(self) -> tuple[str, list]:
        uploaded_pdf = st.sidebar.file_uploader(
            "Upload your book here (PDF)",
            type=['pdf']
        )

        if 'book_uploaded' not in st.session_state:
            st.session_state['book_uploaded'] = None

        if not uploaded_pdf:
            st.sidebar.warning("Please upload a book to continue!")
            st.stop() # stops ST right here

        pages = []
        if uploaded_pdf:
            st.session_state['book_upload'] = None # reset

            with st.spinner("Processing book..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix='pdf') as temp_pdf:
                    temp_pdf.write(uploaded_pdf.getvalue())

                    temp_pdf_path = temp_pdf.name
                    loader = PyPDFLoader(temp_pdf_path)

                    st.session_state['book_upload'] = temp_pdf_path
                    self.filepath = temp_pdf_path

                    pages.extend(loader.load()) # populate with pdf

        return (temp_pdf_path, pages)

    def _display_toc(self, toc: list[dict], nested: bool=False):
        if not nested:
            for content in toc:
                st.markdown(f"{content['title']}\n\n"
                            f"Page: {content['page']}\n\n"
                            f"________________________\n\n")

        else:
            for content in toc:
                if content['nest'] == 'outer':
                    st.markdown(f"________________________\n\n"
                                f"**{content['title']}**\n\n"
                                f"Page: {content['page']}\n\n"
                                f"________________________\n\n")
                else:
                    st.markdown(f"  == {content['title']}\n\n"
                            f"  == Page: {content['page']}\n\n")


    def display_toc(self):
        toc, nested, n_pages = extract_toc(self.filepath)
        if not (toc):
            st.warning("Could not successfull parse and extract book chapters!")
            return
        else:
            # if nested:

            # st.subheader("Big Chaps")
            # st.write(toc_outer)
            # st.subheader("Small Chaps")
            # st.write(toc_inner)
            # st.subheader("Page Range Test")
            # prange = get_page_range_from_dict(toc_inner, n_pages)
            # st.write(prange)
            self._display_toc(toc, nested)

    def main(self):
        self.upload_section()

        self.display_toc()

if __name__ == '__main__':
    agent = Uploader()
    agent.main()
