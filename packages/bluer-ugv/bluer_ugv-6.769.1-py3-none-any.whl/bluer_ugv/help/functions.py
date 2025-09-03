from typing import List

from bluer_ai.help.generic import help_functions as generic_help_functions

from bluer_ugv import ALIAS
from bluer_ugv.help.parts import help_functions as help_parts
from bluer_ugv.help.swallow import help_functions as help_swallow


help_functions = generic_help_functions(plugin_name=ALIAS)

help_functions.update(
    {
        "parts": help_parts,
        "swallow": help_swallow,
    }
)
