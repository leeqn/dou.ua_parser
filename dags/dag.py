from website import table, response_f, get_info, sort_to_sql
import settings
from datetime import datetime
from airflow.decorators import dag, task
@dag (
    dag_id = "get_info",
    schedule='@weekly',
    start_date=datetime(2026,7,6),
    catchup=False,
    tags=["get_info"]
)

def pipeline():
    @task()
    def init_db_table():
        table(settings.postgres)

    @task()
    def fetch_data():
        response,headers=response_f(settings.url)
        return [response, headers]

    @task()
    def parse_data(fetch_result):
        response, headers = fetch_result[0], fetch_result[1]
        return get_info(response, headers)

    @task()
    def save_data(parsed_data):
        sort_to_sql(parsed_data,settings.postgres)

    db_init = init_db_table()
    site_response = fetch_data()
    parsed_info = parse_data(site_response)
    save_step=save_data(parsed_info)

    db_init>>save_step

pipeline()
