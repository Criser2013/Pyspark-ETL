def eval_interval(val:int|float, intervals: tuple[tuple]) -> int:
    """
    Evaluates a numeric value and assigns it to an interval based on the provided intervals.

    Args:
        val (int|float): The numeric value to evaluate.
        intervals (tuple[tuple]): A tuple of tuples, where each inner tuple represents an interval in the form (lower_bound, upper_bound, assigned_value).

    Returns:
        int: The assigned value for the interval to which the numeric value belongs.
    """
    inf = float("inf")
    for lower, upper, assigned_value in intervals:
        if (lower != -inf) and (upper != inf):
            if (val >= lower) and (val < upper):
                return assigned_value
        elif (lower != -inf) and (upper == inf):
            if (val >= lower):
                return assigned_value
        elif (lower == -inf) and (upper != inf):
            if (val < upper):
                return assigned_value
    return -1

def proc_boolean(data: str) -> int|float:
    """
    Transforms a string representing a boolean value into an integer (1 or 0). Treats common placeholders as NA.

    Args:
        data (str): The string to transform.
    
    Returns:
        int|float: 1 for true values, 0 for false values.
    """
    if isinstance(data, float) and (data not in (1.0, 0.0)):  # Check for NaN
        return float("nan")
    
    data = data.lower()
    if data in ("1", "0"):
        return int(data)
    elif data in ("ni", "no", "n"):
        return 0
    else:
        return 1
    
def proc_other_diseases(data: dict, diseases: list) -> dict:
    """
    Transforms the "Otra Enfermedad" column based on the presence of other diseases. 
    If any of the specified diseases is present (value of 1), "Otra Enfermedad" is set to 1, otherwise it is set to 0.

    Args:
        data (dict): A dictionary containing the values of the "Otra Enfermedad" column and the specified diseases.
        diseases (list): A list of disease column names to check for presence.

    Returns:
        dict: The updated dictionary with the "Otra Enfermedad" column transformed.
    """
    for i in diseases:
        if data[i] == 1:
            data["Otra Enfermedad"] = 1
            return data

    data["Otra Enfermedad"] = 0

    return data