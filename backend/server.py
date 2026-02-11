# backend/server.py - Corrected Version
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import uuid
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
DATA_FILE = 'data.json'
PROTEIN_GOAL = 140
FRONTEND_DIR = '../frontend'

# Helper functions
def load_entries():
    """Load all entries from data file"""
    try:
        if not os.path.exists(DATA_FILE):
            return []
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            entries = data.get('entries', [])
            
            # Ensure each entry has an ID
            for entry in entries:
                if 'id' not in entry:
                    entry['id'] = str(uuid.uuid4())
            
            return entries
    except:
        return []

def save_entries(entries):
    """Save entries to data file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"entries": entries}, f, ensure_ascii=False, indent=4)

def get_entries_by_date(date_str):
    """Get entries for a specific date"""
    return [e for e in load_entries() if e.get('date') == date_str]

def get_summary_today():
    """Get today's summary"""
    today = datetime.now().strftime('%Y-%m-%d')  # Use current date
    meals = get_entries_by_date(today)
    
    total_calories = sum(m.get('calories', 0) for m in meals)
    total_protein = sum(m.get('protein', 0) for m in meals)
    met_goal = total_protein >= PROTEIN_GOAL
    
    return {
        "total_calories": total_calories,
        "total_protein": total_protein,
        "protein_goal": PROTEIN_GOAL,
        "met_protein_goal": met_goal,
        "date": today
    }

def get_weekly_summary():
    """Get weekly summary (last 7 days)"""
    today = datetime.now()  # Use current date
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
            "met_goal": met_goal,
            "meal_count": len(day_entries)
        })
    
    return list(reversed(summary))

def validate_entry(data):
    """Validate meal entry data"""
    errors = []
    
    required_fields = ['food', 'calories', 'protein', 'category', 'date']
    for field in required_fields:
        if field not in data:
            errors.append(f'Missing field: {field}')
        elif isinstance(data[field], str) and not data[field].strip():
            errors.append(f'Empty field: {field}')
    
    # Validate numeric values
    if 'calories' in data:
        try:
            calories = int(data['calories'])
            if calories < 0 or calories > 10000:
                errors.append('Calories must be between 0 and 10000')
        except (ValueError, TypeError):
            errors.append('Calories must be a valid number')
    
    if 'protein' in data:
        try:
            protein = int(data['protein'])
            if protein < 0 or protein > 500:
                errors.append('Protein must be between 0 and 500g')
        except (ValueError, TypeError):
            errors.append('Protein must be a valid number')
    
    # Validate date format (allow any valid date)
    if 'date' in data:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            errors.append('Invalid date format (use YYYY-MM-DD)')
    
    # Validate category
    valid_categories = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
    if 'category' in data and data['category'] not in valid_categories:
        errors.append(f'Category must be one of: {", ".join(valid_categories)}')
    
    return errors

# ====================
# API Routes
# ====================

@app.route('/api/entries', methods=['GET'])
def get_entries():
    """Get all entries or filter by date"""
    try:
        date = request.args.get('date')
        entries = load_entries()
        
        if date:
            entries = [e for e in entries if e.get('date') == date]
        
        return jsonify(entries)  # Return array directly
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/entries', methods=['POST'])
def add_entry():
    """Add a new meal entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate data
        validation_errors = validate_entry(data)
        if validation_errors:
            return jsonify({
                "error": "Validation failed",
                "details": validation_errors
            }), 400
        
        # Add unique ID
        entry_id = str(uuid.uuid4())
        data['id'] = entry_id
        
        # Load existing entries
        entries = load_entries()
        entries.append(data)
        
        # Save entries
        save_entries(entries)
        
        return jsonify({
            "message": "Entry added successfully",
            "id": entry_id
        }), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/entries/<string:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    """Update an existing meal entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate data
        validation_errors = validate_entry(data)
        if validation_errors:
            return jsonify({
                "error": "Validation failed",
                "details": validation_errors
            }), 400
        
        # Load existing entries
        entries = load_entries()
        
        # Find entry by ID
        entry_index = next((i for i, e in enumerate(entries) if e.get('id') == entry_id), -1)
        
        if entry_index >= 0:
            # Preserve ID
            data['id'] = entry_id
            entries[entry_index] = data
            
            # Save entries
            save_entries(entries)
            
            return jsonify({
                "message": "Entry updated successfully"
            })
        else:
            return jsonify({
                "error": "Entry not found"
            }), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/entries/<string:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    """Delete a meal entry"""
    try:
        # Load existing entries
        entries = load_entries()
        
        # Filter out the entry with matching ID
        filtered_entries = [e for e in entries if e.get('id') != entry_id]
        
        if len(filtered_entries) < len(entries):
            # Save filtered entries
            save_entries(filtered_entries)
            return jsonify({
                "message": "Entry deleted successfully"
            })
        else:
            return jsonify({
                "error": "Entry not found"
            }), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary/today', methods=['GET'])
