import pandas as pd
from flask import Flask, request, render_template, send_file
import os
import flask_monitoringdashboard as dashboard
from flask_cors import CORS, cross_origin
from mongo_db.crud import Operations
from logger.log_db import Logger
import config
from training_data_ingestion.data_ingestion_script import TrainingDataIngestion
from training_data_validation.data_validation_script import TrainingDataValidation
from training_db_upload.db_upload_script import TrainingDBUpload
from fetch_from_db.fetch_from_db_script import DBFetch
from best_model_finder.best_model_finder_script import ModelFinder
from threading import Thread
from dotenv import load_dotenv
from prediction_data_ingestion.data_ingestion_script import PredictionDataIngestion
from prediction_data_validation.data_validation_script import PredictionDataValidation
from prediction_db_upload.db_upload_script import PredictionDBUpload
import datetime
import string
import random
from file_deleter.file_deleter_script import FileDeleter

app = Flask(__name__)
dashboard.bind(app)
CORS(app)
config.logger = Logger()
config.mongo_db = Operations("StoreSalesPrediction", config.logger)


@app.route('/', methods=['GET'])
@cross_origin()
def home():
    return render_template("home_page.html")


@app.route('/train-data', methods=['GET'])
@cross_origin()
def render_train_page():
    return render_template('train_data.html')


@app.route('/train', methods=['GET', 'POST'])
@cross_origin()
def train():
    try:
        if request.method == 'POST':
            config.logger.log("INFO", "Data training initiated...")
            file = request.files['file']
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            load_dotenv("env/admin_credentials.env")
            if username != os.getenv("ADMINUSERNAME") or password != os.getenv("ADMINPASSWORD"):
                return render_template("train_data.html", results="Wrong admin username and password")
            ingestion_response = TrainingDataIngestion(file).save_raw_data()
            if ingestion_response['status'] == 'Success':
                validation_response = TrainingDataValidation(ingestion_response['filename']).check_columns()
                if validation_response['status'] == 'Success':
                    upload_response = TrainingDBUpload(validation_response['filename'], 'valid').upload_to_db()
                    if upload_response['status'] == 'Success':
                        fetch_response = DBFetch(upload_response['table_name']).fetch_data_from_db()
                        if fetch_response['status'] == 'Success':
                            train_data = fetch_response['data']
                            X = train_data.drop(columns=['Item_Outlet_Sales'])
                            y = train_data['Item_Outlet_Sales']
                            model_finder = ModelFinder()
                            Thread(target=model_finder.fit, args=(X, y, email)).start()
                            return render_template("train_data.html", results="We will notify you when your model is trained.")
                elif validation_response['status'] == 'Failure' and validation_response['filename'] is not None:
                    upload_response = TrainingDBUpload(validation_response['filename'], 'invalid').upload_to_db()
                else:
                    config.logger.log("ERROR", "Internal Error Occured")
        return render_template("train_data.html", results="Training Unuccessful. Invalid Data")
    except Exception as e:
        config.logger.log("ERROR", str(e))
        return render_template("train_data.html", results="Training Unuccessful. Some Internal Error Occured")


@app.route('/predict-file', methods=['GET', 'POST'])
@cross_origin()
def predict():
    try:
        config.logger.log("INFO", "Prediction initiated...")
        if request.method == "POST":
            file = request.files['file']
            ingestion_response = PredictionDataIngestion(file).save_raw_data()
            if ingestion_response['status'] == 'Success':
                validation_response = PredictionDataValidation(ingestion_response['filename']).check_columns()
                if validation_response['status'] == 'Success':
                    upload_response = PredictionDBUpload(validation_response['filename'], 'valid').upload_to_db()
                    if upload_response['status'] == 'Success':
                        fetch_response = DBFetch(upload_response['table_name']).fetch_data_from_db()
                        if fetch_response['status'] == 'Success':
                            X = fetch_response['data']
                            model_finder = ModelFinder()
                            predict_response = model_finder.predict(X)
                            if predict_response['status'] == "Success":
                                pred = predict_response['pred']
                                df = pd.DataFrame().from_dict({"Item_Outlet_Sales": pred})
                                filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + ".csv"
                                filepath = os.path.join('predictions', filename)
                                df.to_csv(filepath, index=False)
                                Thread(target=FileDeleter(filepath).delete_file).start()
                                return send_file(filepath)
        return render_template("home_page.html", results="Prediction Unsuccessful")
    except Exception as e:
        config.logger.log("ERROR", str(e))
        return render_template("home_page.html", results="Internal Error Occured")


@app.route('/predict-data', methods=['GET', 'POST'])
@cross_origin()
def predict_data():
    try:
        config.logger.log("INFO", "Prediction initiated...")
        if request.method == "POST":
            data = {
                "Item_Identifier": [request.form["Item_Identifier"]],
                "Item_Weight": [float(request.form["Item_Weight"])],
                "Item_Fat_Content": [request.form["Item_Fat_Content"]],
                "Item_Visibility": [float(request.form["Item_Visibility"])],
                "Item_Type": [request.form["Item_Type"]],
                "Item_MRP": [float(request.form["Item_MRP"])],
                "Outlet_Identifier": [request.form["Outlet_Identifier"]],
                "Outlet_Establishment_Year": [request.form["Outlet_Establishment_Year"]],
                "Outlet_Size": [request.form["Outlet_Size"]],
                "Outlet_Location_Type": [request.form["Outlet_Location_Type"]],
                "Outlet_Type": [request.form["Outlet_Type"]]
            }
            config.logger.log("INFO", os.getcwd())
            config.logger.log("INFO", os.listdir())
            folder_path = '/app/prediction_raw_files'
            filename = 'prediction_raw_data_' + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + ".csv"
            filepath = os.path.join(folder_path, filename)
            test_data = pd.DataFrame.from_dict(data)
            test_data.to_csv(filename, index=False)
            config.logger.log("INFO", "File saved")
            test_data.to_csv(filepath, index=False)
            # test_data.to_csv(filename, index=False)
            config.logger.log("INFO", str(os.listdir(filepath)))
            validation_response = PredictionDataValidation(filename).check_columns()
            if validation_response['status'] == 'Success':
                upload_response = PredictionDBUpload(validation_response['filename'], 'valid').upload_to_db()
                if upload_response['status'] == 'Success':
                    fetch_response = DBFetch(upload_response['table_name']).fetch_data_from_db()
                    if fetch_response['status'] == 'Success':
                        X = fetch_response['data']
                        model_finder = ModelFinder()
                        predict_response = model_finder.predict(X)
                        if predict_response['status'] == "Success":
                            pred = predict_response['pred']
                            return render_template("home_page.html", results=str(pred[0]))
        return render_template("home_page.html", results="Prediction Unsuccessful")
    except Exception as e:
        config.logger.log("ERROR", str(e))
        return render_template("home_page.html", results="Internal Error Occured")


if __name__ == '__main__':
    config.logger.log("INFO", "App starting...")
    host = '0.0.0.0'
    port = int(os.getenv("PORT", 5000))
    app.run(host=host, port=port, debug=True)


