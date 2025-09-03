import argparse

from blueness import module
from blueness.argparse.generic import sys_exit
from bluer_objects.env import abcli_object_name

from bluer_ugv import NAME
from bluer_ugv.logger import logger
from bluer_ugv.swallow.session.functions import start_session

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="start_session",
)
args = parser.parse_args()

success = False
if args.task == "start_session":
    success = start_session(
        object_name=abcli_object_name,
    )
else:
    success = None
sys_exit(logger, NAME, args.task, success)
