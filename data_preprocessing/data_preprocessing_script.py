import config
from pipelines.custom_pipelines import CustomPipeline


class DataPreprocessing:

    def __init__(self, n_neighbors):
        """
        This function is used to preprocess batch data.
        :param n_neighbors: number of neighbors for the knn imputer
        """
        self.pipeline = CustomPipeline().total_pipeline(n_neighbors)

    def transform_data(self, X):
        """

        :param X: Transforms the feature variable.
        :return: Returns the transformed variable.
        """
        config.logger.log("INFO", "Transforming data")
        X_tf = self.pipeline.transform(X)
        return X_tf

    def fit_data(self, X):
        """

        :param X: Fits the feature variable to pipeline.
        :return: None
        """
        config.logger.log("INFO", "Fitting data")
        self.pipeline.fit(X)

