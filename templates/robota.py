import random
import asyncio
from typing import Optional
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession
from templates.base import BaseParser


class RobotaParser(BaseParser):
    CONCURRENCY_LIMIT = 3
    DELAY_RANGE = (1.0, 2.0)

    GRAPHQL_URL = "https://dracula.robota.ua/?q=getPublishedVacancyById"
    VACANCY_QUERY = """
    query getPublishedVacancyById($id: ID!) {
      publishedVacancy(id: $id) {
        id
        title
        description
        company {
          id
          name
        }
      }
    }
    """

    @property
    def source_name(self) -> str:
        return "robota"

    def get_vacancy_urls(self, list_html: str) -> list[str]:
        return []

    def parse_vacancy_page(self, html: str, url: str) -> Optional[dict]:
        return None

    async def _fetch_vacancy_graphql(self, session: AsyncSession, vac_id: int, headers: dict) -> Optional[dict]:
        async with self.semaphore:
            await asyncio.sleep(random.uniform(*self.DELAY_RANGE))
            payload = {
                "operationName": "getPublishedVacancyById",
                "variables": {"id": str(vac_id)},
                "query": self.VACANCY_QUERY,
            }
            try:
                resp = await session.post(self.GRAPHQL_URL, json=payload, headers=headers, timeout=15)
                if resp.status_code != 200:
                    print(f"[{self.source_name}] GraphQL HTTP {resp.status_code} для ID {vac_id}")
                    return None

                data = resp.json().get("data", {}).get("publishedVacancy")
                if not data or not data.get("title"):
                    return None

                company_data = data.get("company") or {}
                company_id = company_data.get("id", 0)
                company_name = company_data.get("name", "None")

                clean_desc = BeautifulSoup(data.get("description", ""), "html.parser").get_text(" ", strip=True)

                return {
                    "title": data["title"],
                    "company": company_name,
                    "link": f"https://robota.ua/company{company_id}/vacancy{vac_id}",
                    "raw_text": clean_desc,
                }
            except Exception as e:
                print(f"[{self.source_name}] GraphQL error for ID {vac_id}: {e}")
                return None

    async def run(self, start_url: str):
        query = start_url.split("/zapros/")[-1].split("/")[0]
        print(f"[{self.source_name}] start API crawling for: {query}")

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://robota.ua",
            "Referer": "https://robota.ua/",
        }

        async with AsyncSession(impersonate="chrome") as session:
            await session.get("https://robota.ua/", timeout=15)
            await asyncio.sleep(random.uniform(1.0, 2.0))

            search_payload = {"keywords": query, "page": 0, "pageSize": 20, "cityId": 0}
            resp = await session.post(
                "https://api.robota.ua/vacancy/search",
                json=search_payload,
                headers=headers,
                timeout=15,
            )
            if resp.status_code != 200:
                print(f"[{self.source_name}] Search API HTTP error {resp.status_code}")
                return

            docs = resp.json().get("documents", [])
            vac_ids = [d["id"] for d in docs if d.get("id")]
            print(f"[{self.source_name}] found {len(vac_ids)}")

            tasks = [self._fetch_vacancy_graphql(session, vid, headers) for vid in vac_ids]
            results = await asyncio.gather(*tasks)
            jobs = [j for j in results if j is not None]
            self.save_to_db(jobs)