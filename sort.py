import sqlite3
import pandas as pd

SKILL_KEYS  ={'Python':['python','numpy','sklearn','pandas'],
        'SQL':['sql','mysql','postgresql','бази даних'],
        'Docker':['docker'],
        'Git':['git'],
        'Linux':['linux'],
        'Machine Learning':['machine learning','ml','pytorch','tensorflow'],
        'English':['English','англійський','intermediate','знання англійської мови'],
        'Degree':['degree','освіта','повна вища технічна освіта'],}

conn = sqlite3.connect('jobs.db')
vacancies = pd.read_sql("SELECT * FROM vacancies", conn)
conn.close()

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

vacancies['Found_Skills'] = vacancies['Raw_Text'].apply(skill_filter)

print(vacancies[['Title', 'Found_Skills']].head(15))