import requests
import sqlite3
from bs4 import BeautifulSoup

def get_info(url):
    connection = sqlite3.connect('jobs.db')
    cursor = connection.cursor()

#cursor.execute("DROP TABLE IF EXISTS vacancies")

    cursor.execute('''CREATE TABLE IF NOT EXISTS vacancies (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      Title TEXT Not NULL,
                      Company TEXT Not NULL,  
                      Link TEXT Not NULL,
                      Raw_Text TEXT)''')
    connection.commit()

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    #response = requests.get(url, headers=headers)

    with requests.Session() as session:
        response=session.get(url, headers=headers)

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')
        vacancy_links = soup.find_all('a', class_='vt')
        company_name=soup.find('.b-compinfo .l-n a')

        for link in vacancy_links:
            if link:
                title= link.text.strip()
                href= link.get('href')

                temp_url=link.get('href')
                temp_response=requests.get(temp_url, headers=headers)
                temp_soup=BeautifulSoup(temp_response.text, 'html.parser')
                raw = temp_soup.find('div', class_='b-typo')
                raw_text = raw.get_text() if raw else 'None'
                l_n = temp_soup.find('div', class_='l-n')
                company_name=l_n.find('a')
                company = company_name.text.strip() if company_name else 'None'

                cursor.execute(("INSERT INTO vacancies (title,company,link,raw_text) VALUES (?,?,?,?)"),
                (title,company,href,raw_text))
                connection.commit()
                #print(f"Saved {raw_text}")
    connection.close()
    print("DONE")