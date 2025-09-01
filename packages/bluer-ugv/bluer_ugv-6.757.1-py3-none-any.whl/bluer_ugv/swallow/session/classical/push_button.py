from RPi import GPIO  # type: ignore
import time

from bluer_options import string
from bluer_sbc.session.functions import reply_to_bash

from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.logger import logger

BUTTON_PRESS_DURATION_UPDATE = 5
BUTTON_PRESS_DURATION_SHUTDOWN = 10
BUTTON_PRESS_DURATION_IGNORE = 15


class ClassicalPushButton:
    def __init__(self, leds: ClassicalLeds):
        self.pin = 26
        self.state = False

        logger.info(
            "{}: GPIO#{}.".format(
                self.__class__.__name__,
                self.pin,
            )
        )

        self.press_time: int = 0
        self.press_duration: int = -1

        self.leds = leds

    def initialize(self) -> bool:
        try:
            GPIO.setup(
                self.pin,
                GPIO.IN,
                pull_up_down=GPIO.PUD_UP,
            )
        except Exception as e:
            logger.error(e)
            return False

        return True

    def update(self) -> bool:
        button_pressed = not GPIO.input(self.pin)
        if button_pressed:
            if not self.state:
                logger.info("push button pressed.")
                self.press_time = time.time()

            self.leds.leds["yellow"]["state"] = True

            self.press_duration = time.time() - self.press_time
            if self.press_duration > BUTTON_PRESS_DURATION_IGNORE:
                self.leds.leds["red"]["state"] = False
            elif self.press_duration > BUTTON_PRESS_DURATION_SHUTDOWN:
                self.leds.leds["red"]["state"] = True
            elif self.press_duration > BUTTON_PRESS_DURATION_UPDATE:
                self.leds.leds["red"]["state"] = not self.leds.leds["red"]["state"]
        elif self.state:
            logger.info(
                "push button released after {}.".format(
                    string.pretty_duration(
                        self.press_duration,
                    )
                )
            )

            self.leds.leds["yellow"]["state"] = False

            if self.press_duration < BUTTON_PRESS_DURATION_IGNORE:
                if self.press_duration > BUTTON_PRESS_DURATION_SHUTDOWN:
                    reply_to_bash("shutdown")
                    return False

                if self.press_duration > BUTTON_PRESS_DURATION_UPDATE:
                    reply_to_bash("update")
                    return False

        self.state = button_pressed

        return True
