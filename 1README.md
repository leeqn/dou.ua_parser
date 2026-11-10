# Job Parser & Skill Analyzer (DOU.ua)
An automated ETL pipeline designed to scrape job vacancies from the DOU.ua platform ("First Job" section), extract key technical skills from text descriptions, and store the processed data into a PostgreSQL relational database.

Stack: BeautifulSoup4, sqlalchemy, postgreSQl, pandas, psycopg2, request, docker

main.py — The core pipeline orchestrator. Manages target URLs, handles data structures cleanup, and coordinates execution flow.
website.py — The data extraction (scraping) module. Handles HTTP session headers, HTML tree parsing, raw DataFrame generation, and DB pipeline execution.
sort.py — The analytical module. Contains the skill_filter text-parsing function and the custom conflict resolution utility for safe bulk operations.

docker run --name postgres-local -e POSTGRES_PASSWORD=1234 -p 5432:5432 -d postgres