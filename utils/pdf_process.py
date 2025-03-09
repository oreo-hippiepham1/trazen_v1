from pypdf import PdfReader

class ChapterExtractor():
    def __init__(self, filepath):
        self.reader = PdfReader(filepath)
        self.chapters = self.extract_toc()
        self.nested = False
        self.n_pages = self.reader.get_num_pages()

    def get_chapters(self):
        return self.chapters

    def get_nested(self):
        return self.nested

    def get_n_pages(self):
        return self.n_pages

    def _recursive_nested_chapter(self, node: list, nest_level: int=0):
        chapters = []

        if isinstance(node, list):
            self.nested = True
            # Handle nested list of chapters
            for sub_node in node:
                chapters.extend(self._recursive_nested_chapter(sub_node, nest_level+1))
            return chapters

        else: # BASE BASE
            # Single chapter node
            title = node.title
            page = self.reader.get_destination_page_number(node) + 1  # 1-based indexing
            chapter_data = {
                'title': title,
                'page': page,
                'nest': nest_level
            }

            return [chapter_data]  # Return as list for consistent typing


    def extract_toc(self) -> tuple[list[dict]]:
        """
        Given a file_path to a Book PDF, extract the book's table of content (if possible by bare minimum).
        """
        chapters = []

        if not self.reader.outline:
            chapters = [] # Cannot find Table of Contents

        else:
            chapters.extend(self._recursive_nested_chapter(self.reader.outline, nest_level=0))

        return chapters


    def get_page_range_from_dict(self) -> list[dict]:
        """
        Given a list of dicts containing:
        [
            {
                'title': ...,
                'page' : ...
            },
            {}, ...
        ]

        Return a page range for each title
        """
        pagerange = []
        page_dict = self.get_chapters()
        for d in range(len(page_dict)):
            current_page = {}

            current_page['title'] = page_dict[d]['title']
            current_page['nest'] = page_dict[d]['nest']
            current_page['start'] = page_dict[d]['page']

            try: # page range = current page -> next chapter page
                current_page['end'] = page_dict[d+1]['page']
            except Exception as e: # last title
                current_page['end'] = self.get_n_pages()

            pagerange.append(
                current_page
            )

        return pagerange
