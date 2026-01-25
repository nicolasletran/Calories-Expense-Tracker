import json
from datetime import date, timedelta
from tabulate import tabulate
DATA_FILE = "data.json"
BODY_WEIGHT = 70  # kg
PROTEIN_GOAL = BODY_WEIGHT * 2


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def show_menu():
    print("\n" + "="*30)
    print("   Calorie & Expense Tracker   ")
    print("="*30)
    print("1. Add meal")
    print("2. View today's summary")
    print("3. View last 7 days")
    print("4. Edit or delete a meal")   # new
    print("5. Exit")


    
def add_meal():
    data = load_data()  # load existing entries

    print("\nEnter meal details:")
    food = input("Food name: ")
    calories = int(input("Calories: "))
    protein = int(input("Protein (g): "))

    # New: category
    print("Select category:")
    print("1. Breakfast")
    print("2. Lunch")
    print("3. Dinner")
    print("4. Snack")
    category_choice = input("Choose 1-4: ")
    categories = {"1": "Breakfast", "2": "Lunch", "3": "Dinner", "4": "Snack"}
    category = categories.get(category_choice, "Other")

    entry = {
        "date": str(date.today()),
        "food": food,
        "calories": calories,
        "protein": protein,
        "category": category
    }

    data["entries"].append(entry)
    save_data(data)

    print(f"✅ Meal added successfully under '{category}'.")


def view_today():
    data = load_data()
    today = str(date.today())

    total_cal = 0
    total_protein = 0
    category_totals = {}

    for entry in data["entries"]:
        if entry["date"] == today:
            total_cal += entry["calories"]
            total_protein += entry["protein"]
            cat = entry.get("category", "Other")
            category_totals[cat] = category_totals.get(cat, 0) + entry["calories"]

    print("\nToday's Total:")
    print(f"Calories: {total_cal}")
    print(f"Protein: {total_protein} g")
    print("\nCalories by category:")
    for cat, cal in category_totals.items():
        print(f"{cat}: {cal}")

    # ✅ Check protein goal
    if total_protein >= PROTEIN_GOAL:
        print(f"\n🎉 You reached your protein goal today! ({total_protein}/{PROTEIN_GOAL} g)")
    else:
        print(f"\n⚠️ You are below your protein goal today: {total_protein}/{PROTEIN_GOAL} g")


def view_last_7_days():
    data = load_data()
    today = date.today()
    start_date = today - timedelta(days=6)

    summary = {}

    for entry in data["entries"]:
        entry_date = date.fromisoformat(entry["date"])
        if start_date <= entry_date <= today:
            d = entry_date.isoformat()
            if d not in summary:
                summary[d] = {"calories": 0, "protein": 0}
            summary[d]["calories"] += entry["calories"]
            summary[d]["protein"] += entry["protein"]

    # Build table
    table = []
    for d, totals in sorted(summary.items()):
        # Add check for protein goal
        status = "✅" if totals["protein"] >= PROTEIN_GOAL else "⚠️"

        table.append([d, totals["calories"], totals["protein"], status])

    print("\nLast 7 Days Summary:")
    print(tabulate(
    table,
    headers=["Date", "Calories", "Protein (g)", "Goal (2x BW)"],
    tablefmt="grid"
))

def edit_or_delete_meal():
    data = load_data()
    
    # Step 1: Ask for the date
    date_input = input("Enter the date of the meal (YYYY-MM-DD) or leave blank for today: ")
    if date_input.strip() == "":
        target_date = str(date.today())
    else:
        try:
            target_date = str(date.fromisoformat(date_input))
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return

    # Step 2: Filter meals by that date
    meals_on_date = [entry for entry in data["entries"] if entry["date"] == target_date]

    if not meals_on_date:
        print(f"\nNo meals found for {target_date}.")
        return

    # Step 3: Show meals on that date
    print(f"\nMeals on {target_date}:")
    for i, meal in enumerate(meals_on_date, start=1):
        print(f"{i}. {meal['food']} - {meal['calories']} cal, {meal['protein']}g, {meal.get('category', 'Other')}")

    # Step 4: Choose a meal
    choice = input("\nEnter the number of the meal to edit/delete: ")

    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(meals_on_date):
        print("Invalid choice.")
        return

    index = int(choice) - 1
    meal = meals_on_date[index]

    # Step 5: Ask for action
    action = input("Type 'e' to edit or 'd' to delete: ").lower()

    if action == 'd':
        data["entries"].remove(meal)
        save_data(data)
        print("✅ Meal deleted successfully.")

    elif action == 'e':
        # Step 6: Edit meal details
        print("\nLeave blank to keep current value.")
        new_food = input(f"Food name [{meal['food']}]: ") or meal['food']
        new_calories = input(f"Calories [{meal['calories']}]: ")
        new_protein = input(f"Protein (g) [{meal['protein']}]: ")
        print("Select category:")
        print("1. Breakfast  2. Lunch  3. Dinner  4. Snack")
        new_category_choice = input(f"Category [{meal.get('category', 'Other')}]: ")

        meal['food'] = new_food
        meal['calories'] = int(new_calories) if new_calories else meal['calories']
        meal['protein'] = int(new_protein) if new_protein else meal['protein']

        categories = {"1": "Breakfast", "2": "Lunch", "3": "Dinner", "4": "Snack"}
        meal['category'] = categories.get(new_category_choice, meal.get('category', 'Other'))

        save_data(data)
        print("✅ Meal updated successfully.")

    else:
        print("Invalid action.")

def fix_missing_categories():
    data = load_data()
    updated = False
    for entry in data["entries"]:
        if "category" not in entry:
            entry["category"] = "Other"
            updated = True
    if updated:
        save_data(data)


def main():
    fix_missing_categories()
    while True:
        show_menu()
        choice = input("Choose an option: ")

        if choice == "1":
            add_meal()
        elif choice == "2":
            view_today() # placeholder
        elif choice == "3":
            view_last_7_days()  # placeholder
        elif choice == "4":
            edit_or_delete_meal()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
