from RPi import GPIO  # type: ignore

from bluer_ugv.logger import logger


class ClassicalLeds:
    def __init__(self):
        self.leds = {
            "yellow": {"pin": 17, "state": True},
            "red": {"pin": 27, "state": False},
            "green": {"pin": 22, "state": True},
        }

        logger.info(
            "{}: {}.".format(
                self.__class__.__name__,
                ", ".join(
                    [
                        "{}:GPIO#{}".format(
                            led_name,
                            led_info["pin"],
                        )
                        for led_name, led_info in self.leds.items()
                    ]
                ),
            )
        )

    def initialize(self) -> bool:
        try:
            for led in self.leds.values():
                GPIO.setup(
                    led["pin"],
                    GPIO.OUT,
                )
        except Exception as e:
            logger.error(e)
            return False

        return True

    def set_all(
        self,
        state: bool = True,
    ) -> bool:
        for led in self.leds.values():
            led["state"] = state

        return self.update(flash_green=False)

    def update(
        self,
        flash_green: bool = True,
    ) -> bool:
        if flash_green:
            self.leds["green"]["state"] = not self.leds["green"]["state"]

        for led in self.leds.values():
            GPIO.output(
                led["pin"],
                GPIO.HIGH if led["state"] else GPIO.LOW,
            )

        return True
