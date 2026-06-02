import pandas as pd
from sqlite3 import connect
conn=connect('jobs.db')
jobs=pd.read_sql('SELECT id,Title,Link,Raw_Text from vacancies', conn)

print(jobs.head())

