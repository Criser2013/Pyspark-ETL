from constants import NUMS, BOOLEANS
from pandas import DataFrame, Series
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score, roc_auc_score

def create_model():
    """
    Creates and returns an untrained ML pipeline for TEP prediction.

    Returns:
        Pipeline: An untrained ML pipeline with imputation and a classifier.
    """
    BOOL = BOOLEANS + ["Género", "Otra Enfermedad"]
    MODEL = MLPClassifier(hidden_layer_sizes=(44,44,43,44), solver="adam", activation="tanh", random_state=123)

    IMPUTER_TRANSFORMER = ColumnTransformer(transformers=[
        ("num", SimpleImputer(strategy="most_frequent"), NUMS),
        ("bool", SimpleImputer(strategy="most_frequent"), BOOL),
    ])

    PIPELINE = Pipeline(steps=[
        ("imputer", IMPUTER_TRANSFORMER),
        ("model", MODEL)
    ])

    return PIPELINE


def train_model(pipeline: Pipeline, X_train: DataFrame, y_train: Series) -> Pipeline:
    """
    Trains the given ML pipeline on the provided training data.

    Args:
        pipeline (Pipeline): The ML pipeline to be trained.
        X_train (DataFrame): The training features.
        y_train (Series): The training labels.

    Returns:
        Pipeline: The trained ML pipeline.
    """
    pipeline.fit(X_train, y_train)
    return pipeline


def evaluate_model(pipeline: Pipeline, X_test: DataFrame, y_test: Series) -> dict:
    """
    Evaluates the trained model on the test set and returns a dictionary of metrics.

    Args:
        pipeline (Pipeline): The trained ML pipeline.
        X_test (DataFrame): The test features.
        y_test (Series): The true labels for the test set.

    Returns:
        dict: A dictionary containing the evaluation metrics.
    """
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:,1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba)
    }

    return metrics