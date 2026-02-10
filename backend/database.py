import json
from config import DATA_FILE

def load_entries():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('entries', [])
    except FileNotFoundError:
        return []

def save_entries(entries):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"entries": entries}, f, ensure_ascii=False, indent=4)
