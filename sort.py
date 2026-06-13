from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
import pandas as pd
from settings import postgres

SKILL_KEYS = {'Python': ['python', 'numpy', 'sklearn', 'pandas'],
              'SQL': ['sql', 'mysql', 'postgresql', 'бази даних'],
              'Docker': ['docker'],
              'Git': ['git'],
              'Linux': ['linux'],
              'Machine Learning': ['machine learning', 'ml', 'pytorch', 'tensorflow'],
              'English': ['English', 'англійський', 'intermediate', 'знання англійської мови'],
              'Degree': ['degree', 'освіта', 'повна вища технічна освіта'], }

engine=create_engine(postgres)
with engine.connect() as connection:

    vacancies = pd.read_sql("""SELECT id,title,link,raw_text,company from vacancies""", connection)
    connection.commit()
    connection.close()


    def conflict(table, connection, keys, data_iter):
        data = [dict(zip(keys, row)) for row in data_iter]
        stmt = insert(table.table).values(data)
        stmt = stmt.on_conflict_do_nothing(index_elements=['link'])
        connection.execute(stmt)

    def skill_filter(raw_text):

        if not isinstance(raw_text,str):
            return 'not found'

        text=raw_text.lower()
        founded_skills=[]

        for skill,markers in SKILL_KEYS.items():
            if any(markers in text for markers in markers):
                founded_skills.append(skill)

        if len(founded_skills)>0:
            return ','.join(founded_skills)
        else:
            return 'not found'

    vacancies['found_skills'] = vacancies['raw_text'].apply(skill_filter)

#    print(vacancies[['title', 'found_skills']].head(15))