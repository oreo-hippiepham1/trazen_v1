from pypdf import PdfReader

class ChapterExtractor():
    def __init__(self, filepath):
        self.reader = PdfReader(filepath)
        self.max_nest = 0
        self.chapters = self.extract_toc()
        self.n_pages = self.reader.get_num_pages()

    def get_chapters(self):
        return self.chapters

    def get_n_pages(self):
        return self.n_pages

    def get_nest(self):
        return self.max_nest

    def _recursive_nested_chapter_flat(self, node: list, nest_level: int=0):
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
            page = self.reader.get_destination_page_number(node) + 1  # 1-based indexing
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


    def extract_toc(self) -> tuple[list[dict]]:
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
                for d_2 in range(d+1, len(page_dict)):
                    if page_dict[d_2]['nest'] <= page_dict[d]['nest']: # end of current outer chapter / or next is same nest
                        current_page['end'] = page_dict[d_2]['page']
                        break

            except Exception as e: # last title
                current_page['end'] = self.get_n_pages()

            pagerange.append(
                current_page
            )

        return pagerange