import re
from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from templates.base import BaseParser


class RobotaParser(BaseParser):
    BASE_URL = "https://robota.ua"
    CONCURRENCY_LIMIT = 1
    DELAY_RANGE = (1.5, 3.5)
    WARMUP_HOME = True

    @property
    def source_name(self) -> str:
        return "robota"

    def get_vacancy_urls(self, list_html: str) -> list[str]:
        soup = BeautifulSoup(list_html, "html.parser")
        urls = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if re.search(r"/company\d+/vacancy\d+", href):
                clean_path = href.split("?")[0]
                full_url = urljoin(self.BASE_URL, clean_path)
                if full_url not in urls:
                    urls.append(full_url)
        return urls

    def parse_vacancy_page(self, html: str, url: str) -> Optional[dict]:
        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.find("h1")
        if not title_tag:
            return None
        title = title_tag.get_text(strip=True)
        company_tag = soup.find("a", href=re.compile(r"^/company\d+$"))
        company = company_tag.get_text(strip=True) if company_tag else "Не указана"

        desc_block = (
            soup.find("div", class_=re.compile(r"description", re.I))
            or soup.find("alliance-vacancy-description")
            or soup.find("main")
        )
        if not desc_block:
            return None

        raw_text = desc_block.get_text(separator=" ", strip=True)

        return {
            "title": title,
            "company": company,
            "link": url,
            "raw_text": raw_text,
        }