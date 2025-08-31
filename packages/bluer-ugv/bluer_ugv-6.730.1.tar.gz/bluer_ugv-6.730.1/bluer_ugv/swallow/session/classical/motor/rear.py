from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.motor.generic import GenericMotor
from bluer_ugv.swallow.session.classical.setpoint import ClassicalSetPoint


class ClassicalRearMotors(GenericMotor):
    def __init__(
        self,
        setpoint: ClassicalSetPoint,
        leds: ClassicalLeds,
    ):
        super().__init__(
            role="speed",
            lpwm_pin=19,
            rpwm_pin=13,
            setpoint=setpoint,
            leds=leds,
        )
