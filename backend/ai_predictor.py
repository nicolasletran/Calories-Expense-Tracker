# backend/ai_predictor.py
import json
import random
import re
from typing import Dict, Optional, List
from functools import lru_cache

class NutrientPredictor:
    """AI-powered nutrient prediction for common foods"""
    
    # Enhanced Food database with average nutritional values per 100g
    FOOD_DATABASE = {
        # Proteins
        "chicken breast": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
        "chicken": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
        "chicken wing": {"calories": 203, "protein": 30, "fat": 8, "carbs": 0},
        "chicken thigh": {"calories": 209, "protein": 26, "fat": 11, "carbs": 0},
        "salmon": {"calories": 208, "protein": 20, "fat": 13, "carbs": 0},
        "tuna": {"calories": 132, "protein": 29, "fat": 1, "carbs": 0},
        "beef": {"calories": 250, "protein": 26, "fat": 17, "carbs": 0},
        "pork": {"calories": 242, "protein": 25, "fat": 14, "carbs": 0},
        "pork chop": {"calories": 231, "protein": 29, "fat": 12, "carbs": 0},
        "bacon": {"calories": 541, "protein": 37, "fat": 42, "carbs": 1.4},
        "eggs": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
        "egg": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1},
        
        # Seafood
        "shrimp": {"calories": 85, "protein": 20, "fat": 0.5, "carbs": 0},
        "crab": {"calories": 87, "protein": 18, "fat": 1, "carbs": 0},
        "lobster": {"calories": 90, "protein": 19, "fat": 0.5, "carbs": 1},
        "squid": {"calories": 92, "protein": 16, "fat": 1.4, "carbs": 3},
        "octopus": {"calories": 82, "protein": 15, "fat": 1, "carbs": 2.2},
        "mussel": {"calories": 86, "protein": 12, "fat": 2, "carbs": 4},
        
        # Dairy
        "milk": {"calories": 61, "protein": 3.2, "fat": 3.3, "carbs": 4.8},
        "cheese": {"calories": 404, "protein": 25, "fat": 33, "carbs": 1.3},
        "yogurt": {"calories": 59, "protein": 3.5, "fat": 0.4, "carbs": 10},
        "protein shake": {"calories": 120, "protein": 25, "fat": 2, "carbs": 3},
        "cottage cheese": {"calories": 98, "protein": 11, "fat": 4.3, "carbs": 3.4},
        "butter": {"calories": 717, "protein": 0.9, "fat": 81, "carbs": 0.1},
        
        # Grains & Carbs
        "rice": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
        "fried rice": {"calories": 163, "protein": 4.5, "fat": 5, "carbs": 25},
        "pasta": {"calories": 131, "protein": 5, "fat": 1.1, "carbs": 25},
        "bread": {"calories": 265, "protein": 9, "fat": 3.2, "carbs": 49},
        "potato": {"calories": 77, "protein": 2, "fat": 0.1, "carbs": 17},
        "sweet potato": {"calories": 86, "protein": 1.6, "fat": 0.1, "carbs": 20},
        "noodles": {"calories": 138, "protein": 4.5, "fat": 2.1, "carbs": 25},
        "oatmeal": {"calories": 68, "protein": 2.4, "fat": 1.4, "carbs": 12},
        "quinoa": {"calories": 120, "protein": 4.4, "fat": 1.9, "carbs": 21},
        
        # Vegetables
        "broccoli": {"calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7},
        "spinach": {"calories": 23, "protein": 2.9, "fat": 0.4, "carbs": 3.6},
        "carrot": {"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10},
        "lettuce": {"calories": 15, "protein": 1.4, "fat": 0.2, "carbs": 2.9},
        "cabbage": {"calories": 25, "protein": 1.3, "fat": 0.1, "carbs": 6},
        "cauliflower": {"calories": 25, "protein": 2, "fat": 0.3, "carbs": 5},
        "bell pepper": {"calories": 31, "protein": 1, "fat": 0.3, "carbs": 6},
        "onion": {"calories": 40, "protein": 1.1, "fat": 0.1, "carbs": 9},
        "garlic": {"calories": 149, "protein": 6.4, "fat": 0.5, "carbs": 33},
        "tomato": {"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9},
        "cucumber": {"calories": 15, "protein": 0.7, "fat": 0.1, "carbs": 3.6},
        
        # Fruits
        "apple": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14},
        "banana": {"calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23},
        "orange": {"calories": 47, "protein": 0.9, "fat": 0.1, "carbs": 12},
        "grape": {"calories": 69, "protein": 0.7, "fat": 0.2, "carbs": 18},
        "strawberry": {"calories": 32, "protein": 0.7, "fat": 0.3, "carbs": 7.7},
        "blueberry": {"calories": 57, "protein": 0.7, "fat": 0.3, "carbs": 14},
        "mango": {"calories": 60, "protein": 0.8, "fat": 0.4, "carbs": 15},
        "pineapple": {"calories": 50, "protein": 0.5, "fat": 0.1, "carbs": 13},
        "watermelon": {"calories": 30, "protein": 0.6, "fat": 0.2, "carbs": 8},
        
        # Nuts & Seeds
        "almonds": {"calories": 579, "protein": 21, "fat": 50, "carbs": 22},
        "peanut butter": {"calories": 588, "protein": 25, "fat": 50, "carbs": 20},
        "peanut": {"calories": 567, "protein": 26, "fat": 49, "carbs": 16},
        "walnut": {"calories": 654, "protein": 15, "fat": 65, "carbs": 14},
        "cashew": {"calories": 553, "protein": 18, "fat": 44, "carbs": 30},
        "sunflower seed": {"calories": 584, "protein": 21, "fat": 51, "carbs": 20},
        "chia seed": {"calories": 486, "protein": 17, "fat": 31, "carbs": 42},
        
        # Asian & Vietnamese Foods
        "pho": {"calories": 350, "protein": 15, "fat": 10, "carbs": 50},
        "ramen": {"calories": 400, "protein": 12, "fat": 15, "carbs": 55},
        "spring roll": {"calories": 80, "protein": 4, "fat": 3, "carbs": 10},
        "dumpling": {"calories": 40, "protein": 2, "fat": 1, "carbs": 6},
        "tofu": {"calories": 76, "protein": 8, "fat": 4.8, "carbs": 1.9},
        "tempeh": {"calories": 193, "protein": 19, "fat": 11, "carbs": 9},
        "miso soup": {"calories": 35, "protein": 2, "fat": 1, "carbs": 5},
        "sushi": {"calories": 150, "protein": 4, "fat": 1, "carbs": 30},
        "kimchi": {"calories": 24, "protein": 1.1, "fat": 0.5, "carbs": 4},
        "fish sauce": {"calories": 8, "protein": 1, "fat": 0, "carbs": 2},
        "soy sauce": {"calories": 53, "protein": 8, "fat": 0.1, "carbs": 5},
        
        # Vietnamese Dishes
        "banh mi": {"calories": 350, "protein": 15, "fat": 10, "carbs": 45},
        "pho bo": {"calories": 380, "protein": 20, "fat": 12, "carbs": 50},
        "pho ga": {"calories": 350, "protein": 18, "fat": 8, "carbs": 50},
        "bun cha": {"calories": 420, "protein": 25, "fat": 15, "carbs": 45},
        "com tam": {"calories": 450, "protein": 25, "fat": 12, "carbs": 55},
        "goi cuon": {"calories": 90, "protein": 6, "fat": 2, "carbs": 12},
        "banh xeo": {"calories": 280, "protein": 10, "fat": 15, "carbs": 25},
        
        # Plant-based Proteins
        "lentils": {"calories": 116, "protein": 9, "fat": 0.4, "carbs": 20},
        "chickpeas": {"calories": 139, "protein": 7, "fat": 2, "carbs": 23},
        "black beans": {"calories": 132, "protein": 9, "fat": 0.5, "carbs": 24},
        "kidney beans": {"calories": 127, "protein": 8.7, "fat": 0.5, "carbs": 22},
        
        # Common Dishes
        "pizza": {"calories": 266, "protein": 11, "fat": 10, "carbs": 33},
        "burger": {"calories": 295, "protein": 17, "fat": 14, "carbs": 30},
        "sandwich": {"calories": 250, "protein": 10, "fat": 8, "carbs": 35},
        "salad": {"calories": 150, "protein": 5, "fat": 8, "carbs": 15},
        "spaghetti bolognese": {"calories": 160, "protein": 8, "fat": 5, "carbs": 22},
        "chicken curry": {"calories": 180, "protein": 15, "fat": 10, "carbs": 12},
        "beef stew": {"calories": 220, "protein": 20, "fat": 12, "carbs": 8},
        "vegetable soup": {"calories": 60, "protein": 2, "fat": 1, "carbs": 12},
        "fried chicken": {"calories": 290, "protein": 20, "fat": 15, "carbs": 20},
        
        # Beverages
        "coffee": {"calories": 2, "protein": 0.3, "fat": 0, "carbs": 0},
        "tea": {"calories": 1, "protein": 0, "fat": 0, "carbs": 0.3},
        "soda": {"calories": 41, "protein": 0, "fat": 0, "carbs": 10},
        "juice": {"calories": 45, "protein": 0.5, "fat": 0.1, "carbs": 11},
        "water": {"calories": 0, "protein": 0, "fat": 0, "carbs": 0},
        "beer": {"calories": 43, "protein": 0.5, "fat": 0, "carbs": 3.6},
        "wine": {"calories": 83, "protein": 0.1, "fat": 0, "carbs": 2.6},
        "whiskey": {"calories": 250, "protein": 0, "fat": 0, "carbs": 0.1},
        "smoothie": {"calories": 120, "protein": 3, "fat": 1, "carbs": 25},
        
        # Condiments & Sauces
        "ketchup": {"calories": 101, "protein": 1.3, "fat": 0.1, "carbs": 25},
        "mayonnaise": {"calories": 680, "protein": 1, "fat": 75, "carbs": 2},
        "mustard": {"calories": 66, "protein": 4.4, "fat": 3.3, "carbs": 6},
        "honey": {"calories": 304, "protein": 0.3, "fat": 0, "carbs": 82},
        "maple syrup": {"calories": 260, "protein": 0, "fat": 0, "carbs": 67},
        "olive oil": {"calories": 884, "protein": 0, "fat": 100, "carbs": 0},
    }
    
    @classmethod
    def extract_weight(cls, food_description: str) -> Optional[float]:
        """Extract weight in grams from food description including Vietnamese units"""
        patterns = [
            # Standard units
            r'(\d+)\s*g(?:ram)?s?',           # 200g, 200 grams
            r'(\d+\.\d+)\s*g(?:ram)?s?',      # 200.5g
            r'(\d+)\s*oz',                    # 8oz
            r'(\d+)\s*ounce',                 # 8 ounce
            r'(\d+)\s*ml',                    # 250ml
            r'(\d+)\s*lb',                    # 1lb
            r'(\d+)\s*pound',                 # 1 pound
            
            # Metric units
            r'(\d+)\s*kg',                    # 1kg
            r'(\d+\.\d+)\s*kg',               # 1.5kg
            r'(\d+)\s*kilogram',              # 1 kilogram
            
            # Vietnamese units
            r'(\d+)\s*cân',                   # Vietnamese: cân (approximately 500g)
            r'(\d+)\s*lạng',                  # Vietnamese: lạng (approximately 100g)
            r'(\d+)\s*chỉ',                   # Vietnamese: chỉ (approximately 3.75g)
            
            # Portion sizes (common phrases)
            r'(\d+)\s*slice',                 # 2 slices
            r'(\d+)\s*piece',                 # 3 pieces
            r'(\d+)\s*cup',                   # 1 cup
            r'(\d+\.\d+)\s*cup',              # 0.5 cup
            r'(\d+)\s*tablespoon',            # 2 tablespoons
            r'(\d+)\s*tbsp',                  # 2 tbsp
            r'(\d+)\s*teaspoon',              # 1 teaspoon
            r'(\d+)\s*tsp',                   # 1 tsp
        ]
        
        # First try to match standard patterns
        for pattern in patterns:
            match = re.search(pattern, food_description, re.IGNORECASE)
            if match:
                weight = float(match.group(1))
                
                # Convert to grams based on unit
                unit_lower = food_description.lower()
                
                if 'oz' in unit_lower or 'ounce' in unit_lower:
                    weight *= 28.35  # oz to grams
                elif 'lb' in unit_lower or 'pound' in unit_lower:
                    weight *= 453.6  # lb to grams
                elif 'kg' in unit_lower or 'kilogram' in unit_lower:
                    weight *= 1000  # kg to grams
                elif 'cân' in unit_lower:
                    weight *= 500  # Vietnamese cân to grams (approximately)
                elif 'lạng' in unit_lower:
                    weight *= 100  # Vietnamese lạng to grams
                elif 'chỉ' in unit_lower:
                    weight *= 3.75  # Vietnamese chỉ to grams
                elif 'cup' in unit_lower:
                    weight *= 240  # cup to grams (approximate for most foods)
                elif 'tablespoon' in unit_lower or 'tbsp' in unit_lower:
                    weight *= 15  # tablespoon to grams
                elif 'teaspoon' in unit_lower or 'tsp' in unit_lower:
                    weight *= 5  # teaspoon to grams
                elif 'slice' in unit_lower:
                    weight *= 30  # slice to grams (average for bread, cheese)
                elif 'piece' in unit_lower:
                    weight *= 50  # piece to grams (average for fruit, chicken)
                
                return weight
        
        # Try to extract from common portion descriptions
        portion_patterns = {
            'small': 100,
            'medium': 150,
            'large': 200,
            'extra large': 250,
            'regular': 150,
            'big': 180,
            'small bowl': 200,
            'medium bowl': 300,
            'large bowl': 400,
            'plate': 300,
            'serving': 150,
        }
        
        for portion, default_weight in portion_patterns.items():
            if portion in food_description.lower():
                return default_weight
        
        return None
    
    @classmethod
    def extract_food_name(cls, food_description: str) -> str:
        """Extract clean food name from description"""
        # Remove weight/quantity information
        food_description = re.sub(
            r'\d+[\.\d]*\s*(?:g|gram|oz|ounce|ml|lb|pound|kg|kilogram|cân|lạng|chỉ|slice|piece|cup|tbsp|tsp|tablespoon|teaspoon)s?',
            '', 
            food_description, 
            flags=re.IGNORECASE
        )
        
        # Remove common prepositions and articles
        remove_words = ['with', 'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'by']
        for word in remove_words:
            food_description = re.sub(r'\b' + word + r'\b', '', food_description, flags=re.IGNORECASE)
        
        # Remove portion size words
        portion_words = ['small', 'medium', 'large', 'extra large', 'regular', 'big', 'bowl', 'plate', 'serving']
        for word in portion_words:
            food_description = re.sub(r'\b' + word + r'\b', '', food_description, flags=re.IGNORECASE)
        
        # Clean up: remove extra spaces and punctuation
        food_description = re.sub(r'[^\w\s]', '', food_description)
        food_description = re.sub(r'\s+', ' ', food_description)
        
        return food_description.strip().lower()
    
    @classmethod
    def find_best_match(cls, food_name: str) -> Optional[str]:
        """Find the best matching food in database"""
        if not food_name:
            return None
            
        food_name = food_name.lower().strip()
        
        # 1. Direct match
        if food_name in cls.FOOD_DATABASE:
            return food_name
        
        # 2. Remove common adjectives and try again
        adjectives = ['grilled', 'fried', 'roasted', 'baked', 'steamed', 'boiled', 'raw', 'fresh', 'cooked']
        clean_name = food_name
        for adj in adjectives:
            clean_name = clean_name.replace(adj, '').strip()
        
        if clean_name in cls.FOOD_DATABASE and clean_name != food_name:
            return clean_name
        
        # 3. Partial match (database food in input or input in database food)
        for db_food in cls.FOOD_DATABASE:
            if db_food in food_name or food_name in db_food:
                return db_food
        
        # 4. Word match (any common word)
        food_words = set(food_name.split())
        best_match = None
        best_score = 0
        
        for db_food in cls.FOOD_DATABASE:
            db_words = set(db_food.split())
            common_words = food_words & db_words
            
            if common_words:
                score = len(common_words)
                # Bonus for longer matches
                if any(word in food_name for word in db_food.split()):
                    score += 1
                
                if score > best_score:
                    best_score = score
                    best_match = db_food
        
        return best_match
    
    @classmethod
    @lru_cache(maxsize=500)
    def predict_nutrients_cached(cls, food_description: str, quantity_g: Optional[float] = None) -> Dict:
        """Cached version of predict_nutrients for better performance"""
        return cls.predict_nutrients(food_description, quantity_g)
    
    @classmethod
    def predict_nutrients(cls, food_description: str, quantity_g: Optional[float] = None, category: str = None) -> Dict:
        """Predict nutrients for a food item with optional meal category context"""
        # Clean the food description
        clean_name = cls.extract_food_name(food_description)
        
        # Extract weight if not provided
        if quantity_g is None:
            quantity_g = cls.extract_weight(food_description)
            if quantity_g is None:
                quantity_g = 100  # Default to 100g
        
        # Find best match
        matched_food = cls.find_best_match(clean_name)
        
        if matched_food:
            # Use database values
            nutrients = cls.FOOD_DATABASE[matched_food].copy()
            
            # Scale by quantity
            scale = quantity_g / 100.0
            for key in nutrients:
                if isinstance(nutrients[key], (int, float)):
                    nutrients[key] = round(nutrients[key] * scale)
            
            # Adjust based on meal category if provided
            if category:
                nutrients = cls.adjust_by_category(nutrients, category)
            
            confidence = "high" if matched_food == clean_name else "medium"
            
            nutrients.update({
                "food_name": matched_food.title(),
                "original_name": food_description,
                "quantity_g": round(quantity_g),
                "confidence": confidence,
                "source": "food_database",
                "matched_food": matched_food
            })
        else:
            # AI-like estimation based on food type patterns
            nutrients = cls.estimate_nutrients(clean_name, quantity_g, category)
            nutrients.update({
                "food_name": clean_name.title() if clean_name else food_description.title(),
                "original_name": food_description,
                "quantity_g": round(quantity_g),
                "confidence": "low",
                "source": "ai_estimation",
                "matched_food": None
            })
        
        return nutrients
    
    @classmethod
    def adjust_by_category(cls, nutrients: Dict, category: str) -> Dict:
        """Adjust nutrient estimates based on meal category"""
        adjustments = {
            "Breakfast": {"calories_mult": 0.9, "protein_mult": 0.9},  # Typically lighter
            "Lunch": {"calories_mult": 1.0, "protein_mult": 1.0},      # Standard
            "Dinner": {"calories_mult": 1.1, "protein_mult": 1.1},     # Typically heavier
            "Snack": {"calories_mult": 0.7, "protein_mult": 0.8},      # Smaller portions
        }
        
        if category in adjustments:
            adj = adjustments[category]
            nutrients["calories"] = round(nutrients["calories"] * adj["calories_mult"])
            nutrients["protein"] = round(nutrients["protein"] * adj["protein_mult"])
        
        return nutrients
    
    @classmethod
    def estimate_nutrients(cls, food_name: str, quantity_g: float, category: str = None) -> Dict:
        """Estimate nutrients using pattern recognition"""
        food_name_lower = food_name.lower()
        
        # Initialize with average values
        base_calories = 150
        base_protein = 10
        base_fat = 5
        base_carbs = 20
        
        # Food type detection
        protein_keywords = [
            'chicken', 'beef', 'pork', 'fish', 'meat', 'steak', 'egg', 
            'tofu', 'protein', 'shrimp', 'crab', 'lobster', 'squid',
            'octopus', 'mussel', 'bacon', 'ham', 'sausage', 'turkey',
            'duck', 'lamb', 'venison', 'bison'
        ]
        
        carb_keywords = [
            'rice', 'pasta', 'bread', 'potato', 'noodle', 'cereal', 
            'oat', 'grain', 'quinoa', 'barley', 'wheat', 'corn',
            'tortilla', 'wrap', 'bagel', 'muffin', 'cake', 'cookie',
            'pastry', 'pie', 'pancake', 'waffle'
        ]
        
        fat_keywords = [
            'cheese', 'butter', 'oil', 'avocado', 'nut', 'seed', 'cream',
            'mayonnaise', 'dressing', 'sauce', 'gravy', 'fat', 'lard',
            'shortening', 'margarine', 'peanut', 'almond', 'cashew',
            'walnut', 'pecan', 'hazelnut', 'macadamia'
        ]
        
        veg_keywords = [
            'broccoli', 'spinach', 'lettuce', 'carrot', 'vegetable',
            'salad', 'cabbage', 'cauliflower', 'pepper', 'onion',
            'garlic', 'tomato', 'cucumber', 'celery', 'asparagus',
            'zucchini', 'eggplant', 'mushroom', 'squash', 'pea',
            'bean', 'corn', 'artichoke', 'brussel', 'kale', 'chard'
        ]
        
        fruit_keywords = [
            'apple', 'banana', 'orange', 'grape', 'strawberry',
            'blueberry', 'mango', 'pineapple', 'watermelon', 'melon',
            'peach', 'pear', 'plum', 'cherry', 'kiwi', 'lemon',
            'lime', 'grapefruit', 'pomegranate', 'raspberry',
            'blackberry', 'cranberry', 'apricot', 'fig', 'date'
        ]
        
        # Determine food type
        food_type = "mixed"
        
        if any(keyword in food_name_lower for keyword in protein_keywords):
            food_type = "protein"
            base_calories = 200
            base_protein = 25
            base_fat = 10
            base_carbs = 5
        elif any(keyword in food_name_lower for keyword in carb_keywords):
            food_type = "carb"
            base_calories = 130
            base_protein = 5
            base_fat = 2
            base_carbs = 30
        elif any(keyword in food_name_lower for keyword in fat_keywords):
            food_type = "fat"
            base_calories = 300
            base_protein = 10
            base_fat = 25
            base_carbs = 5
        elif any(keyword in food_name_lower for keyword in veg_keywords):
            food_type = "vegetable"
            base_calories = 50
            base_protein = 3
            base_fat = 1
            base_carbs = 10
        elif any(keyword in food_name_lower for keyword in fruit_keywords):
            food_type = "fruit"
            base_calories = 60
            base_protein = 1
            base_fat = 0.5
            base_carbs = 15
        
        # Adjust based on preparation method
        prep_adjustment = 1.0
        if 'fried' in food_name_lower or 'deep fried' in food_name_lower:
            prep_adjustment = 1.5  # Fried foods have more calories
            if food_type == "protein":
                base_fat *= 2
        elif 'grilled' in food_name_lower or 'roasted' in food_name_lower:
            prep_adjustment = 1.1  # Slightly higher due to oil
        elif 'steamed' in food_name_lower or 'boiled' in food_name_lower:
            prep_adjustment = 0.9  # Lower fat content
        
        # Add some randomness to make it feel AI-like (reduced range)
        variation = 0.9 + (random.random() * 0.2)  # 0.9 to 1.1
        
        scale = quantity_g / 100.0
        
        # Calculate final values
        calories = round(base_calories * scale * variation * prep_adjustment)
        protein = round(base_protein * scale * variation)
        fat = round(base_fat * scale * variation * prep_adjustment)
        carbs = round(base_carbs * scale * variation)
        
        # Adjust based on category if provided
        if category:
            if category == "Breakfast":
                calories = round(calories * 0.9)
                protein = round(protein * 0.9)
            elif category == "Dinner":
                calories = round(calories * 1.1)
                protein = round(protein * 1.1)
            elif category == "Snack":
                calories = round(calories * 0.7)
                protein = round(protein * 0.8)
        
        return {
            "calories": max(10, calories),  # Minimum 10 calories
            "protein": max(0, protein),
            "fat": max(0, fat),
            "carbs": max(0, carbs),
            "estimated_type": food_type
        }
    
    @classmethod
    def get_similar_foods(cls, food_name: str, limit: int = 5) -> List[Dict]:
        """Get similar foods for suggestions"""
        food_name_lower = food_name.lower()
        similar = []
        
        # Score foods based on similarity
        scored_foods = []
        for db_food, nutrients in cls.FOOD_DATABASE.items():
            score = 0
            
            # Exact match
            if food_name_lower == db_food:
                score += 100
            # Contains match
            elif food_name_lower in db_food or db_food in food_name_lower:
                score += 50
            # Word match
            else:
                food_words = set(food_name_lower.split())
                db_words = set(db_food.split())
                common_words = food_words & db_words
                if common_words:
                    score += len(common_words) * 10
            
            # Same food type bonus
            food_type = cls.estimate_nutrients(food_name_lower, 100).get("estimated_type", "mixed")
            db_food_type = cls.estimate_nutrients(db_food, 100).get("estimated_type", "mixed")
            if food_type == db_food_type:
                score += 5
            
            if score > 0:
                scored_foods.append((score, db_food, nutrients))
        
        # Sort by score and take top results
        scored_foods.sort(key=lambda x: x[0], reverse=True)
        
        for score, db_food, nutrients in scored_foods[:limit]:
            similar.append({
                "name": db_food.title(),
                "similarity_score": score,
                "calories_per_100g": nutrients["calories"],
                "protein_per_100g": nutrients["protein"],
                "fat_per_100g": nutrients["fat"],
                "carbs_per_100g": nutrients["carbs"]
            })
        
        return similar
    
    @classmethod
    def search_foods(cls, query: str, limit: int = 10) -> List[Dict]:
        """Search for foods in database with fuzzy matching"""
        query = query.lower().strip()
        results = []
        
        if len(query) < 2:
            return results
        
        for food_name, nutrients in cls.FOOD_DATABASE.items():
            if query in food_name:
                # Exact substring match
                score = 100 - food_name.find(query)  # Earlier match = higher score
                results.append({
                    "name": food_name.title(),
                    "score": score,
                    "calories": nutrients["calories"],
                    "protein": nutrients["protein"],
                    "fat": nutrients["fat"],
                    "carbs": nutrients["carbs"]
                })
            elif any(word in food_name for word in query.split()):
                # Word match
                score = 50
                results.append({
                    "name": food_name.title(),
                    "score": score,
                    "calories": nutrients["calories"],
                    "protein": nutrients["protein"],
                    "fat": nutrients["fat"],
                    "carbs": nutrients["carbs"]
                })
        
        # Sort by score and return limited results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    @classmethod
    def get_database_stats(cls) -> Dict:
        """Get statistics about the food database"""
        total_foods = len(cls.FOOD_DATABASE)
        
        # Count by category
        categories = {}
        for food_name in cls.FOOD_DATABASE:
            # Simple category detection
            food_type = cls.estimate_nutrients(food_name, 100).get("estimated_type", "mixed")
            categories[food_type] = categories.get(food_type, 0) + 1
        
        # Average nutrient values
        avg_calories = sum(n["calories"] for n in cls.FOOD_DATABASE.values()) / total_foods
        avg_protein = sum(n["protein"] for n in cls.FOOD_DATABASE.values()) / total_foods
        
        return {
            "total_foods": total_foods,
            "categories": categories,
            "avg_calories_per_100g": round(avg_calories, 1),
            "avg_protein_per_100g": round(avg_protein, 1),
            "last_updated": "2024-01-15"
        }

# Singleton instance
predictor = NutrientPredictor()