from website import get_info
from sqlalchemy import create_engine, text
from settings import postgres,url

def delete_table():
    engine = create_engine(postgres)
    with engine.connect() as connection:
        query=text("""DROP TABLE IF EXISTS vacancies;""")
        connection.execute(query)
        connection.commit()
        connection.close()

get_info(url,postgres)