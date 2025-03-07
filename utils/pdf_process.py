from pypdf import PdfReader

def extract_toc(file_path) -> tuple[list[dict], bool, int]:
    reader = PdfReader(file_path)

    chapters_outer = []
    chapters_inner = []
    chapters = []
    nested = False

    if not reader.outline:
        return None # Cannot find Table of Contents

    num_pages = reader.get_num_pages()

    for item in reader.outline:
        if isinstance(item, list): # for nested chapters
            for subitem in item:
                # print(subitem)
                chapters.append(
                    {
                        'title': subitem.title,
                        'nest': 'inner',
                        'page': reader.get_destination_page_number(subitem)
                    }
                )
                # print(f'Appending {subitem.title}')
                # print('======')
                nested = True
        else:
            chapters.append(
                {
                    'title': item.title,
                    'nest': 'outer',
                    'page': reader.get_destination_page_number(item)
                }
            )

    return (chapters, nested, num_pages)


def get_page_range_from_dict(page_dict: list[dict], num_page:int) -> list[dict]:
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
    count = 0
    for d in range(len(page_dict)):
        current_page = {}
        current_page['title'] = page_dict[d]['title']
        current_page['start'] = page_dict[d]['page']
        try: # page range = current page -> next chapter page
            current_page['end'] = page_dict[d+1]['page'] - 1
        except Exception as e: # last title
            current_page['end'] = num_page - 1

        pagerange.append(
            current_page
        )

    return pagerange
