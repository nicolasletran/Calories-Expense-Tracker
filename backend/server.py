# server.py - Clean Flask server
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = 'data.json'

def load_entries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('entries', [])

def save_entries(entries):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"entries": entries}, f, ensure_ascii=False, indent=4)

@app.route('/api/entries', methods=['GET'])
def get_entries():
    entries = load_entries()
    return jsonify(entries)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "Flask is working!"})

if __name__ == '__main__':
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"entries": []}, f, ensure_ascii=False, indent=4)
    print("Starting Flask server...")
    app.run(debug=True, port=5000)