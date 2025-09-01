# 🏥 PyHealthify

[![PyPI version](https://img.shields.io/pypi/v/pyhealthify?color=blue)](https://pypi.org/project/pyhealthify/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/pyhealthify.svg)](https://pypi.org/project/pyhealthify/)

A simple Python package for **health, fitness, and nutrition calculations**.  
Calculate **BMI, daily calorie needs, macros, steps-to-calories, and hydration requirements** easily.  

---

## ✨ Features
- 📊 **BMI Calculator** – with WHO categories  
- 🔥 **Daily Calorie Needs** – using Mifflin-St Jeor equation  
- 🍽️ **Macro Breakdown** – protein, carbs, fats split  
- 🚶 **Steps → Calories** – estimate calories burned from steps  
- 💧 **Hydration Needs** – suggest daily water intake  

---

## 📦 Installation
Install directly from PyPI:

```bash
pip install pyhealthify
## Usage

from pyhealthify import bmi, calories, activity, hydration

### BMI
my_bmi = bmi.calculate(70, 1.75)
print("BMI:", my_bmi, "-", bmi.category(my_bmi))

### Daily Calories
cals = calories.daily_calories(70, 175, 25, "male", "moderate")
print("Calories Needed:", cals)
print("Macro Split:", calories.macro_breakdown(cals))

### Activity
print("Calories Burned (10000 steps):", activity.steps_to_calories(10000, 70))

### Hydration
print("Water Intake (L):", hydration.daily_water_intake(70))
