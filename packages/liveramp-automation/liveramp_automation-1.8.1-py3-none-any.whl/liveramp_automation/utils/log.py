# -*- coding: utf-8 -*-
import configparser
import os
import logging
from datetime import datetime
from logging import handlers
from threading import Lock


class MyFormatter(logging.Formatter):

    def __init__(self,
                 fmt='%(asctime)s - %(levelname)s - [ %(test_case_name)s ] '
                     '[ %(filename)s: %(lineno)d ] - %(message)s '):
        logging.Formatter.__init__(self, fmt)

    def format(self, record):
        record.test_case_name = os.environ["SCENARIO_NAME"]
        result = logging.Formatter.format(self, record)
        return result


class LoggerUtils:
    """
    Singleton class for configuring and obtaining a logger instance.

    This class ensures that only one instance of the logger is created and shared among different parts of the codebase.
    It uses the Python 'logging' module to manage logging operations.
    
    Note: When a 'pytest.ini' configuration file is present, both console and file logging are enabled.
    If the file is not found, only console logging is enabled (no file logging).

    Usage:
    Logger = LoggerUtils.get_logger()

    :return: Logger instance
    :rtype: logging.Logger
    """

    _instance = None
    _lock = Lock()

    @classmethod
    def get_logger(cls):
        """
        Retrieve or create a logger instance.

        If an instance already exists, it returns that instance; otherwise,
        it creates and configures a new logger instance.

        :return: Logger instance
        :rtype: logging.Logger
        """

        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls._configure_logging()
        return cls._instance

    @staticmethod
    def _configure_logging():
        """
        Configure the logger based on settings from 'pytest.ini'.

        This method reads log-related configuration parameters from the 'pytest.ini' file,
        such as log path and log name.
        If the file is not found, only console logging is enabled (no file logging).

        :return: Configured logger instance
        :rtype: logging.Logger
        """
        config = configparser.ConfigParser()
        try:
            with open("pytest.ini", 'r') as file:
                config.read_file(file)
                try:
                    log_path = config.get('log', 'log_path')
                except (configparser.NoSectionError, configparser.NoOptionError):
                    log_path = "reports/"
                try:
                    log_name = config.get('log', 'log_name')
                except (configparser.NoSectionError, configparser.NoOptionError):
                    log_name = "%Y%m%d%H%M%S.log"
                try:
                    log_file_level = config.get('log', 'log_file_level')
                except (configparser.NoSectionError, configparser.NoOptionError):
                    log_file_level = logging.DEBUG
                try:
                    log_console_level = config.get('log', 'log_console_level')
                except (configparser.NoSectionError, configparser.NoOptionError):
                    log_console_level = logging.DEBUG
                try:
                    log_include_scenario = config.get('log', 'log_include_scenario')
                except (configparser.NoSectionError, configparser.NoOptionError):
                    log_include_scenario = "false"
                
                log_format = LoggerUtils.get_log_format(log_include_scenario)
                log_directory = os.path.join(os.getcwd(), log_path)
                if not os.path.exists(log_directory):
                    os.makedirs(log_directory)
                log_name = datetime.now().strftime(log_name)
                file_name = os.path.join(log_path, log_name)

                logger = logging.getLogger(log_name)
                logger.setLevel(logging.DEBUG)

                console_handler = logging.StreamHandler()
                console_handler.setFormatter(log_format)
                console_handler.setLevel(log_console_level)
                logger.addHandler(console_handler)

                file_handler = handlers.TimedRotatingFileHandler(filename=file_name, when='midnight', backupCount=30,
                                                             encoding='utf-8')
                file_handler.setLevel(log_file_level)
                file_handler.setFormatter(log_format)
                logger.addHandler(file_handler)

                logger.debug("======Now LOG BEGIN=======")
                return logger
                
        except FileNotFoundError:
            logger = logging.getLogger("console_only_logger")
            logger.setLevel(logging.DEBUG)
            

            console_format = logging.Formatter('%(asctime)s - %(levelname)s - [ %(filename)s: %(lineno)d ] - %(message)s')
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_format)
            console_handler.setLevel(logging.INFO)  
            logger.addHandler(console_handler)
            
            logger.info("======Console logging enabled (no pytest.ini found)=======")
            return logger

    @staticmethod
    def get_log_format(log_include_scenario):
        """
            Determine the logging format based on whether scenarios should be included.

            Args:
            - log_include_scenario (str): A string value indicating whether the log should include scenarios.
            Accepts 'true'/'false', 'yes'/'no', '1'/'0'.

            Returns:
            - str: The log format string based on the input.
            This could be customized based on whether scenarios are included or not.
            """

        # Define a simple conversion of common boolean representations
        def to_boolean(value):
            true_values = ['true', 'yes', '1']
            false_values = ['false', 'no', '0']

            # Normalize the string to lowercase to make the comparison case-insensitive
            value_lower = value.lower()
            if value_lower in true_values:
                return True
            elif value_lower in false_values:
                return False
            else:
                # Raise an error if the input is not a recognized boolean string
                raise ValueError(
                    f"Invalid input for log_include_scenario: {value}. Expected 'true/false', 'yes/no', '1/0'.")

        try:
            # Use the custom to_boolean function to convert the input string to a boolean
            include_scenario = to_boolean(log_include_scenario)
        except ValueError as e:
            # Propagate the error up with a clear message
            raise ValueError(f"Error processing log_include_scenario: {e}") from e

        if include_scenario:
            if not os.environ.get("SCENARIO_NAME"):
                os.environ["SCENARIO_NAME"] = ""
            log_format = MyFormatter()
        else:
            log_format = logging.Formatter('%(asctime)s - %(levelname)s - [ %(filename)s: %(lineno)d ] - %(message)s')

        return log_format


Logger = LoggerUtils.get_logger()
