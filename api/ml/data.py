from pandas import DataFrame
from sklearn.model_selection import train_test_split

def split_data(data: DataFrame, train_size: float = 0.8, test_size:float = 0.2):
    """
    Splits the data into training and testing sets.

    Args:
        data (DataFrame): The input data to be split.
        train_size (float): The proportion of the dataset to include in the training set. Default is 0.8.
        test_size (float): The proportion of the dataset to include in the testing set. Default is 0.2.
    Returns:
        tuple[DataFrame, DataFrame]: The training and testing sets.
    """
    train, test = train_test_split(
        data, train_size=train_size, test_size=test_size, random_state=123, shuffle=True
        )
    
    return train, test