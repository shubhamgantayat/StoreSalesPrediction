import os
import config
import pandas as pd
import json


class PredictionDataValidation:

    def __init__(self, filename):
        try:
            folder_path = 'prediction_raw_files'
            with open('master_data_management/prediction_schema.json', 'r') as f:
                self.schema = json.load(f)
            self.map_dtypes = {
                "object": "string",
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
            test_data = pd.read_csv(self.filepath)
            null_columns = test_data.isna().sum()
            null_columns = list(null_columns[null_columns > 0].index)
            if self.schema['NumberOfColumns'] == len(test_data.columns) and self.schema['NullColumns'] == null_columns:
                col_dtypes = pd.DataFrame(test_data.dtypes, columns=['dtype'])
                col_dtypes['dtype'] = col_dtypes['dtype'].apply(lambda x:self.map_dtypes[str(x)])
                if col_dtypes.to_dict()['dtype'] == self.schema['ColData']:
                    folder_path = 'prediction_batch_files'
                    file_name = 'prediction_batch_data_' + self.filename[:-4].split("_")[-1] + ".csv"
                    file_path = os.path.join(folder_path, file_name)
                    test_data.to_csv(file_path, index=False)
                    message = "Successfully completed data validation"
                    config.logger.log("INFO", message)
                    return {"status": "Success", "filename": file_name, "message": message}
                else:
                    folder_path = 'prediction_invalid_files'
                    file_name = 'prediction_invalid_data_' + self.filename[:-4].split("_")[-1] + ".csv"
                    file_path = os.path.join(folder_path, file_name)
                    test_data.to_csv(file_path, index=False)
                    message = "column data types do not match"
                    config.logger.log("ERROR", message)
                    return {"status": "Failure", "filename": file_name, "message": message}
            else:
                folder_path = 'prediction_invalid_files'
                file_name = 'prediction_invalid_data_' + self.filename[:-4].split("_")[-1] + ".csv"
                file_path = os.path.join(folder_path, file_name)
                test_data.to_csv(file_path, index=False)
                message = "total number of columns are different"
                config.logger.log("ERROR", message)
                return {"status": "Failure", "filename": file_name, "message": message}
        except Exception as e:
            message = str(e)
            config.logger.log("ERROR", message)
            return {"status": "Failure", "filename": None, "message": message}

