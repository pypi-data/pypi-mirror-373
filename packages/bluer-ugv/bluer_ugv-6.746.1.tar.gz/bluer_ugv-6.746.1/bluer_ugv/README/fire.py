from bluer_ugv.parts.db import db_of_parts
from bluer_ugv.fire.README import items
from bluer_ugv.fire.parts import dict_of_parts

docs = [
    {"path": "../docs/bluer_fire"},
    {
        "path": "../docs/bluer_fire/parts.md",
        "items": db_of_parts.as_images(
            dict_of_parts,
            reference="../parts",
        ),
        "macros": {
            "parts:::": db_of_parts.as_list(
                dict_of_parts,
                reference="../parts",
                log=False,
            ),
        },
    },
]
