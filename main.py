from flask import Flask, request, render_template
from wsgiref import simple_server
import os
import flask_monitoringdashboard as dashboard
from flask_cors import CORS, cross_origin
from mongo_db.crud import Operations
from logger.log_db import Logger
import config

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


