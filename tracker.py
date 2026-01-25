import json
from datetime import date, timedelta

DATA_FILE = "data.json"

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
    print("4. Exit")

    
def add_meal():
    data = load_data()  # load existing entries

    food = input("Food name: ")
    calories = int(input("Calories: "))
    protein = int(input("Protein (g): "))

    entry = {
        "date": str(date.today()),  # today’s date
        "food": food,
        "calories": calories,
        "protein": protein
    }

    data["entries"].append(entry)
    save_data(data)  # save back to file

    print("Meal added successfully.")

def view_today():
    data = load_data()
    today = str(date.today())

    total_cal = 0
    total_protein = 0

    for entry in data["entries"]:
        if entry["date"] == today:
            total_cal += entry["calories"]
            total_protein += entry["protein"]

    print("\nToday's Total:")
    print(f"Calories: {total_cal}")
    print(f"Protein: {total_protein} g")

def view_last_7_days():
    data = load_data()
    today = date.today()
    start_date = today - timedelta(days=6)  # last 7 days including today

    total_cal = 0
    total_protein = 0

    for entry in data["entries"]:
        entry_date = date.fromisoformat(entry["date"])
        if start_date <= entry_date <= today:
            total_cal += entry["calories"]
            total_protein += entry["protein"]

    print("\nLast 7 Days Total:")
    print(f"Calories: {total_cal}")
    print(f"Protein: {total_protein} g")


def main():
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
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
