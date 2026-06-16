from pyspark.sql import DataFrame

def split_data(data: DataFrame, train_size: float = 0.8, test_size:float = 0.2) -> tuple[DataFrame, DataFrame]:
    """
    Splits the data into training and testing sets.

    Args:
        data (DataFrame): The input data to be split.
        train_size (float): The proportion of the dataset to include in the training set. Default is 0.8.
        test_size (float): The proportion of the dataset to include in the testing set. Default is 0.2.
    Returns:
        tuple[DataFrame, DataFrame]: The training and testing sets.
    """
    train, test = data.randomSplit([train_size, test_size], seed=123)
    
    return train, test