from pyspark.sql.functions import when
from pyspark.sql import Column
from unicodedata import normalize, category


def eval_interval(col: Column, intervals: tuple) -> Column:
    """
    Evaluates a numeric value and assigns it to an interval based on the provided intervals.

    Args:
        col (Column): The numeric value to evaluate.
        intervals (tuple): A tuple of tuples, where each inner tuple represents an
        interval in the form (lower_bound, upper_bound, assigned_value).

    Returns:
        Column: The assigned value for the interval to which the numeric value belongs.
    """
    expr = None

    for lower, upper, assigned_value in intervals:

        if lower != float("-inf") and upper != float("inf"):
            cond = (col >= lower) & (col < upper)

        elif lower != float("-inf"):
            cond = col >= lower

        else:
            cond = col < upper

        expr = (
            when(cond, assigned_value)
            if expr is None
            else expr.when(cond, assigned_value)
        )

    return expr.otherwise(-1)


def remove_accents(texto: str) -> str:
    nfkd = normalize("NFKD", texto)
    return "".join([c for c in nfkd if category(c) != "Mn"])
