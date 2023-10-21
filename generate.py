import re
from dataclasses import dataclass
from typing import Set, Optional, List, Tuple
from collections import deque

import requests
from bs4 import BeautifulSoup


@dataclass
class Style:
    tailwind_name: str
    css_attributes: List[Tuple[str, str]]
    css_selector_extension: Optional[str] = None

    def css_class(self):
        name = self.tailwind_name if self.css_selector_extension is None \
            else f'{self.tailwind_name}{self.css_selector_extension}'
        attributes = ';'.join(f'{attribute[0]}: {attribute[1]}' for attribute in self.css_attributes)
        return f'.{name}{{{attributes}}}'


def main():
    page_names = fetch_all_doc_page_names()
    styles = []

    for page_name in page_names:
        if page_name in ('animation',):
            print(f'skipping page {page_name}')
            continue

        print(f'fetching page {page_name}')
        page = fetch_page(page_name)

        for table in page.find_all('table'):
            strings = table.stripped_strings
            if next(strings) != 'Class' or next(strings) != 'Properties':
                continue

            print('found tailwind classes')
            parse_styles_into(styles, raw_styles=deque(strings))

        print()

    with open('tailwindlike.css', mode='w', encoding='utf8') as file:
        file.writelines(map(Style.css_class, styles))


TAILWIND_NAME = re.compile('[a-z][a-z0-9-./]*[a-z0-9%]')


def parse_styles_into(styles, raw_styles: deque[str]):
    while raw_styles:
        match raw_styles:
            case [str(css_name), ':', str(css_value), ';', *_]:
                styles[-1].css_attributes.append((css_name, css_value))
                for _ in range(4):
                    raw_styles.popleft()

            case [str(comment), *_] if is_comment(comment):
                raw_styles.popleft()

            case [str(tailwind_name), '> * + *', *_] if re.fullmatch(TAILWIND_NAME, tailwind_name):
                styles.append(Style(tailwind_name, css_attributes=[], css_selector_extension='>*+*'))
                raw_styles.popleft()
                raw_styles.popleft()

            case [str(tailwind_name), *_] if re.fullmatch(TAILWIND_NAME, tailwind_name):
                styles.append(Style(tailwind_name, []))
                raw_styles.popleft()

            case [str(header_name), *_] if header_name.lower() != header_name:
                raw_styles.popleft()

            case _:
                print(raw_styles[0], re.fullmatch(TAILWIND_NAME, raw_styles[0]))
                raise ValueError(raw_styles)


def fetch_all_doc_page_names() -> Set[str]:
    return set(re.findall(
        '/docs/([a-z][a-z0-9-]*[a-z0-9])',
        str(requests.get('https://tailwindcss.com/docs/installation').content),
        re.MULTILINE))


def fetch_page(name: str) -> BeautifulSoup:
    return BeautifulSoup(requests.get(f'https://tailwindcss.com/docs/{name}').content, features='html.parser')


def is_comment(text: str) -> bool:
    return text.startswith('/*') and text.endswith('*/')


if __name__ == '__main__':
    main()
