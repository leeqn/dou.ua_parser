import asyncio
from abc import ABC, abstractmethod
import pandas as pd
from sort import skill_filter
from typing import Optional
from curl_cffi.requests import AsyncSession
import random

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

    async def _fetch(self, session: AsyncSession, url: str) -> Optional[str]:
        async with self.semaphore:
            await asyncio.sleep(random.uniform(*self.DELAY_RANGE))
            try:
                response = await session.get(url, timeout=15)
                if response.status_code == 200:
                    return response.text
                print(f"[{self.source_name}] HTTP error {response.status_code} for {url}")
            except Exception as e:
                print(f"[{self.source_name}] Error {url}: {e}")
        return None

    async def _process_single_vacancy(self, session: AsyncSession, url: str)-> Optional[dict]:
        html = await self._fetch(session, url)
        if html:
            return self.parse_vacancy_page(html, url)
        return None

    async def run(self, start_url:str):
        """run cycle"""
        print(f"[{self.source_name}] start crawling {start_url}]")
        async with AsyncSession(impersonate="safari") as session:
            main_html = await self._fetch(session, start_url)
            if not main_html:
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
        df.to_csv(f"vacancies_{self.source_name}.csv")