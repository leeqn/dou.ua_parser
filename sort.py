import json
import re
from pathlib import Path
from sqlalchemy.dialects.postgresql import insert

CONFIG_PATH = Path(__file__).parent / "skills_config.json"

def _load_skill_patterns(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(f"Not found config: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        skill_keys = json.load(f)

    compiled_patterns = {}
    for skill, keywords in skill_keys.items():
        escaped_kw = [re.escape(kw) for kw in keywords]
        pattern_str = r'(?<![\w#+])(' + '|'.join(escaped_kw) + r')(?![\w#+])'
        compiled_patterns[skill] = re.compile(pattern_str, re.IGNORECASE)

    return compiled_patterns

SKILL_PATTERNS = _load_skill_patterns(CONFIG_PATH)


def skill_filter(raw_text: str) -> str:
    if not isinstance(raw_text, str) or not raw_text.strip():
        return 'not found'

    found_skills = []
    for skill, pattern in SKILL_PATTERNS.items():
        if pattern.search(raw_text):
            found_skills.append(skill)

    return ','.join(found_skills) if found_skills else 'not found'


def conflict(table, conn, keys, data_iter):

    data = [dict(zip(keys, row)) for row in data_iter]
    if not data:
        return

    stmt = insert(table.table).values(data)
    stmt = stmt.on_conflict_do_nothing(index_elements=['link'])

    conn.execute(stmt)