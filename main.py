import pandas as pd
from flask import Flask, request, render_template
from wsgiref import simple_server
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
from sklearn.model_selection import train_test_split

app = Flask(__name__)
dashboard.bind(app)
CORS(app)
config.logger = Logger()
config.mongo_db = Operations("StoreSalesPrediction", config.logger)


@app.route('/', methods=['GET'])
@cross_origin()
def home():
    return "Flask app is running"


@app.route('/train-data', methods=['GET'])
@cross_origin()
def render_train_page():
    return render_template('train_data.html')


@app.route('/train', methods=['GET', 'POST'])
@cross_origin()
def train():
    if request.method == 'POST':
        config.logger.log("INFO", "Data training initiated...")
        file = request.files['file']
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
                        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

            elif validation_response['status'] == 'Failure' and validation_response['filename'] is not None:
                upload_response = TrainingDBUpload(validation_response['filename'], 'invalid').upload_to_db()
            else:
                config.logger.log("ERROR", "Internal Error Occured")
    return "Training Successful"


@app.route('/predict', methods=['GET', 'POST'])
@cross_origin()
def predict():
    config.logger.log("INFO", "Prediction initiated...")
    return "Prediction Successful"


if __name__ == '__main__':
    config.logger.log("INFO", "App starting...")
    host = '0.0.0.0'
    port = int(os.getenv("PORT", 5000))
    httpd = simple_server.make_server(host=host, port=port, app=app)
    httpd.serve_forever()


