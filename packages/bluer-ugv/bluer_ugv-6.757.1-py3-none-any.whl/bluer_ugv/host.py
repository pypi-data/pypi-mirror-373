from typing import List

from bluer_ai.host import signature as bluer_ai_signature
from bluer_sbc import fullname as bluer_sbc_fullname

from bluer_ugv import fullname


def signature() -> List[str]:
    return [
        fullname(),
        bluer_sbc_fullname(),
    ] + bluer_ai_signature()
