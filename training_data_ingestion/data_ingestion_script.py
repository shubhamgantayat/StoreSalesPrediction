import config
import pandas as pd
import datetime
import os


class TrainingDataIngestion:

    def __init__(self, file):
        """

        :param file: raw file for data ingestion provided from frontend
        """
        self.folder_path = 'training_raw_files'
        self.file = file

    def save_raw_data(self):
        """

        :return: Filename where raw data is saved
        """
        try:
            filename = 'training_raw_data_' + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + ".csv"
            filepath = os.path.join(self.folder_path, filename)
            train_data = pd.read_csv(self.file)
            train_data.to_csv(filepath, index=False)
            message = "Successful data ingestion"
            config.logger.log("INFO", message)
            return {"status": "Success", "filename": filename, "message": message}
        except Exception as e:
            message = str(e)
            config.logger.log("ERROR", message)
            return {"status": "Failure", "filename": None, "message": message}
