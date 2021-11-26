from logging import Handler, LogRecord, getLogger
import pymongo
import ssl
import os
from dotenv import load_dotenv


class DB_Handler(Handler):

    def __init__(self, level=0, backup_logger_name=None):
        """

        A log handler created to upload all log data to mongo db server.
        If in case the server cannot be reached, a log file "file.log" will be created and data will be dumped there.
        """
        super().__init__(level)
        if backup_logger_name:
            self.backup_logger_name = backup_logger_name
            self.backup_logger = getLogger(backup_logger_name)

    def emit(self, record: LogRecord) -> None:
        try:
            load_dotenv('env/mongo_credentials.env')
            username = os.getenv('MONGO_USERNAME')
            password = os.getenv('MONGO_PASSWORD')
            client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.qwvki.mongodb.net/myFirstDatabase?retryWrites=true&w=majority".format(username=username, password=password), ssl_cert_reqs=ssl.CERT_NONE)
            my_db = client["StoreSalesPrediction"]
            record = {
                "levelname": record.levelname,
                "log_msg": record.msg,
                "name": record.name,
                "levelno": record.levelno,
                "datetime": self.format(record).split(" - ")[1]
            }
            table = my_db['logger']
            table.insert_one(record)
        except Exception as e:
            print(e)
            # if self.backup_logger:
            #     string = "self." + self.backup_logger_name + "." + record.levelname.lower() + "('" + self.format(record) + "')"
            #     eval(string)
            # else:
            #     print(self.format(record))
