# 🍽️ Calorie & Protein Tracker (CLI)

A Python command-line application for tracking daily meals, calories, and protein intake.  
The app provides daily and weekly summaries and checks whether the user meets a **personalized protein goal based on body weight**.

This project was built as a portfolio project to demonstrate fundamental computer science skills such as data handling, control flow, and clean program structure.

---

## 🚀 Features

- Add meals with:
  - Food name
  - Calories
  - Protein (grams)
  - Category (Breakfast, Lunch, Dinner, Snack)
- View **today’s calorie and protein summary**
- View **last 7 days summary** in a table format
- **Edit or delete meals** from any date
- **Personalized protein goal tracking**
  - Daily protein goal = **2 × body weight (kg)**
  - Visual feedback:
    - ✅ Goal met
    - ⚠️ Goal not met
- Data stored locally using JSON

---

## 🧠 Protein Goal Logic

The application calculates the daily protein goal using the formula:

Protein Goal (g) = 2 × Body Weight (kg)

This project helped me practice:

File I/O with JSON

Data aggregation and filtering

Command-line user interaction

Input validation and error handling

Writing clean, maintainable Python code

🔮 Future Improvements

Allow users to input body weight dynamically

Show weekly average protein intake

Export data to CSV

Build a web version using Flask