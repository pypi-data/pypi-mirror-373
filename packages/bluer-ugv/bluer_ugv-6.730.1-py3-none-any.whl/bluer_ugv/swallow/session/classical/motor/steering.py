from bluer_ugv.swallow.session.classical.motor.generic import GenericMotor
from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.setpoint import ClassicalSetPoint


class ClassicalSteeringMotor(GenericMotor):
    def __init__(
        self,
        setpoint: ClassicalSetPoint,
        leds: ClassicalLeds,
    ):
        super().__init__(
            role="steering",
            lpwm_pin=12,
            rpwm_pin=18,
            setpoint=setpoint,
            leds=leds,
        )
