from blueness.argparse.generic import main

from bluer_ugv import NAME, VERSION, DESCRIPTION, ICON
from bluer_ugv.README.build import build
from bluer_ugv.logger import logger

main(
    ICON=ICON,
    NAME=NAME,
    DESCRIPTION=DESCRIPTION,
    VERSION=VERSION,
    main_filename=__file__,
    tasks={
        "build_README": lambda _: build(),
    },
    logger=logger,
)
