from constants import NUMS_CLEANED, BOOLEANS_CLEANED
from pyspark.sql import DataFrame
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator

def create_model() -> Pipeline:
    """
    Creates and returns an untrained ML pipeline for TEP prediction.

    Returns:
        Pipeline: An untrained ML pipeline with imputation and a classifier.
    """
    BOOL = BOOLEANS_CLEANED.copy() + ["Otra_Enfermedad", "Cirugia_reciente", "Fiebre", "Genero"]
    NUMS = NUMS_CLEANED.copy() + ["Edad"]
    MODEL = MultilayerPerceptronClassifier(layers=[45, 44, 43, 44, 2], solver="l-bfgs", seed=123, labelCol="TEP")

    ASSEMBLER_NUM = VectorAssembler(inputCols=NUMS, outputCol="num_features", handleInvalid="skip")
    SCALER = StandardScaler(inputCol="num_features", outputCol="scaled_num_features", withMean=True, withStd=True)
    ASSEMBLER_BOOL = VectorAssembler(inputCols=BOOL, outputCol="bool_features", handleInvalid="skip")

    FINAL_ASSEMBLER = VectorAssembler(inputCols=["scaled_num_features", "bool_features"], outputCol="features")

    PIPELINE = Pipeline(stages=[ASSEMBLER_NUM, SCALER, ASSEMBLER_BOOL, FINAL_ASSEMBLER, MODEL])

    return PIPELINE


def train_model(pipeline: Pipeline, train_data: DataFrame) -> PipelineModel:
    """
    Trains the given ML pipeline on the provided training data.

    Args:
        pipeline (Pipeline): The ML pipeline to be trained.
        train_data (DataFrame): The training data.

    Returns:
        Pipeline: The trained ML pipeline.
    """
    return pipeline.fit(train_data)


def evaluate_model(pipeline: PipelineModel, test_data: DataFrame) -> dict:
    """
    Evaluates the trained model on the test set and returns a dictionary of metrics.

    Args:
        pipeline (PipelineModel): The trained ML pipeline.
        test_data (DataFrame): The test data.

    Returns:
        dict: A dictionary containing the evaluation metrics.
    """
    PREDS = pipeline.transform(test_data)
    
    AUC_ROC = BinaryClassificationEvaluator(labelCol="TEP", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
    ACCURACY = MulticlassClassificationEvaluator(labelCol="TEP", predictionCol="prediction", metricName="accuracy")
    F1 = MulticlassClassificationEvaluator(labelCol="TEP", predictionCol="prediction", metricName="f1")
    RECALL = MulticlassClassificationEvaluator(labelCol="TEP", predictionCol="prediction", metricName="recallByLabel")
    PRECISION = MulticlassClassificationEvaluator(labelCol="TEP", predictionCol="prediction", metricName="precisionByLabel")
    

    metrics = {
        "accuracy": ACCURACY.evaluate(PREDS),
        "f1_score": F1.evaluate(PREDS),
        "recall": RECALL.evaluate(PREDS),
        "precision": PRECISION.evaluate(PREDS),
        "roc_auc": AUC_ROC.evaluate(PREDS)
    }

    return metrics