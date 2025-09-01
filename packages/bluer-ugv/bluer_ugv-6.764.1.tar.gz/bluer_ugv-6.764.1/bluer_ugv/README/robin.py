from bluer_ugv.parts.db import db_of_parts
from bluer_ugv.robin.README import items
from bluer_ugv.robin.parts import dict_of_parts


docs = [
    {
        "items": items,
        "path": "../docs/bluer_robin",
    },
    {
        "path": "../docs/bluer_robin/parts.md",
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
