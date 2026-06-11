import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine, text
from sort import skill_filter, conflict

def get_info(url, db_url):
    engine = create_engine(db_url)
    jobs = []

    with engine.connect() as connection:
        query = text('''
            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,  
                link TEXT NOT NULL UNIQUE,
                raw_text TEXT,
                found_skills TEXT
            )''')
        connection.execute(query)
        connection.commit()

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    print(f"Починаємо парсинг: {url}")
    with requests.Session() as session:
        response = session.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Помилка доступу до сайту: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        vacancy_links = soup.find_all('a', class_='vt')

        for link in vacancy_links:
            href = link.get('href')
            if not href:
                continue
                
            title = link.text.strip()
            
            try:
                temp_response = session.get(href, headers=headers)
                temp_soup = BeautifulSoup(temp_response.text, 'html.parser')
                
                raw = temp_soup.find('div', class_='b-typo')
                raw_text = raw.get_text() if raw else 'None'
                
                l_n = temp_soup.find('div', class_='l-n')
                company_name = l_n.find('a') if l_n else None
                company = company_name.text.strip() if company_name else 'None'
                
                vacancy_dict = {
                    "title": title,
                    "company": company,
                    "link": href,
                    "raw_text": raw_text
                }
                jobs.append(vacancy_dict)
                print(f"Оброблено вакансію: {title} в {company}")
            except Exception as e:
                print(f"Помилка при парсингу вакансії {href}: {e}")
            time.sleep(1)

    if jobs:
        df = pd.DataFrame(jobs)
        df['found_skills'] = df['raw_text'].apply(skill_filter)
        
        with engine.connect() as connection:
            df.to_sql('vacancies', con=connection, if_exists='append', index=False, method=conflict)
            connection.commit()  
        print(f"Успішно збережено {len(jobs)} вакансій.")
    else:
        print("Вакансій не знайдено.")