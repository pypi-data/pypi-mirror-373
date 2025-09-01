from typing import Tuple
import numpy as np

from bluer_options.timer import Timer
from bluer_options import string
from bluer_algo.tracker.classes.target import Target
from bluer_algo.tracker.classes.camshift import CamShiftTracker
from bluer_sbc.imager.camera import instance as camera

from bluer_ugv import env
from bluer_ugv.swallow.session.classical.camera.generic import ClassicalCamera
from bluer_ugv.swallow.session.classical.camera.generic import ClassicalCamera
from bluer_ugv.swallow.session.classical.keyboard import ClassicalKeyboard
from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.setpoint.classes import ClassicalSetPoint
from bluer_ugv.swallow.session.classical.mode import OperationMode
from bluer_ugv.logger import logger


class ClassicalTrackingCamera(ClassicalCamera):
    def __init__(
        self,
        keyboard: ClassicalKeyboard,
        leds: ClassicalLeds,
        setpoint: ClassicalSetPoint,
        object_name: str,
    ):
        super().__init__(keyboard, leds, setpoint, object_name)

        self.track_window: Tuple[int, int, int, int] = None

        self.tracking_timer = Timer(
            period=env.BLUER_UGV_CAMERA_ACTION_PERIOD,
            name="{}.tracking".format(self.__class__.__name__),
            log=True,
        )

        self.tracker = CamShiftTracker()

    def initialize(self) -> bool:
        if not super().initialize():
            return False

        return self.select_target()

    def select_target(self) -> bool:
        success, image = camera.capture(
            close_after=False,
            open_before=False,
            log=True,
        )
        if not success:
            return success

        self.leds.set_all(True)
        success, self.track_window = Target.select(
            np.flip(image, axis=2),
            local=False,
        )
        self.leds.set_all(False)
        if not success:
            return success

        logger.info(f"track_window: {self.track_window}")

        self.tracker.start(
            frame=image,
            track_window=self.track_window,
        )

        return True

    def update(self) -> bool:
        if not super().update():
            return False

        if self.keyboard.mode == OperationMode.TRAINING:
            return self.update_training()

        if self.setpoint.speed <= 0:
            return True

        if self.keyboard.mode == OperationMode.ACTION:
            return self.update_action()

        return True

    def update_action(self) -> bool:
        if not self.tracking_timer.tick():
            return True

        self.leds.leds["red"]["state"] = not self.leds.leds["red"]["state"]

        success, image = camera.capture(
            close_after=False,
            open_before=False,
            log=True,
        )
        if not success:
            return success

        _, self.track_window, _ = self.tracker.track(
            frame=image,
            track_window=self.track_window,
        )

        x, _, w, _ = self.track_window
        if x + w // 2 > image.shape[1] * 2 / 3:
            self.setpoint.put(
                what="steering",
                value=-env.BLUER_UGV_SWALLOW_STEERING_SETPOINT,
                log=True,
            )
        elif x + w // 2 < image.shape[1] * 1 / 3:
            self.setpoint.put(
                what="steering",
                value=env.BLUER_UGV_SWALLOW_STEERING_SETPOINT,
                log=True,
            )

        return True

    def update_training(self) -> bool:
        self.keyboard.mode = OperationMode.NONE
        return self.select_target()
