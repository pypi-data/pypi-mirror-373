import logging
import logging.config
import os
from os import environ
from os.path import abspath, dirname, join

import yaml

DATE_FORMAT = '%y-%m-%d_%H-%M'


def get_cfg_root():
    """
    Returns:
        Directory with configuration files. By default cfg folder in the parent folder
    """
    if 'RP_CFG_ROOT' in environ:
        return environ['RP_CFG_ROOT']
    return join(dirname(abspath(__file__)), 'logging_cfg')


def read_logging_cfg():
    """
    """
    config_dir = get_cfg_root()
    file_name = config_dir + "//logging.yaml"
    with open(file_name, 'rt') as f:
        config = yaml.safe_load(f.read())

    return config


def setup_logging():
    """Setup logging configuration

    """
    default_level = eval("logging." + os.environ.get('LOG_LEVEL', 'WARN'))
    conf = read_logging_cfg()
    logging.config.dictConfig(conf)
    logger = logging.getLogger('msci.sdk')
    logger.setLevel(level=default_level)
    logging.getLogger("urllib3").propagate = False
    logging.getLogger('snowflake.connector').setLevel(logging.WARNING)
    logging.getLogger('snowflake.connector.connection').propagate = False
    logging.getLogger('snowflake.connector.cursor').propagate = False
