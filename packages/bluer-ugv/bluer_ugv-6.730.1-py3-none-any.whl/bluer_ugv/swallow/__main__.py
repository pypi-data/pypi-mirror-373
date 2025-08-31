import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_ugv import NAME
from bluer_ugv.swallow.targeting import select_target
from bluer_ugv.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="select_target",
)
parser.add_argument(
    "--host",
    type=str,
)
parser.add_argument(
    "--loop",
    type=int,
    default=1,
    help="0 | 1",
)
args = parser.parse_args()

success = False
if args.task == "select_target":
    success = select_target(
        host=args.host,
        loop=args.loop == 1,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
