# -*- coding: utf-8 -*-

import os
import time
import logging

def ignore_logger_exceptions(f):
    def wrapper(*args):
        try:
            return f(*args)
        except:
            pass
    return wrapper

class Logger:
    def __init__(self, logging_level='debug', console_level='info', log_file='debug.log'):
        log_file = log_file.replace('.log', '')

        log_levels = {
            'debug': logging.DEBUG
        ,   'info': logging.INFO
        ,   'error': logging.ERROR
        ,   'warning': logging.WARNING
        ,   'critical': logging.CRITICAL
        }

        log_level = log_levels.get(logging_level, logging.CRITICAL)
        self.console_level = log_levels.get(console_level, logging.INFO)
        formatter = '%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s'

        output_dir = 'logs/'

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        if log_level == logging.DEBUG:
            formatter = '%(asctime)s.%(msecs)03d | '\
                        '%(funcName)s | %(message)s'

        output = output_dir + '/' + time.strftime('%Y%m%d_%H%M%S_') + log_file

        logging.basicConfig(
            level=logging.NOTSET
        ,   format=formatter
        ,   datefmt='%Y-%m-%d %H:%M:%S'
        ,   filename=output + '.log'
        ,   filemode='w'
        )

        self.console = logging.StreamHandler()
        self.console.setLevel(self.console_level)
        self.console.setFormatter(logging.Formatter('%(asctime)s %(message)s', '%Y-%m-%d %H:%M:%S'))
        logging.getLogger(__name__).addHandler(self.console)

        # console_file = logging.FileHandler(output + '_console.log', mode='w')
        # console_file.setLevel(log_level)
        # console_file.setFormatter(
        #     logging.Formatter('%(asctime)s.%(msecs)03d | %(message)s', '%Y-%m-%d %H:%M:%S'))
        # logging.getLogger('').addHandler(console_file)

    @ignore_logger_exceptions
    def Error(self, msg):
        logging.error(msg)

    @ignore_logger_exceptions
    def Warning(self, msg):
        logging.warning(msg)

    @ignore_logger_exceptions
    def Critical(self, msg):
        logging.critical(msg)

    @ignore_logger_exceptions
    def Debug(self, msg):
        logging.debug(msg)

    @ignore_logger_exceptions
    def Info(self, msg):
        logging.info(msg)

    def Suppress(self, loggerName):
        logging.getLogger(loggerName).setLevel(100)

    def SuppressConsoleOutput(self):
        self.console.setLevel(100)

    def ResumeConsoleOutput(self):
        self.console.setLevel(self.console_level)