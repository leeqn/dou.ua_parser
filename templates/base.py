import asyncio
import aiohttp
from abc import ABC, abstractmethod
import pandas as pd
from sort import skill_filter
from typing import Optional
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}
class BaseParser(ABC):
    CONCURRENCY_LIMIT: int = 10
    DELAY_RANGE: tuple[float, float] = (0.3, 0.7)

    def __init__(self):
        self.semaphore = asyncio.Semaphore(self.CONCURRENCY_LIMIT)
    @property
    @abstractmethod
    def source_name(self)->str:
        """URL"""
        pass

    @abstractmethod
    def get_vacancy_urls(self, list_html: str)->list[str]:
        """Vacancy URLs"""
        pass

    @abstractmethod
    def parse_vacancy_page(self, html:str, url:str)-> Optional[dict]:
        """Parse data from html"""
        pass

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        async with self.semaphore:
            await asyncio.sleep(random.uniform(*self.DELAY_RANGE))
            try:
                async with session.get(url, headers=HEADERS, timeout=15) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"[{self.source_name}] HTTP error {response.status} for {url}")
            except Exception as e:
                print(f"[{self.source_name}] error {url}: {e}")
        return None

    async def _process_single_vacancy(self, session: aiohttp.ClientSession, url: str)-> Optional[dict]:
        html = await self._fetch(session, url)
        if html:
            return self.parse_vacancy_page(html, url)
        return None

    async def run(self, start_url:str):
        """run cycle"""
        print(f"[{self.source_name}] start crawling {start_url}]")
        async with aiohttp.ClientSession() as session:
            main_html = await self._fetch(session, start_url)
            if not main_html:
                print(f"[{self.source_name}] main html load error")
                return

            urls=self.get_vacancy_urls(main_html)
            print(f"[{self.source_name}] found {len(urls)}")

            tasks=[self._process_single_vacancy(session, url) for url in urls]
            results=await asyncio.gather(*tasks)
            jobs=[j for j in results if j is not None]
            self.save_to_db(jobs)

    def save_to_db(self, jobs: list[dict]) -> None:
        if not jobs:
            print(f"[{self.source_name}] no found vacancies.")
            return

        df = pd.DataFrame(jobs)
        df['found_skills'] = df['raw_text'].apply(skill_filter)
        df.to_csv("vacancies.csv")