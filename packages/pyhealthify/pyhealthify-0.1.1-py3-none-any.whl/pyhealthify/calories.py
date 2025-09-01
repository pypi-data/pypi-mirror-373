def daily_calories(weight: float, height: float, age: int, gender: str, activity_level: str) -> float:
    """
    Calculate daily calorie needs using Mifflin-St Jeor Equation.
    
    :param weight: Weight in kg
    :param height: Height in cm
    :param age: Age in years
    :param gender: "male" or "female"
    :param activity_level: "sedentary", "light", "moderate", "active", "very active"
    :return: Daily calorie needs
    """
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif gender.lower() == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        raise ValueError("Gender must be 'male' or 'female'")

    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very active": 1.9
    }

    factor = activity_factors.get(activity_level.lower())
    if not factor:
        raise ValueError("Invalid activity level")

    return round(bmr * factor, 2)


def macro_breakdown(calories: float) -> dict:
    """
    Suggest protein, carbs, and fats breakdown.
    Ratios: 30% protein, 50% carbs, 20% fats.
    """
    return {
        "protein_g": round((0.3 * calories) / 4, 1),  # 1g protein = 4 kcal
        "carbs_g": round((0.5 * calories) / 4, 1),
        "fats_g": round((0.2 * calories) / 9, 1)
    }
