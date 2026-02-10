from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

DATA_FILE = 'data.json'
PROTEIN_GOAL = 140  # daily protein goal in grams

# ------------------ Helpers ------------------

def load_entries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('entries', [])

def save_entries(entries):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"entries": entries}, f, ensure_ascii=False, indent=4)

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

# ------------------ API Routes ------------------

@app.route('/api/entries', methods=['GET'])
def get_entries():
    date = request.args.get('date')
    entries = load_entries()
    if date:
        entries = [e for e in entries if e['date'] == date]
    return jsonify(entries)

@app.route('/api/entries', methods=['POST'])
def add_entry():
    data = request.get_json()
    entries = load_entries()
    entries.append(data)
    save_entries(entries)
    return jsonify({"message": "Entry added"}), 201

@app.route('/api/entries/<int:index>', methods=['PUT'])
def update_entry(index):
    data = request.get_json()
    entries = load_entries()
    if 0 <= index < len(entries):
        entries[index] = data
        save_entries(entries)
        return jsonify({"message": "Entry updated"})
    return jsonify({"error": "Index out of range"}), 404

@app.route('/api/entries/<int:index>', methods=['DELETE'])
def delete_entry(index):
    entries = load_entries()
    if 0 <= index < len(entries):
        entries.pop(index)
        save_entries(entries)
        return jsonify({"message": "Entry deleted"})
    return jsonify({"error": "Index out of range"}), 404

@app.route('/api/summary/today', methods=['GET'])
def summary_today():
    return jsonify(get_summary_today())

@app.route('/api/summary/week', methods=['GET'])
def summary_week():
    return jsonify(get_weekly_summary())

# ------------------ Serve Frontend ------------------

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# ------------------ Run App ------------------

if __name__ == '__main__':
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"entries": []}, f, ensure_ascii=False, indent=4)
    app.run(debug=True, port=5000)