import threading
from typing import Union, Dict

from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.setpoint.steering import (
    generate_left_and_right,
)
from bluer_ugv.logger import logger


class ClassicalSetPoint:
    def __init__(
        self,
        leds: ClassicalLeds,
    ):
        self.speed = 0
        self.steering = 0
        self.started = False

        self.leds = leds

        self._lock = threading.Lock()

    def get(
        self,
        what: str = "all",
    ) -> Union[int, bool, Dict[str, Union[int, bool]]]:
        with self._lock:
            if what == "all":
                return {
                    "speed": self.speed,
                    "started": self.started,
                    "steering": self.steering,
                }

            if what == "left":
                return generate_left_and_right(self.speed, self.steering)[0]

            if what == "right":
                return generate_left_and_right(self.speed, self.steering)[1]

            if what == "speed":
                return self.speed

            if what == "started":
                return self.started

            if what == "steering":
                return self.steering

            logger.error(f"{self.__class__.__name__}.get: {what} not found.")
            return 0

    def put(
        self,
        value: Union[int, bool, Dict[str, Union[int, bool]]],
        what: str = "all",
        log: bool = False,
    ):
        with self._lock:
            if what == "all":
                self.speed = min(100, max(-100, int(value["speed"])))
                self.started = bool(value["started"])
                self.steering = min(100, max(-100, int(value["steering"])))
                return

            if what == "speed":
                self.speed = min(100, max(-100, int(value)))
                if log:
                    logger.info(
                        "{}.put: speed={}".format(
                            self.__class__.__name__,
                            self.speed,
                        )
                    )
                return

            if what == "started":
                self.started = bool(value)
                if log:
                    logger.info(
                        "{}.put: {}".format(
                            self.__class__.__name__,
                            "started" if value else "stopped",
                        )
                    )
                return

            if what == "steering":
                self.steering = min(100, max(-100, int(value)))
                if log:
                    logger.info(
                        "{}.put: steering={}".format(
                            self.__class__.__name__,
                            self.steering,
                        )
                    )
                return

            logger.error(f"{self.__class__.__name__}.put: {what} not found.")

    def start(self):
        self.put(
            {
                "speed": 0,
                "started": True,
                "steering": 0,
            }
        )

        logger.info(f"{self.__class__.__name__}.start")

    def stop(self):
        self.put(
            {
                "speed": 0,
                "started": False,
                "steering": 0,
            }
        )

        logger.info(f"{self.__class__.__name__}.stop")

        self.leds.leds["red"]["state"] = False
        self.leds.leds["yellow"]["state"] = False

    def update(self) -> bool:
        with self._lock:
            if self.started:
                self.leds.leds["red"]["state"] = not self.leds.leds["red"]["state"]

        return True
