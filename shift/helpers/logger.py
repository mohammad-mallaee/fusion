import logging
from logging.handlers import RotatingFileHandler
from os.path import dirname, abspath, join

log_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s"
)

logFile = join(dirname(dirname(dirname(abspath(__file__)))), "shift.log")
my_handler = RotatingFileHandler(
    logFile, mode="a", maxBytes=5 * 1024 * 1024, backupCount=1, delay=False
)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

log = logging.getLogger("root")
log.setLevel(logging.INFO)

log.addHandler(my_handler)
