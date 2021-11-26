import os
import config
import json
import pandas as pd


class PredictionDBUpload:

    def __init__(self, filename, filetype):
        self.filename = filename
        if filetype == 'invalid':
            folder_path = 'prediction_invalid_files'
            self.table_name = filename[:-4]
        else:
            folder_path = 'prediction_batch_files'
            self.table_name = filename[:-4]
        self.filepath = os.path.join(folder_path, self.filename)

    def upload_to_db(self):
        try:
            df = pd.read_csv(self.filepath)
            table = config.mongo_db.my_db[self.table_name]
            table.insert_many(json.loads(df.to_json(orient='records')))
            config.logger.log("INFO", "Successfully uploaded to db")
            return {"status": "Success", "table_name": self.table_name, "message": "Successfully uploaded to db"}
        except Exception as e:
            config.logger.log("ERROR", "Upload to db unsuccessful")
            return {"status": "Failure", "table_name": None, "message": str(e)}
