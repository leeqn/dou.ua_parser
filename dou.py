import requests
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup

url = "https://jobs.dou.ua/first-job/"
connection = sqlite3.connect('jobs.db')
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS vacancies (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  Title TEXT Not NULL,
                  Link TEXT Not NULL,,
                  Raw_Text TEXT)''')
connection.commit()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:

    soup = BeautifulSoup(response.text, 'html.parser')
    vacancy_links = soup.find_all('a', class_='vt')

    title_list=[]
    href_list=[]
    raw_list=[]

    for link in vacancy_links:
        temp_url = link.get('href')
        temp_response = requests.get(temp_url, headers=headers)
        temp_soup = BeautifulSoup(temp_response.text, 'html.parser')
        raw=temp_soup.find('div', class_='b-typo')

        raw_text=raw.get_text()
        title= link.text.strip()
        href= link.get('href')

        cursor.execute('SELECT id FROM vacancies WHERE link = ?', (href,))
        title_list.append(title)
        href_list.append(href)

    vacancies = pd.DataFrame({'Title': title_list, 'Link': href_list, 'Raw': raw_list})
    print(vacancies.head())

