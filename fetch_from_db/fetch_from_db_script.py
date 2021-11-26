import config
import pandas as pd


class DBFetch:

    def __init__(self, table_name):
        self.table_name = table_name

    def fetch_data_from_db(self):
        try:
            table = config.mongo_db.my_db[self.table_name]
            records = []
            for i in table.find():
                records.append(i)
            train_data = pd.DataFrame(data=records)
            train_data['Item_Weight'] = train_data['Item_Weight'].apply(lambda x: x if x != 0 else None)
            train_data['Outlet_Size'] = train_data['Outlet_Size'].apply(lambda x: x if x != '' else None)
            train_data.drop(columns=['_id'], inplace=True)
            message = "Successfully fetched from from db"
            config.logger.log("INFO", message)
            return {"status": "Success", "data": train_data, "message": message}
        except Exception as e:
            message = str(e)
            config.logger.log("ERROR", str(e))
            return {"status": "Failure", "data": None, "message": message}
