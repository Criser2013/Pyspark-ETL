from pickle import dump, load
from skl2onnx import to_onnx
from pandas import DataFrame
from sklearn.pipeline import Pipeline

def save_pipeline(pipeline: Pipeline, path: str):
    """
    Save a trained pipeline to a file.

    Args:
        pipeline (Pipeline): The trained machine learning pipeline to be saved.
        path (str): The file path where the pipeline will be saved.
    """
    with open(path, "wb") as f:
        dump(pipeline, f)

def load_pipeline(path: str) -> Pipeline:
    """
    Load a Pickle file containing a trained pipeline.

    Args:
        path (str): The file path from which the pipeline will be loaded.

    Returns:
        Pipeline: The loaded machine learning pipeline.
    """
    with open(path, "rb") as f:
        pipeline = load(f)
    
    return pipeline

def export_model_to_onnx(pipeline: Pipeline, X_sample: DataFrame, path: str):
    """
    Export a trained pipeline to ONNX format.

    Args:
        pipeline (Pipeline): The trained machine learning pipeline to be exported.
        X_sample (DataFrame): A sample of the input data for shape inference.
        path (str): The file path where the ONNX model will be saved.
    """
    onnx_model = to_onnx(pipeline, X_sample.astype("float32"), target_opset=12)
    with open(path, "wb") as f:
        f.write(onnx_model.SerializeToString())