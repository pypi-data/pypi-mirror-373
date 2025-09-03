from bluer_objects.README.items import ImageItems

from bluer_ugv.parts.db import db_of_parts
from bluer_ugv.sparrow.README import items
from bluer_ugv.sparrow.parts import dict_of_parts
from bluer_ugv.README.consts import bluer_sparrow_mechanical_design

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
        "path": "../docs/bluer_sparrow/design/mechanical",
        "items": ImageItems(
            {
                f"{bluer_sparrow_mechanical_design}/robot.png": f"{bluer_sparrow_mechanical_design}/robot.stl",
                f"{bluer_sparrow_mechanical_design}/cage.png": f"{bluer_sparrow_mechanical_design}/cage.stl",
                f"{bluer_sparrow_mechanical_design}/measurements.png": "",
            }
        ),
    },
    {
        "path": "../docs/bluer_sparrow/design/mechanical/v1.md",
        "items": ImageItems(
            {
                f"{bluer_sparrow_mechanical_design}/v1/robot.png": f"{bluer_sparrow_mechanical_design}/v1/robot.stl",
                f"{bluer_sparrow_mechanical_design}/v1/cage.png": f"{bluer_sparrow_mechanical_design}/v1/cage.stl",
                f"{bluer_sparrow_mechanical_design}/v1/measurements.png": "",
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
