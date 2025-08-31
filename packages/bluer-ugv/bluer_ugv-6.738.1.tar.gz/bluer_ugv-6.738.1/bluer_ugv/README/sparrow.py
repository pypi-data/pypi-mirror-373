from bluer_objects.README.items import ImageItems

from bluer_ugv.parts.db import db_of_parts
from bluer_ugv.sparrow.README import items
from bluer_ugv.sparrow.parts import dict_of_parts
from bluer_ugv.README.consts import bluer_sparrow_design

docs = [
    {
        "items": items,
        "path": "../docs/bluer_sparrow",
    },
    {
        "path": "../docs/bluer_sparrow/design",
    },
    {
        "path": "../docs/bluer_sparrow/design/specs.md",
    },
    {
        "path": "../docs/bluer_sparrow/design/parts.md",
        "items": db_of_parts.as_images(
            dict_of_parts,
            reference="../../parts",
        ),
        "macros": {
            "parts:::": db_of_parts.as_list(
                dict_of_parts,
                reference="../../parts",
                log=False,
            ),
        },
    },
    {
        "path": "../docs/bluer_sparrow/design/terraform.md",
    },
    {
        "path": "../docs/bluer_sparrow/design/mechanical.md",
        "items": ImageItems(
            {
                f"{bluer_sparrow_design}/robot.png": f"{bluer_sparrow_design}/robot.stl",
                f"{bluer_sparrow_design}/cage.png": f"{bluer_sparrow_design}/cage.stl",
            }
        ),
    },
    {
        "path": "../docs/bluer_sparrow/algo",
    },
    {
        "path": "../docs/bluer_sparrow/algo/target-detection",
    },
]
