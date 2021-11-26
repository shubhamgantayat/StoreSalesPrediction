import os
import config
import pandas as pd
import json
import datetime


class TrainingDataValidation:

    def __init__(self, filename):
        try:
            folder_path = 'training_raw_files'
            with open('master_data_management/schema.json', 'r') as f:
                self.schema = json.load(f)
            self.map_dtypes = {
                "object": "str",
                "float32": "float",
                "float64": "float",
                "int32": "int",
                "int64": "int",
                "uint8": "int"
            }
            self.filename = filename
            self.filepath = os.path.join(folder_path, self.filename)
        except Exception as e:
            config.logger.log("ERROR", str(e))

    def check_columns(self):
        try:
            train_data = pd.read_csv(self.filepath)
            if self.schema['NoOfColumns'] == len(train_data.columns):
                col_dtypes = pd.DataFrame(train_data.dtypes, columns=['dtype'])
                col_dtypes['dtype'] = col_dtypes['dtype'].apply(lambda x:self.map_dtypes[str(x)])
                if col_dtypes.to_dict()['dtype'] == self.schema:
                    folder_path = 'training_batch_files'
                    file_name = 'training_batch_data_' + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + ".csv"
                    file_path = os.path.join(folder_path, self.filename)
                    train_data.to_csv(file_path, index=False)
                    message = "Successfully completed data validation"
                    config.logger.log("INFO", message)
                    return {"status": "Success", "filename": file_name, "message": message}
                else:
                    message = "column data types do not match"
                    config.logger.log("ERROR", message)
                    return {"status": "Failure", "filename": None, "message": message}
            else:
                message = "total number of columns are different"
                config.logger.log("ERROR", message)
                return {"status": "Failure", "filename": None, "message": message}
        except Exception as e:
            message = str(e)
            config.logger.log("ERROR", message)
            return {"status": "Failure", "filename": None, "message": message}

