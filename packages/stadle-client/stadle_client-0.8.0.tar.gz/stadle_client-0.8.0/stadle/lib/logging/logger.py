import logging
import logging.config
from os import path, mkdir


class Logger(object):


    def __init__(self, class_name):
        if (not path.exists('stadle_logs')):
            mkdir('stadle_logs')
            
        log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.conf')
        logging.config.fileConfig(fname=log_file_path, disable_existing_loggers=False)
        self.logger_instance = logging.getLogger(name=class_name)

    @property
    def logger(self):
        return self.logger_instance
