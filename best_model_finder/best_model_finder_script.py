import numpy as np
import xgboost as xgb
import optuna
import config
from sklearn.model_selection import train_test_split
from pipelines.custom_pipelines import CustomPipeline
from data_preprocessing.data_preprocessing_script import DataPreprocessing
from sklearn.metrics import mean_squared_error
import joblib
import os
from mail_automation.mail import SendMail


class ModelFinder:

    def __init__(self):
        """
        This class is used to find the best hyperparameters for the machine learning model.
        """
        self.scaler_path = os.path.join("models", "scaler.pkl")
        self.model_path = os.path.join("models", "xgboost_model.pkl")

    def fit(self, X, y, email):
        """

        :param X: feature variable
        :param y: labels/values
        :param email: email for notifying
        :return: status of the job
        """
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            study = optuna.create_study(direction='maximize')
            study.optimize(lambda trial: objective(trial, X_train, X_test, y_train, y_test), n_trials=20)
            best_params = study.best_params
            n_neighbors = best_params['n_neighbors']
            preprocessing = DataPreprocessing(n_neighbors)
            preprocessing.fit_data(X_train)
            X_train_tf = preprocessing.transform_data(X_train)
            X_test_tf = preprocessing.transform_data(X_test)
            config.logger.log("INFO", "Best Params : " + str(best_params))
            best_params.pop('n_neighbors')
            xgb_reg = xgb.XGBRegressor(**best_params)
            xgb_reg.fit(X_train_tf, y_train)
            config.logger.log("INFO", "Data Fitted")
            train_pred = xgb_reg.predict(X_train_tf)
            test_pred = xgb_reg.predict(X_test_tf)
            training_rmse = np.sqrt(mean_squared_error(train_pred, y_train))
            testing_rmse = np.sqrt(mean_squared_error(test_pred, y_test))
            training_score = xgb_reg.score(X_train_tf, y_train)
            testing_score = xgb_reg.score(X_test_tf, y_test)
            config.logger.log("INFO", "Training RMSE : " + str(training_rmse))
            config.logger.log("INFO", "Testing RMSE : " + str(testing_rmse))
            config.logger.log("INFO", "Training Score : " + str(training_score))
            config.logger.log("INFO", "Testing RMSE : " + str(testing_score))
            joblib.dump(xgb_reg, self.model_path)
            joblib.dump(preprocessing, self.scaler_path)
            config.logger.log("INFO", "Model saved")
            SendMail("Training is completed", email).send()
            return {"status": "Success"}
        except Exception as e:
            SendMail("Training failed",email).send()
            config.logger.log("ERROR", str(e))
            return {"status": "Failure"}

    def predict(self, X):
        """

        :param X: feature variable
        :return: prediction result
        """
        try:
            if os.path.exists(self.scaler_path):
                preprocessing = joblib.load(self.scaler_path)
                X_tf = preprocessing.transform_data(X)
                if os.path.exists(self.model_path):
                    model = joblib.load(self.model_path)
                    pred = model.predict(X_tf)
                    config.logger.log("INFO", "Prediction Successful")
                    return {"status": "Success", "pred": pred}
                else:
                    config.logger.log("ERROR", "Model Not Found")
                    return {"status": "Failure", "pred": None}
            else:
                config.logger.log("ERROR", "Scaler not found")
                return {"status": "Failure", "pred": None}
        except Exception as e:
            config.logger.log("ERROR", str(e))
            return {"status": "Failure", "pred": None}


def objective(trial, X_train, X_test, y_train, y_test):
    knn_param = {
        "n_neighbors": trial.suggest_int("n_neighbors", 3, 30)
    }
    pipeline = CustomPipeline().total_pipeline(**knn_param)
    X_train_tf = pipeline.fit_transform(X_train)
    X_test_tf = pipeline.transform(X_test)

    param = {
        # "tree_method": "gpu_hist",
        # "gpu_id": 1,
        "lambda": trial.suggest_loguniform("lambda", 1e-4, 10.0),
        "alpha": trial.suggest_loguniform("alpha", 1e-4, 10.0),
        "colsample_bytree": trial.suggest_categorical("colsample_bytree", [.3, .4, .5, .6, .7, .8, .9, 1.0]),
        "subsample": trial.suggest_categorical("subsample", [.08, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]),
        "learning_rate": trial.suggest_categorical("learning_rate", [.00001, .0003, 0.008, 0.02, 0.01, 1, 10, 20]),
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "max_depth": trial.suggest_categorical("max_depth", [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
        "random_state": trial.suggest_categorical("random_state", [10, 20, 30, 70, 300, 231232]),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 100),
        "verbosity": 3
    }
    xgb_reg = xgb.XGBRegressor(**param)
    try:
        xgb_reg.fit(X_train_tf, y_train, eval_set=[(X_test_tf, y_test)], verbose=True)
        return xgb_reg.score(X_test_tf, y_test)
    except:
        return 0
