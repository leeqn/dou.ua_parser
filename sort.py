from sqlalchemy.dialects.postgresql import insert

SKILL_KEYS = {
    'Python': ['python', 'numpy', 'sklearn', 'pandas'],
    'SQL': ['sql', 'mysql', 'postgresql', 'бази даних'],
    'Docker': ['docker'],
    'Git': ['git'],
    'Linux': ['linux'],
    'Machine Learning': ['machine learning', 'ml', 'pytorch', 'tensorflow'],
    'English': ['english', 'англійський', 'intermediate', 'знання англійської мови'],
    'Degree': ['degree', 'освіта', 'повна вища технічна освіта'],
}

def skill_filter(raw_text):
    if not isinstance(raw_text, str):
        return 'not found'

    text_lower = raw_text.lower()
    founded_skills = []

    for skill, markers in SKILL_KEYS.items():
        if any(m in text_lower for m in markers):
            founded_skills.append(skill)

    return ','.join(founded_skills) if founded_skills else 'not found'

def conflict(table, connection, keys, data_iter):
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = insert(table.table).values(data)
    stmt = stmt.on_conflict_do_nothing(index_elements=['link'])
    connection.execute(stmt)