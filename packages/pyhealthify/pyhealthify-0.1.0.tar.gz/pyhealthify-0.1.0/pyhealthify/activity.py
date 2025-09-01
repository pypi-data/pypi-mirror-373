def steps_to_calories(steps: int, weight: float = 70) -> float:
    """
    Estimate calories burned from steps.
    Approx: 0.04 - 0.05 kcal per step for avg 70kg person.
    
    :param steps: Number of steps
    :param weight: Weight in kg (default 70)
    :return: Estimated calories burned
    """
    if steps < 0:
        raise ValueError("Steps cannot be negative")

    # Adjust calorie per step by weight (basic scaling)
    kcal_per_step = 0.04 + ((weight - 70) * 0.0002)
    return round(steps * kcal_per_step, 2)
