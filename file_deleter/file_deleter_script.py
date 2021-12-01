import time
import os


class FileDeleter:

    def __init__(self, filepath):
        """
        This class is used to delete stale prediction files after they are dwonloaded by the user.
        :param filepath: path to the prediction file
        """
        self.filepath = filepath

    def delete_file(self):
        time.sleep(600)
        os.remove(self.filepath)
