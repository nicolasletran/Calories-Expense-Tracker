# backend/config.py
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
ENV_FILE = os.path.join(BASE_DIR, '.env')

# Configuration with defaults
PROTEIN_GOAL = int(os.getenv('PROTEIN_GOAL', 140))  # daily protein goal in grams
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', 5000))
AI_ENABLED = os.getenv('AI_ENABLED', 'True').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')

# Validation limits
MAX_CALORIES = int(os.getenv('MAX_CALORIES', 10000))
MAX_PROTEIN = int(os.getenv('MAX_PROTEIN', 500))
MIN_CALORIES = int(os.getenv('MIN_CALORIES', 0))
MIN_PROTEIN = int(os.getenv('MIN_PROTEIN', 0))

# Caching
CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))  # 5 minutes

# Rate limiting (requests per minute)
RATE_LIMIT = int(os.getenv('RATE_LIMIT', 60))

# Frontend configuration
FRONTEND_DIR = os.path.join(BASE_DIR, '../frontend')
ALLOWED_EXTENSIONS = {'json'}

# App metadata
APP_NAME = "NutriTrack AI"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-powered calorie and protein tracker"
APP_AUTHOR = "NutriTrack Team"

def check_data_file():
    """Ensure data file exists with proper structure"""
    if not os.path.exists(DATA_FILE):
        print(f"Creating new data file at {DATA_FILE}")
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "entries": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat(),
                    "total_entries": 0,
                    "version": APP_VERSION
                }
            }, f, ensure_ascii=False, indent=4)
    else:
        # Ensure file has proper structure
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "entries" not in data:
                    data["entries"] = []
                if "metadata" not in data:
                    data["metadata"] = {
                        "created_at": datetime.now().isoformat(),
                        "last_modified": datetime.now().isoformat(),
                        "total_entries": len(data.get("entries", [])),
                        "version": APP_VERSION
                    }
                data["metadata"]["last_modified"] = datetime.now().isoformat()
                data["metadata"]["total_entries"] = len(data["entries"])
                
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is corrupted, create a new one
            print(f"Data file corrupted, creating new one at {DATA_FILE}")
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "entries": [],
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "last_modified": datetime.now().isoformat(),
                        "total_entries": 0,
                        "version": APP_VERSION
                    }
                }, f, ensure_ascii=False, indent=4)

def get_config_summary():
    """Get configuration summary for debugging"""
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "debug": DEBUG,
        "port": PORT,
        "host": HOST,
        "ai_enabled": AI_ENABLED,
        "protein_goal": PROTEIN_GOAL,
        "data_file": DATA_FILE,
        "frontend_dir": FRONTEND_DIR,
        "cache_timeout": CACHE_TIMEOUT,
        "rate_limit": RATE_LIMIT
    }

# Initialize data file on import
check_data_file()

if __name__ == "__main__":
    # Print config summary when run directly
    summary = get_config_summary()
    print("Configuration Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")