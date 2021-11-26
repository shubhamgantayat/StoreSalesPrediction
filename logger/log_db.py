import logging as lg
from .db_handler import DB_Handler


class Logger:

    def __init__(self):
        """
        Initializes logger
        """
        lg.basicConfig(level=lg.DEBUG, format='%(name)s - %(asctime)s - %(levelname)s - %(message)s')
        format1 = lg.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s')
        
        # backup_logger = lg.getLogger('backup_logger')
        # file_handler = lg.FileHandler('file.log')
        # file_handler.setLevel(lg.DEBUG)
        # file_handler.setFormatter(format1)
        # backup_logger.addHandler(file_handler)

        self.db_logger = lg.getLogger('logger')
        db_handler = DB_Handler()
        db_handler.setLevel(lg.DEBUG)
        db_handler.setFormatter(format1)
        self.db_logger.addHandler(db_handler)

    def log(self, levelname, message):
        """

        :param levelname: info, debug, warning, error or critical.
        :param message: log message
        :return: None
        """
        levelname = levelname.upper()
        if levelname == "INFO":
            self.db_logger.info(str(message))
        elif levelname == "DEBUG":
            self.db_logger.debug(str(message))
        elif levelname == "WARNING":
            self.db_logger.warning(str(message))
        elif levelname == "ERROR":
            self.db_logger.error(str(message))
        elif levelname == "CRITICAL":
            self.db_logger.critical(str(message))
