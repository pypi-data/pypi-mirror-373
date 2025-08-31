from RPi import GPIO  # type: ignore

from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.setpoint import ClassicalSetPoint
from bluer_ugv.logger import logger


class GenericMotor:
    def __init__(
        self,
        role: str,
        lpwm_pin: int,
        rpwm_pin: int,
        setpoint: ClassicalSetPoint,
        leds: ClassicalLeds,
    ):
        self.role = role
        self.lpwm_pin = lpwm_pin
        self.rpwm_pin = rpwm_pin
        self.setpoint = setpoint
        self.leds = leds
        self.state: int = 0

        self.lpwm = None
        self.rpwm = None

        # Internal state for jitter protection
        self._last_direction = 0  # -1 for reverse, 0 for stop, 1 for forward
        self._last_duty = 0  # Last applied duty cycle

        logger.info(f"{self.__class__.__name__}: {role}")

    def cleanup(self):
        try:
            if self.lpwm:
                self.lpwm.stop()
                self.lpwm = None
            if self.rpwm:
                self.rpwm.stop()
                self.rpwm = None
        except Exception as e:
            logger.warning(e)

        logger.info(f"{self.__class__.__name__}.cleanup")

    def initialize(self) -> bool:
        GPIO.setup(self.lpwm_pin, GPIO.OUT)
        GPIO.setup(self.rpwm_pin, GPIO.OUT)

        self.lpwm = GPIO.PWM(self.lpwm_pin, 1000)  # 1 kHz
        self.rpwm = GPIO.PWM(self.rpwm_pin, 1000)

        self.lpwm.start(0)
        self.rpwm.start(0)

        logger.info(
            "{}: {} motor initialized on LPWM=GPIO#{}, RPWM=GPIO#{}".format(
                self.__class__.__name__,
                self.role,
                self.lpwm_pin,
                self.rpwm_pin,
            )
        )
        return True

    def update(self) -> bool:
        self.state = self.setpoint.get(what=self.role)

        value = max(-100, min(100, self.state))  # Clamp
        duty_cycle = abs(value)

        direction = 0
        if value > 0:
            direction = 1
        elif value < 0:
            direction = -1

        if direction == self._last_direction and duty_cycle == self._last_duty:
            return True

        if direction == 1:
            self.rpwm.ChangeDutyCycle(duty_cycle)
            self.lpwm.ChangeDutyCycle(0)
        elif direction == -1:
            self.rpwm.ChangeDutyCycle(0)
            self.lpwm.ChangeDutyCycle(duty_cycle)
        else:
            self.rpwm.ChangeDutyCycle(0)
            self.lpwm.ChangeDutyCycle(0)

        self._last_direction = direction
        self._last_duty = duty_cycle

        logger.info(
            "{}.update: {} {}".format(
                self.__class__.__name__,
                "->" if direction == 1 else "<-",
                duty_cycle,
            )
        )

        self.leds.leds["red"]["state"] = not self.leds.leds["red"]["state"]

        return True
