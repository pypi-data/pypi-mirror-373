def daily_water_intake(weight: float) -> float:
    """
    Suggest daily water intake (liters) based on weight.
    General rule: 35 ml per kg.
    
    :param weight: Weight in kg
    :return: Water intake in liters
    """
    if weight <= 0:
        raise ValueError("Weight must be positive")
    return round((weight * 35) / 1000, 2)
