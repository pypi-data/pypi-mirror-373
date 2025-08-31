from blueness import module
import numpy as np

from bluer_options.terminal import hr
from bluer_algo.socket.classes import SocketComm
from bluer_algo.tracker.classes.target import Target

from bluer_ugv import NAME
from bluer_ugv.logger import logger


NAME = module.name(__file__, NAME)


def select_target(
    host: str,
    loop: bool = True,
) -> bool:
    logger.info(
        "{}.select_target on {}{}".format(
            NAME,
            host,
            " on a loop." if loop else "",
        )
    )

    try:
        while loop:
            socket = SocketComm.listen_on()
            success, image = socket.receive_data(np.ndarray)
            if not success:
                return success

            success, track_window = Target.select(
                image,
                title=f"select target on {host} ...",
            )
            if not success:
                return success

            socket = SocketComm.connect_to(host)
            if not socket.send_data(track_window):
                return False

            hr_line = hr(
                width=12,
                mono=True,
            )
            logger.info(f"{hr_line} Ctrl+C to exit {hr_line}")
    except KeyboardInterrupt:
        logger.info("Ctrl+C, stopping.")

    return True
