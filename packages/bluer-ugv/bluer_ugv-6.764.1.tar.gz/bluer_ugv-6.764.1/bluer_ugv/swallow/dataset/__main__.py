import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_ugv import NAME
from bluer_ugv.swallow.dataset.combination import combine
from bluer_ugv.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="combine",
)
parser.add_argument(
    "--count",
    type=int,
    default=-1,
)
parser.add_argument(
    "--download",
    type=int,
    default=1,
    help="0 | 1",
)
parser.add_argument(
    "--object_name",
    type=str,
)
parser.add_argument(
    "--recent",
    type=int,
    default=1,
    help="0 | 1",
)
parser.add_argument(
    "--split",
    type=int,
    default=1,
    help="0 | 1",
)
parser.add_argument(
    "--test_ratio",
    type=float,
    default=0.1,
)
parser.add_argument(
    "--train_ratio",
    type=float,
    default=0.8,
)
parser.add_argument(
    "--datasets",
    type=str,
    default="not-given",
    help="<object-name-1>,<object-name-2>",
)
parser.add_argument(
    "--sequence",
    type=int,
    default=-1,
)
args = parser.parse_args()

success = False
if args.task == "combine":
    success = combine(
        object_name=args.object_name,
        count=args.count,
        download=args.download == 1,
        recent=args.recent == 1,
        sequence=args.sequence,
        split=args.split == 1,
        test_ratio=args.test_ratio,
        train_ratio=args.train_ratio,
        explicit_dataset_object_names=args.datasets,
    )
else:
    success = None
sys_exit(logger, NAME, args.task, success)
