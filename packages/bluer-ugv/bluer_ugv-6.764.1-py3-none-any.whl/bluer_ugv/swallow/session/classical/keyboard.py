import keyboard

from bluer_sbc.session.functions import reply_to_bash

from bluer_ugv.swallow.session.classical.setpoint.classes import ClassicalSetPoint
from bluer_ugv.swallow.session.classical.mode import OperationMode
from bluer_ugv import env
from bluer_ugv.logger import logger

bash_keys = {
    "i": "exit",
    "o": "shutdown",
    "p": "reboot",
    "u": "update",
}


class ClassicalKeyboard:
    def __init__(
        self,
        setpoint: ClassicalSetPoint,
    ):
        logger.info(
            "{}: {}".format(
                self.__class__.__name__,
                ", ".join(
                    [f"{key}:{action}" for key, action in bash_keys.items()],
                ),
            )
        )

        self.last_key: str = ""
        self.setpoint = setpoint

        self.mode = OperationMode.NONE

    def update(self) -> bool:
        self.last_key = ""

        mode = self.mode

        for key, event in bash_keys.items():
            if keyboard.is_pressed(key):
                reply_to_bash(event)
                return False

        if keyboard.is_pressed(" "):
            self.setpoint.stop()

        if keyboard.is_pressed("x"):
            self.setpoint.start()

        if keyboard.is_pressed("a"):
            self.last_key = "a"
            self.setpoint.put(
                what="steering",
                value=env.BLUER_UGV_SWALLOW_STEERING_SETPOINT,
            )
        elif keyboard.is_pressed("d"):
            self.last_key = "d"
            self.setpoint.put(
                what="steering",
                value=-env.BLUER_UGV_SWALLOW_STEERING_SETPOINT,
            )
        else:
            self.setpoint.put(
                what="steering",
                value=0,
                log=False,
            )

        if keyboard.is_pressed("s"):
            self.setpoint.put(
                what="speed",
                value=self.setpoint.get(what="speed") - 10,
            )

        if keyboard.is_pressed("w"):
            self.setpoint.put(
                what="speed",
                value=self.setpoint.get(what="speed") + 10,
            )

        if keyboard.is_pressed("y"):
            self.mode = OperationMode.NONE

        if keyboard.is_pressed("t"):
            self.mode = OperationMode.TRAINING

        if keyboard.is_pressed("g"):
            self.mode = OperationMode.ACTION

        if mode != self.mode:
            logger.info("mode: {}.".format(self.mode.name.lower()))

        return True
