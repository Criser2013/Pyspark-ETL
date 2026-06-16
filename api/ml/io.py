from pyspark.ml import Pipeline, PipelineModel

def save_pipeline(pipeline: Pipeline, path: str):
    """
    Save a trained pipeline to a file.

    Args:
        pipeline (Pipeline): The trained machine learning pipeline to be saved.
        path (str): The file path where the pipeline will be saved.
    """
    pipeline.save(path)

def load_untrained_pipeline(path: str) -> Pipeline:
    """
    Load an untrained pipeline from a file.

    Args:
        path (str): The file path from which the pipeline will be loaded.

    Returns:
        Pipeline: The loaded machine learning pipeline.
    """
    return Pipeline.load(path)

def load_trained_pipeline(path: str) -> PipelineModel:
    """
    Load a trained pipeline from a file.

    Args:
        path (str): The file path from which the trained pipeline will be loaded.

    Returns:
        PipelineModel: The loaded trained machine learning pipeline.
    """
    return PipelineModel.load(path)