import pandas as pd
from website import get_info
from sort import skill_filter
from sqlite3 import connect

def delete_table():
    conn=connect('jobs.db')
    cursor=conn.cursor()
    cursor.execute("DELETE FROM vacancies")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='vacancies'")
    conn.commit()
    conn.close()

#interface
url = "https://jobs.dou.ua/first-job/"

get_info(url)

conn=connect('jobs.db')
jobs=pd.read_sql('SELECT id,Title,Link,Raw_Text,Company from vacancies', conn, index_col='id')
jobs['Found_Skills'] = jobs['Raw_Text'].apply(skill_filter)
print(jobs.head())
jobs.to_csv('jobs.csv')
