# server.py - Complete Calorie Tracker Backend with AI
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)

# IMPORTANT: Set the correct path to your frontend folder
app.static_folder = '../frontend'
app.static_url_path = ''
CORS(app)

# Configuration
DATA_FILE = 'data.json'
PROTEIN_GOAL = 140  # daily protein goal in grams

# Import AI predictor
try:
    from ai_predictor import predictor
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False
    print("AI predictor module not found. AI features disabled.")

# Helper functions
def load_entries():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('entries', [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_entries(entries):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"entries": entries}, f, ensure_ascii=False, indent=4)

def get_entries_by_date(date_str):
    return [e for e in load_entries() if e.get('date') == date_str]

def get_summary_today():
    today = datetime.today().strftime('%Y-%m-%d')
    meals = get_entries_by_date(today)
    total_calories = sum(m.get('calories', 0) for m in meals)
    total_protein = sum(m.get('protein', 0) for m in meals)
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
        day_entries = [e for e in entries if e.get('date') == day]
        total_cal = sum(e.get('calories', 0) for e in day_entries)
        total_prot = sum(e.get('protein', 0) for e in day_entries)
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
        entries = [e for e in entries if e.get('date') == date]
    return jsonify(entries)

@app.route('/api/entries', methods=['POST'])
def add_entry():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required = ['food', 'calories', 'protein', 'date']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
        
        entries = load_entries()
        entries.append(data)
        save_entries(entries)
        return jsonify({"message": "Entry added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/entries/<int:index>', methods=['PUT'])
def update_entry(index):
    try:
        data = request.get_json()
        entries = load_entries()
        if 0 <= index < len(entries):
            entries[index] = data
            save_entries(entries)
            return jsonify({"message": "Entry updated"})
        return jsonify({"error": "Index out of range"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/entries/<int:index>', methods=['DELETE'])
def delete_entry(index):
    try:
        entries = load_entries()
        if 0 <= index < len(entries):
            entries.pop(index)
            save_entries(entries)
            return jsonify({"message": "Entry deleted"})
        return jsonify({"error": "Index out of range"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary/today', methods=['GET'])
def summary_today():
    return jsonify(get_summary_today())

@app.route('/api/summary/week', methods=['GET'])
def summary_week():
    return jsonify(get_weekly_summary())

# ------------------ AI Routes ------------------

@app.route('/api/ai/predict', methods=['POST', 'GET'])
def ai_predict():
    """AI prediction endpoint"""
    try:
        if not AI_ENABLED:
            return jsonify({
                "error": "AI features are not enabled",
                "success": False
            }), 503
        
        if request.method == 'POST':
            data = request.get_json()
        else:  # GET request
            food = request.args.get('food', '')
            data = {'food': food}
        
        food_description = data.get('food', '').strip()
        
        if not food_description:
            return jsonify({"error": "Food description is required", "success": False}), 400
        
        # Get prediction
        prediction = predictor.predict_nutrients(food_description)
        
        # Get similar foods for suggestions
        similar_foods = predictor.get_similar_foods(food_description)
        
        return jsonify({
            "prediction": prediction,
            "similar_foods": similar_foods,
            "success": True
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/ai/foods/search', methods=['GET'])
def ai_search_foods():
    """Search for foods in database"""
    if not AI_ENABLED:
        return jsonify({"results": [], "message": "AI disabled"})
    
    query = request.args.get('q', '').lower().strip()
    
    if not query or len(query) < 2:
        return jsonify({"results": []})
    
    results = []
    for food_name, nutrients in predictor.FOOD_DATABASE.items():
        if query in food_name:
            results.append({
                "name": food_name.title(),
                "calories": nutrients["calories"],
                "protein": nutrients["protein"],
                "fat": nutrients["fat"],
                "carbs": nutrients["carbs"]
            })
    
    return jsonify({"results": results[:10]})  # Limit to 10 results

@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Check if AI is enabled"""
    return jsonify({
        "enabled": AI_ENABLED,
        "foods_in_database": len(predictor.FOOD_DATABASE) if AI_ENABLED else 0
    })

# ------------------ Serve Frontend ------------------

@app.route('/')
def index():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return f"Error loading frontend: {str(e)}", 500

@app.route('/<path:path>')
def static_proxy(path):
    try:
        return send_from_directory(app.static_folder, path)
    except Exception as e:
        return f"File not found: {path}", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "ai_enabled": AI_ENABLED
    })

# ------------------ Run App ------------------

if __name__ == '__main__':
    # Ensure data file exists
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"entries": []}, f, ensure_ascii=False, indent=4)
    
    print(f"Static folder path: {app.static_folder}")
    print(f"Starting Calorie Tracker on http://localhost:5000")
    print(f"API Base URL: http://localhost:5000/api")
    print(f"AI Features: {'Enabled' if AI_ENABLED else 'Disabled'}")
    
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"Failed to start server: {e}")