import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from website import get_info
 
load_dotenv()
 
POSTGRES_URL = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)
TARGET_URL = os.getenv("TARGET_URL")
 
def delete_table():
    print("Очищення старої таблиці...")
    engine = create_engine(POSTGRES_URL)
    with engine.connect() as connection:
        query = text("""DROP TABLE IF EXISTS vacancies;""")
        connection.execute(query)
        connection.commit()
 
if __name__ == "__main__":
    delete_table()
    get_info(TARGET_URL, POSTGRES_URL)
    print("DONE")
