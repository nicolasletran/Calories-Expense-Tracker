from database import load_entries, save_entries
from config import PROTEIN_GOAL
from datetime import datetime, timedelta

def get_entries_by_date(date_str):
    return [e for e in load_entries() if e['date'] == date_str]

def get_summary_today():
    today = datetime.today().strftime('%Y-%m-%d')
    meals = get_entries_by_date(today)
    total_calories = sum(m['calories'] for m in meals)
    total_protein = sum(m['protein'] for m in meals)
    met_goal = total_protein >= PROTEIN_GOAL
    return {
        "total_calories": total_calories,
        "total_protein": total_protein,
        "protein_goal": PROTEIN_GOAL,
        "met_protein_goal": met_goal
    }

def get_weekly_summary():
    today = datetime.today()
    entries = load_entries()
    summary = []
    for i in range(7):
        day = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        day_entries = [e for e in entries if e['date'] == day]
        total_cal = sum(e['calories'] for e in day_entries)
        total_prot = sum(e['protein'] for e in day_entries)
        met_goal = total_prot >= PROTEIN_GOAL
        summary.append({
            "date": day,
            "calories": total_cal,
            "protein": total_prot,
            "met_goal": met_goal
        })
    return list(reversed(summary))
