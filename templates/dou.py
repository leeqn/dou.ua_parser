from bs4 import BeautifulSoup
from typing import Optional
from templates.base import BaseParser

class DouParser(BaseParser):
    @property
    def source_name(self)->str:
        return 'dou'

    def get_vacancy_urls(self, list_html: str) ->list[str]:
        soup = BeautifulSoup(list_html, 'lxml')
        return [a['href'] for a in soup.find_all('a', class_='vt') if a.get('href')]

    def parse_vacancy_page(self, html:str, url:str)->Optional[dict]:
        soup = BeautifulSoup(html, 'lxml')

        title_el=soup.find('h1', class_='g-h2')
        raw_el=soup.find('div', class_='b-typo')
        l_n=soup.find('div', class_='l-n')
        company_el=l_n.find('a') if l_n else None

        return {
            "title":title_el.text.strip() if title_el else None,
            "company":company_el.text.strip() if company_el else None,
            "link":url,
            "raw_text":raw_el.get_text(strip=True) if raw_el else None
        }