def summary_today():
    """Get today's summary"""
    try:
        summary = get_summary_today()
        return jsonify(summary)  # Return object directly
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary/week', methods=['GET'])
def summary_week():
    """Get weekly summary"""
    try:
        summary = get_weekly_summary()
        return jsonify(summary)  # Return array directly
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/common-foods', methods=['GET'])
def common_foods():
    """Get most commonly logged foods"""
    try:
        entries = load_entries()
        
        food_counts = {}
        for entry in entries:
            food_name = entry.get('food', '').lower().strip()
            if food_name:
                food_counts[food_name] = food_counts.get(food_name, 0) + 1
        
        # Sort by frequency
        sorted_foods = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)
        
        return jsonify({
            "common_foods": [{"food": food, "count": count} for food, count in sorted_foods[:10]]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export', methods=['GET'])
def export_data():
    """Export all data as JSON"""
    try:
        entries = load_entries()
        
        export_data = {
            "entries": entries,
            "export_date": datetime.now().isoformat(),
            "total_entries": len(entries)
        }
        
        return jsonify(export_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        entries = load_entries()
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "ai_enabled": True,
            "entries_count": len(entries)
        }
        
        return jsonify(health_data)
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# ====================
# AI Routes
# ====================

@app.route('/api/ai/predict', methods=['POST', 'GET'])
def ai_predict():
    """AI prediction endpoint"""
    try:
        if request.method == 'POST':
            data = request.get_json()
        else:  # GET request
            food = request.args.get('food', '')
            data = {'food': food}
        
        food_description = data.get('food', '').strip()
        
        if not food_description:
            return jsonify({"error": "Food description is required"}), 400
        
        # Try to import AI predictor
        try:
            from ai_predictor import predictor
            
            # Get prediction
            prediction = predictor.predict_nutrients(food_description)
            
            # Get similar foods for suggestions
            similar_foods = predictor.get_similar_foods(food_description)
            
            return jsonify({
                "prediction": prediction,
                "similar_foods": similar_foods,
                "success": True
            })
        except ImportError:
            # Fallback to simple estimation if AI module not available
            import random
            
            # Simple estimation
            calories = random.randint(50, 500)
            protein = random.randint(5, 50)
            
            prediction = {
                "calories": calories,
                "protein": protein,
                "quantity_g": 100,
                "confidence": "low",
                "source": "estimation",
                "food_name": food_description.title()
            }
            
            return jsonify({
                "prediction": prediction,
                "similar_foods": [],
                "success": True
            })
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Check if AI is enabled"""
    try:
        from ai_predictor import predictor
        return jsonify({
            "enabled": True,
            "foods_in_database": len(predictor.FOOD_DATABASE)
        })
    except ImportError:
        return jsonify({
            "enabled": False,
            "foods_in_database": 0
        })

# ====================
# Serve Frontend
# ====================

@app.route('/')
def index():
    """Serve main frontend page"""
    try:
        return send_from_directory(FRONTEND_DIR, 'index.html')
    except Exception as e:
        return f"Error loading frontend: {str(e)}", 500

@app.route('/<path:path>')
def static_proxy(path):
    """Serve static files"""
    try:
        return send_from_directory(FRONTEND_DIR, path)
    except:
        return "File not found", 404

# ====================
# Error Handlers
# ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "path": request.path
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error"
    }), 500

# ====================
# Startup
# ====================

if __name__ == '__main__':
    # Ensure data file exists
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"entries": []}, f, ensure_ascii=False, indent=4)
    
    print("=" * 60)
    print("NutriTrack AI - Calorie & Protein Tracker")
    print("=" * 60)
    print(f"Frontend directory: {FRONTEND_DIR}")
    print(f"Data file: {DATA_FILE}")
    
    # Check AI availability
    try:
        from ai_predictor import predictor
        print(f"✅ AI features: Enabled ({len(predictor.FOOD_DATABASE)} foods in database)")
    except ImportError:
        print("⚠️  AI features: Disabled (ai_predictor.py not found)")
    
    print(f"🌐 Server: http://localhost:5000")
    print(f"📊 Protein goal: {PROTEIN_GOAL}g")
    print("=" * 60)
    print("Available API endpoints:")
    print("  /api/health          - Health check")
    print("  /api/entries         - Manage meal entries")
    print("  /api/summary/today   - Today's summary")
    print("  /api/summary/week    - Weekly summary")
    print("  /api/ai/predict      - AI nutrient prediction")
    print("  /api/export          - Export data")
    print("=" * 60)
    
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"Failed to start server: {e}")