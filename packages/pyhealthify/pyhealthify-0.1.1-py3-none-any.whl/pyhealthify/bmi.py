def calculate(weight: float, height: float) -> float:
    """
    Calculate Body Mass Index (BMI).
    
    :param weight: Weight in kilograms
    :param height: Height in meters
    :return: BMI value
    """
    if height <= 0:
        raise ValueError("Height must be greater than zero")
    return round(weight / (height ** 2), 2)


def category(bmi: float) -> str:
    """
    Return BMI category based on WHO standards.
    """
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"
