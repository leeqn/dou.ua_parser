import pandas as pd
from website import get_info
from sort import skill_filter
from sqlalchemy import create_engine, text

def delete_table():
    engine = create_engine('postgresql://postgres:1234@localhost:5432/postgres')
    with engine.connect() as connection:
        query=text("""DROP TABLE vacancies;""")
        connection.execute(query)
        connection.commit()
        connection.close()

url = "https://jobs.dou.ua/first-job/"
get_info(url)

engine = create_engine('postgresql+psycopg2://postgres:1234@127.0.0.1:5432/postgres')
with engine.connect() as connection:
    query=text("""SELECT id,Title,Link,Raw_Text,Company from vacancies""")
    jobs=pd.read_sql(query, connection, index_col='id')
    jobs['Found_Skills'] = jobs['Raw_Text'].apply(skill_filter)
    print(jobs.head())
    jobs.to_csv('jobs.csv')
