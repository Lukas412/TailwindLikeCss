import re
from typing import List

import requests
from bs4 import BeautifulSoup


def main():
    page_names = fetch_all_doc_page_names()
    for page_name in page_names:
        page = fetch_page(page_name)
        for table in page.find_all('table'):
            print(page_name)


def fetch_all_doc_page_names() -> List[str]:
    return re.findall(
        '/docs/([a-z][a-z0-9-]*[a-z0-9])',
        str(requests.get('https://tailwindcss.com/docs/installation').content),
        re.MULTILINE)


def fetch_page(name: str) -> BeautifulSoup:
    return BeautifulSoup(requests.get(f'https://tailwindcss.com/docs/{name}').content, features='html.parser')


if __name__ == '__main__':
    main()
