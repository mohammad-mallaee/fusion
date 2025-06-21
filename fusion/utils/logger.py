import logging
from logging.handlers import RotatingFileHandler
from os.path import join
import importlib
from shutil import copy
import subprocess

from fusion.utils.config import config

log_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s"
)

fusion_dir = importlib.import_module("fusion").__path__[0]
logFile = join(fusion_dir, "fusion.log")
my_handler = RotatingFileHandler(
    logFile, mode="a", maxBytes=5 * 1024 * 1024, backupCount=1, delay=False
)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

log = logging.getLogger("root")
log.setLevel(logging.INFO)

log.addHandler(my_handler)


def handle_log_command(args):
    if args.command == "open":
        subprocess.run([config.editor_name, logFile])
    elif args.command == "copy":
        copy(logFile, args.path)
        print("copied 'fusion.log' file into", args.path)
