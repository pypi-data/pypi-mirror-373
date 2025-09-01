from typing import Tuple


def generate_left_and_right(speed: int, steering: int) -> Tuple[int, int]:
    right = speed + steering
    left = speed - steering

    m = max(abs(left), abs(right), 100)
    left = left * 100 / m
    right = right * 100 / m

    return int(left), int(right)
