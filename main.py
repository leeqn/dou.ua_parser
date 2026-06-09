from website import get_info
from sqlalchemy import create_engine, text

def delete_table():
    engine = create_engine('postgresql+psycopg2://postgres:1234@127.0.0.1:5432/postgres')
    with engine.connect() as connection:
        query=text("""DROP TABLE IF EXISTS vacancies;""")
        connection.execute(query)
        connection.commit()
        connection.close()
delete_table()
postgres='postgresql+psycopg2://postgres:1234@127.0.0.1:5432/postgres'
url = "https://jobs.dou.ua/first-job/"
get_info(url)