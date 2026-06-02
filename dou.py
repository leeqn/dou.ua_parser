import requests
import sqlite3
from bs4 import BeautifulSoup

url = "https://jobs.dou.ua/first-job/"
connection = sqlite3.connect('jobs.db')
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS vacancies (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  Title TEXT Not NULL,
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

    for link in vacancy_links:
        title= link.text.strip()
        href= link.get('href')

        temp_url=href
        temp_response=session.get(temp_url, headers=headers)
        temp_soup=BeautifulSoup(response.text, 'html.parser')
        raw_text = temp_soup.find('div', class_='b-typo')

        cursor.execute(("INSERT INTO vacancies (title,link,raw_text) VALUES (?,?,?)"),
        (title,href,raw_text))
        connection.commit()
        print(f"Saved {title}")
connection.close()
print("DONE")

