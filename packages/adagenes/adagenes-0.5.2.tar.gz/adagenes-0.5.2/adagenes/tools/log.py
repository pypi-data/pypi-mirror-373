import logging, datetime
import adagenes.conf.read_config as conf_reader


def setup_custom_logger(name):
    """

    :param name:
    :return:
    """
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger


def get_current_datetime():
    """

    :return:
    """
    current_time = datetime.datetime.now()
    dt = str(current_time.year) + "-" + str(current_time.month) + "-" + str(current_time.day) + "_" + str(
        current_time.hour) + ":" + str(current_time.minute) + ":" + str(current_time.second)
    return dt
