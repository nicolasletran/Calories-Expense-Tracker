# Calories-Expense-Tracker
A Tracker to Track Your Daily Calories Intake
# Calorie & Expense Tracker (CLI)

A simple Python command-line application to track daily calorie and protein intake. This project demonstrates file handling, date manipulation, and basic user interaction in Python.

---

## Features
- Add meal entries with:
  - Food name
  - Calories
  - Protein (grams)
- View total calories and protein **for today**
- View total calories and protein **for the last 7 days**
- Data persists in a JSON file (`data.json`) between sessions

---

## Tech Stack
- Python 3
- JSON for data storage
- Standard Python libraries (`datetime`, `json`)

---

## How to Run
1. Clone this repository:
```bash
git clone https://github.com/nicolasletran/Calories-Expense-Tracker.git
cd Calories-Expense-Tracker
```
Run the tracker: 
```bash
python tracker.py
```
Project Structure: 
calorie-expense-tracker-cli/
├── tracker.py       # Main Python script
├── data.json        # Stores all meal entries
└── README.md        # Project documentation

What I Learned:

How to read/write JSON files in Python

Using datetime for daily and weekly summaries

Designing a small CLI application with menus and user input

Structuring a project for readability and maintainability

Future Improvements

Add visualization of weekly calories/protein using matplotlib

Allow editing and deleting meal entries

Create a web version using Flask for a graphical interface

Support multiple users with separate data files