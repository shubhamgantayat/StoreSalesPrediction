from flask import Flask
from wsgiref import simple_server
import os
import flask_monitoringdashboard as dashboard
from flask_cors import CORS, cross_origin

app = Flask(__name__)
dashboard.bind(app)
CORS(app)


@app.route('/', methods=['GET'])
@cross_origin()
def home():
    return "Flask app is running and i am changing something."


if __name__ == '__main__':
    host = '0.0.0.0'
    port = int(os.getenv("PORT", 5000))
    httpd = simple_server.make_server(host=host, port=port, app=app)
    httpd.serve_forever()


