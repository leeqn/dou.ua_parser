# Job Parser & Skill Analyzer (DOU.ua)
 
An automated ETL pipeline that scrapes job vacancies from DOU.ua ("First Job" section), extracts key technical skills from descriptions, and stores the processed data into a PostgreSQL database.
 
**Stack:** BeautifulSoup4, SQLAlchemy, PostgreSQL, pandas, psycopg2, requests, Docker
 
---
 
## Project Structure
 
- `main.py` — core pipeline orchestrator; manages target URLs, handles table cleanup, and coordinates execution flow
- `website.py` — scraping module; handles HTTP sessions, HTML parsing, DataFrame generation, and DB writes
- `sort.py` — analytical module; contains `skill_filter()` for text parsing and a conflict resolution utility for safe bulk upserts
---
 
## How to Run
 
**1. Clone the repo and install dependencies**
```bash
pip install -r requirements.txt
```
 
**2. Configure environment**
```bash
cp .env.example .env
```
Fill in your values in `.env`.
 
**3. Start the database**
```bash
docker-compose up -d
```
 
**4. Run the parser**
```bash
python main.py
```
 
Results are saved to the `vacancies` table in your PostgreSQL database.
