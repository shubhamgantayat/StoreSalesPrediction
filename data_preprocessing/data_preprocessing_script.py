import config
from pipelines.custom_pipelines import CustomPipeline


class DataPreprocessing:

    def __init__(self, n_neighbors):
        self.pipeline = CustomPipeline().total_pipeline(n_neighbors)

    def transform_data(self, X):
        config.logger.log("INFO", "Transforming data")
        X_tf = self.pipeline.transform(X)
        return X_tf

    def fit_data(self, X):
        config.logger.log("INFO", "Fitting data")
        self.pipeline.fit(X)

