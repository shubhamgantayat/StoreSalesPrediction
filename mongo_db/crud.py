import ssl
import pymongo
import pandas as pd
import csv
import os
from dotenv import load_dotenv


class Operations:

    def __init__(self, db_name, logger):
        """

        :param db_name: Name of the database to establish connection with.
        """
        try:
            self.lg = logger
            load_dotenv('env/mongo_credentials.env')
            username = os.getenv('MONGO_USERNAME')
            password = os.getenv('MONGO_PASSWORD')
            self.client = pymongo.MongoClient(
                f"mongodb+srv://{username}:{password}@cluster0.qwvki.mongodb.net/myFirstDatabase?retryWrites=true&w=majority".format(
                    username=username, password=password), ssl_cert_reqs=ssl.CERT_NONE)
            self.my_db = self.client[db_name]
            self.result = "connection with database successful"
            self.lg.log("info", self.result)
        except Exception as e:
            self.result = str(e)
            self.lg.log("error", self.result)

    def create_table(self, table_name):
        """

        :param table_name: Name of the table.
        :return: Result of the opearation.
        """
        try:
            table = self.my_db[table_name]
            self.result = "created table " + table_name
            self.lg.log("info", self.result)
        except Exception as e:
            self.result = str(e)
            self.lg.log("error", self.result)

    def insert_one(self, table_name, record):
        """

        :param table_name: Name of the table.
        :param record: {
            entity_1: val_1,
            entity_2: val_2,
            entity_3: val_3,
            ...
         }
        :return: Result of the operation
        """
        try:
            table = self.my_db[table_name]
            table.insert_one(record)
            self.result = "inserted a record"
            self.lg.log("info", self.result)
            return {"status": True, "message": "Successfully registered"}
        except pymongo.errors.DuplicateKeyError:
            return {"status": True, "message": "User already exists"}
        except Exception as e:
            self.result = str(e)
            self.lg.log("error", self.result)
            return {"status": True, "message": "Internal Error"}

    def insert_many(self, table_name, filepath, cols):

        """

        :param table_name: Name of the table.
        :param filepath: path\\to\\the\\csv\\file
        :param cols: [
            {"col_name": "id", "data_type": "int"},
            {"col_name": "name", "data_type": "string"},
            {"col_name": "count", "data_type": "int"}
        ]
        NOTE :- The col_name in the list should be in order as it is in the csv file.
        :return: Result of the operation.
        """
        int_types = ["int", "long"]
        float_types = ["float", "double"]
        str_types = ["string", "datetime"]
        bool_types = ["bool"]
        list_types = ["array"]

        map_data_type = {}
        map_data_type.update(dict().fromkeys(int_types, "int"))
        map_data_type.update(dict().fromkeys(float_types, "float"))
        map_data_type.update(dict().fromkeys(str_types, "str"))
        map_data_type.update(dict().fromkeys(bool_types, "bool"))
        map_data_type.update(dict().fromkeys(list_types, "list"))

        try:
            table = self.my_db[table_name]
            with open(filepath) as f:
                records = list(csv.reader(f))
                data = []
                for i in records[1:]:
                    new_record = []
                    for j in range(len(i)):
                        d_type = map_data_type[cols[j]['data_type']]
                        if d_type != 'str':
                            string = d_type + "(" + i[j] + ")"
                            new_record.append(eval(string))
                        else:
                            new_record.append(i[j])
                    data.append(dict(zip(records[0], new_record)))
            table.insert_many(data)
            self.result = "inserted " + str(len(records) - 1) + " records"
            self.lg.log("info", self.result)
        except Exception as e:
            self.result = str(e)
            self.lg.log("error", self.result)

    def update(self, table_name, condition, new_val):

        """

        :param table_name: Name of the table.
        :param condition: {
            <field_1>: <value_1>,
            <field_2>: <value_2>,
            ...
        }
        :param new_val: {
            $set : { <field_1>: <new_value_1 },
            $inc : { <field_1>: <new_value_1 },
            ...
        }
        :return: Returns the result of Operation
        """
        try:
            table = self.my_db[table_name]
            res = table.update_one(condition, new_val)
            if res.modified_count == 0:
                self.result = "User does not exist"
                self.lg.log("info", self.result)
                return {"status": False, "message": self.result}
            else:
                self.result = "updated records successfully"
                self.lg.log("info", self.result)
                return {"status": True, "message": "Successfully updated"}
        except Exception as e:
            self.result = str(e)
            self.lg.log("error", self.result)
            return {"status": False, "message": "Internal Error"}

    def delete(self, table_name, condition):

        """

        :param table_name: Name of the table.
        :param condition: {
            <field_1>: <value_1>,
            <field_2>: <value_2>,
            ...
        }
        :return: Returns the result of the operation.
        """
        try:
            table = self.my_db[table_name]
            res = table.delete_many(condition)
            if res.deleted_count == 0:
                self.result = "User does not exist"
                self.lg.log("info", self.result)
                return {"status": False, "message": self.result}
            else:
                self.result = "deleted records successfully"
                self.lg.log("info", self.result)
                return {"status": True, "message": "Successfully deleted"}
        except Exception as e:
            self.result = str(e)
            self.lg.log("error", self.result)
            return {"status": False, "message": "Internal Error"}

    def download(self, table_name, filepath):
        """

        :param table_name: Name of the table.
        :param filepath: path\\to\\new_file.csv
        :return: Returns the result of the operation.
        """
        try:
            table = self.my_db[table_name]
            df = pd.DataFrame(table.find())
            df.drop(columns=['_id'], axis=1, inplace=True)
            df.to_csv(filepath, index=False)
            self.result = "downloaded file successfully"
            self.lg.log("info", self.result)
        except Exception as e:
            self.result = str(e)
            self.lg.log("error", self.result)

    def display(self, table_name):
        table = self.my_db[table_name]
        for i in table.find():
            print(i)
