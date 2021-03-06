import os
import config
import pandas as pd
import json


class TrainingDataValidation:

    def __init__(self, filename):
        """

        :param filename: filename of the raw data file.
        """
        try:
            folder_path = 'training_raw_files'
            with open('master_data_management/training_schema.json', 'r') as f:
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
        """

        :return: filename of the batch file if check was successful else filename of the invalid file
        """
        try:
            train_data = pd.read_csv(self.filepath)
            os.remove(self.filepath)
            null_columns = train_data.isna().sum()
            null_columns = list(null_columns[null_columns > 0].index)
            flag = True
            for nc in null_columns:
                if nc not in self.schema['NullColumns']:
                    flag = False
            if self.schema['NumberOfColumns'] == len(train_data.columns) and flag:
                col_dtypes = pd.DataFrame(train_data.dtypes, columns=['dtype'])
                col_dtypes['dtype'] = col_dtypes['dtype'].apply(lambda x:self.map_dtypes[str(x)])
                if col_dtypes.to_dict()['dtype'] == self.schema['ColData']:
                    folder_path = 'training_batch_files'
                    file_name = 'training_batch_data_' + self.filename[:-4].split("_")[-1] + ".csv"
                    file_path = os.path.join(folder_path, file_name)
                    train_data.to_csv(file_path, index=False)
                    message = "Successfully completed data validation"
                    config.logger.log("INFO", message)
                    return {"status": "Success", "filename": file_name, "message": message}
                else:
                    folder_path = 'training_invalid_files'
                    file_name = 'training_invalid_data_' + self.filename[:-4].split("_")[-1] + ".csv"
                    file_path = os.path.join(folder_path, file_name)
                    train_data.to_csv(file_path, index=False)
                    message = "column data types do not match"
                    config.logger.log("ERROR", message)
                    return {"status": "Failure", "filename": file_name, "message": message}
            else:
                folder_path = 'training_invalid_files'
                file_name = 'training_invalid_data_' + self.filename[:-4].split("_")[-1] + ".csv"
                file_path = os.path.join(folder_path, file_name)
                train_data.to_csv(file_path, index=False)
                message = "total number of columns are different"
                config.logger.log("ERROR", message)
                return {"status": "Failure", "filename": file_name, "message": message}
        except Exception as e:
            message = str(e)
            config.logger.log("ERROR", message)
            return {"status": "Failure", "filename": None, "message": message}

