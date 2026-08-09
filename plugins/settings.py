POSTGRES_USER='airflow'
POSTGRES_PASSWORD='airflow'
POSTGRES_HOST='postgres'
POSTGRES_PORT='5432'
POSTGRES_DB='airflow'

#if POSTGRES_HOST=='localhost': POSTGRES_HOST='127.0.0.1'
postgres=f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

url = "https://jobs.dou.ua/first-job/"