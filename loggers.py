import os
import json
import logging
import logging.config

FOLDER_LOG = "log"
LOGGING_CONFIG_FILE = 'loggers.json'


def crete_log_folder(folder: str = FOLDER_LOG) -> None:
    """
    Create folder to store log files
    :param folder: name of folder for store log files
    :return:
    """
    if not os.path.exists(folder):
        os.mkdir(folder)


def get_default_logger() -> logging.Logger:
    """
    Return default logger with config from loggers json file
    :return: default logger
    """
    crete_log_folder()

    with open(LOGGING_CONFIG_FILE, "r") as f:
        logging.config.dictConfig(json.load(f))

    return logging.getLogger("default")


def get_logger(name: str, template: str = 'default') -> logging.Logger:
    """
    :param name: name of logger that will be created from the template
    :param template: template for creating a logger
    :return: logger with config from json file
    """
    crete_log_folder()

    with open(LOGGING_CONFIG_FILE, "r") as f:
        dict_config = json.load(f)
        dict_config["loggers"][name] = dict_config["loggers"][template]
    logging.config.dictConfig(dict_config)

    return logging.getLogger(name)


if __name__ == "__main__":
    logger = get_default_logger()
    db_logger = get_logger('test', 'db_template')
