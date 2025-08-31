from evdev import InputDevice, ecodes  # type: ignore
import threading

from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.setpoint import ClassicalSetPoint
from bluer_ugv.logger import logger


class ClassicalMousePad:
    def __init__(
        self,
        leds: ClassicalLeds,
        setpoint: ClassicalSetPoint,
    ):
        self.leds = leds
        self.setpoint = setpoint

        try:
            self.device = InputDevice("/dev/input/event0")
            logger.info(
                "{}: using {}.".format(
                    self.__class__.__name__,
                    self.device.name,
                )
            )
        except Exception as e:
            logger.warning(e)
            self.device = None
            return

        self._thread = threading.Thread(
            target=self.run_,
            daemon=True,
        )
        self._thread.start()

    def run_(self) -> bool:
        logger.info(f"{self.__class__.__name__}: thread started.")

        for event in self.device.read_loop():
            if event.type == ecodes.EV_REL:
                if event.code == ecodes.REL_Y and self.setpoint.started:
                    self.setpoint.put(
                        what="speed",
                        value=self.setpoint.get(what="speed") - event.value,
                    )  # up/down
                elif event.code == ecodes.REL_X:
                    self.setpoint.put(
                        what="steering",
                        value=-event.value,
                    )  # left/right

                self.leds.leds["yellow"]["state"] = not self.leds.leds["yellow"][
                    "state"
                ]

            elif (
                event.type == ecodes.EV_KEY
                and event.code == ecodes.BTN_LEFT
                and event.value == 0
            ):
                self.setpoint.stop()

        return True
