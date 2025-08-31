from RPi import GPIO  # type: ignore

from bluer_sbc.env import BLUER_SBC_ENV, BLUER_SBC_SWALLOW_HAS_STEERING

from bluer_ugv.swallow.session.classical.camera import (
    ClassicalCamera,
    ClassicalNavigationCamera,
    ClassicalTrackingCamera,
)
from bluer_ugv.swallow.session.classical.push_button import ClassicalPushButton
from bluer_ugv.swallow.session.classical.keyboard import ClassicalKeyboard
from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.mousepad import ClassicalMousePad
from bluer_ugv.swallow.session.classical.motor import (
    ClassicalLeftMotor,
    ClassicalRightMotor,
    ClassicalRearMotors,
    ClassicalSteeringMotor,
)
from bluer_ugv.swallow.session.classical.setpoint.classes import ClassicalSetPoint
from bluer_ugv.env import BLUER_UGV_MOUSEPAD_ENABLED
from bluer_ugv.logger import logger


class ClassicalSession:
    def __init__(
        self,
        object_name: str,
    ):
        self.object_name = object_name

        self.leds = ClassicalLeds()

        self.setpoint = ClassicalSetPoint(
            leds=self.leds,
        )

        if BLUER_UGV_MOUSEPAD_ENABLED:
            self.mousepad = ClassicalMousePad(
                leds=self.leds,
                setpoint=self.setpoint,
            )

        self.keyboard = ClassicalKeyboard(
            setpoint=self.setpoint,
        )

        self.push_button = ClassicalPushButton(
            leds=self.leds,
        )

        self.has_steering = BLUER_SBC_SWALLOW_HAS_STEERING == 1
        logger.info("has_steering: {}".format(self.has_steering))

        self.motor1 = (
            ClassicalSteeringMotor if self.has_steering else ClassicalRightMotor
        )(
            setpoint=self.setpoint,
            leds=self.leds,
        )

        self.motor2 = (
            ClassicalRearMotors if self.has_steering else ClassicalLeftMotor
        )(
            setpoint=self.setpoint,
            leds=self.leds,
        )

        logger.info(
            "wheel arrangement: {} + {}".format(
                self.motor1.role,
                self.motor2.role,
            )
        )

        camera_class = (
            ClassicalTrackingCamera
            if BLUER_SBC_ENV == "tracking"
            else (
                ClassicalNavigationCamera
                if BLUER_SBC_ENV == "navigation"
                else ClassicalCamera
            )
        )
        logger.info(f"camera: {camera_class.__name__}")
        self.camera = camera_class(
            keyboard=self.keyboard,
            leds=self.leds,
            setpoint=self.setpoint,
            object_name=self.object_name,
        )

        logger.info(
            "{}: created for {}".format(
                self.__class__.__name__,
                self.object_name,
            )
        )

    def cleanup(self):
        for thing in [
            self.motor1,
            self.motor2,
            self.camera,
        ]:
            thing.cleanup()

        GPIO.cleanup()

        logger.info(f"{self.__class__.__name__}.cleanup")

    def initialize(self) -> bool:
        try:
            GPIO.setmode(GPIO.BCM)
        except Exception as e:
            logger.error(e)
            return False

        return all(
            thing.initialize()
            for thing in [
                self.push_button,
                self.leds,
                self.motor1,
                self.motor2,
                self.camera,
            ]
        )

    def update(self) -> bool:
        return all(
            thing.update()
            for thing in [
                self.keyboard,
                self.push_button,
                self.camera,
                self.setpoint,
                self.motor1,
                self.motor2,
                self.leds,
            ]
        )
