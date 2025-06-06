# -*- coding: utf-8 -*-

# static log class
# It should call setup_logger to init your logger frist, then call logger = tmLog.getLogger(name) to get the logger
import logging,os,sys
import logging.handlers  
LOG_FILE_PATH="logs/ART_Runner.log"

dir= os.path.dirname(LOG_FILE_PATH)
if not os.path.isdir(dir):
    os.mkdir(dir)


class TmLog(object):
    @staticmethod
    def setup_logger(logger_name, log_file, level=logging.INFO, formatter = None):
        l = logging.getLogger(logger_name)
        fileHandler = logging.handlers.RotatingFileHandler(log_file,mode='a', maxBytes=1024*1024*10, backupCount=20, encoding="utf-8")
        if formatter == None:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s')
        else:
            formatter = logging.Formatter(formatter)
        fileHandler.setFormatter(formatter)
        l.setLevel(level)
        l.addHandler(fileHandler)

    @staticmethod
    def getLogger(name):
        try:
            return logging.getLogger(name)
        except Exception as err:
            print(str(err))
            return logging.getLogger()