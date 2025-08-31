from bluer_objects.README.items import ImageItems

from bluer_ugv.parts.db import db_of_parts
from bluer_ugv.swallow.README import items
from bluer_ugv.swallow.parts import dict_of_parts
from bluer_ugv.README.consts import algo_docs, assets, assets2_bluer_swallow

docs = [
    {
        "items": items,
        "path": "../docs/bluer_swallow",
    },
    {
        "path": "../docs/bluer_swallow/analog",
        "items": ImageItems(
            {
                "../../../../diagrams/bluer_swallow/analog.png": "../../../../diagrams/bluer_swallow/analog.svg",
            }
        ),
    },
    {
        "path": "../docs/bluer_swallow/digital",
    },
    {
        "path": "../docs/bluer_swallow/digital/design",
    },
    {
        "path": "../docs/bluer_swallow/digital/design/operation.md",
    },
    {
        "path": "../docs/bluer_swallow/digital/design/parts.md",
        "items": db_of_parts.as_images(
            dict_of_parts,
            reference="../../../parts",
        ),
        "macros": {
            "parts:::": db_of_parts.as_list(
                dict_of_parts,
                reference="../../../parts",
                log=False,
            ),
        },
    },
    {
        "path": "../docs/bluer_swallow/digital/design/terraform.md",
        "items": ImageItems(
            {
                f"{assets2_bluer_swallow}/20250611_100917.jpg": "",
                f"{assets2_bluer_swallow}/lab.png": "",
                f"{assets2_bluer_swallow}/lab2.png": "",
            }
        ),
    },
    {
        "path": "../docs/bluer_swallow/digital/design/steering-over-current-detection.md",
        "items": ImageItems(
            {
                "../../../../../diagrams/bluer_swallow/steering-over-current.png": "../../../../../diagrams/bluer_swallow/steering-over-current.svg",
            }
        ),
    },
    {
        "path": "../docs/bluer_swallow/digital/design/rpi-pinout.md",
    },
    {
        "path": "../docs/bluer_swallow/digital/algo",
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving",
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving/dataset",
        "items": ImageItems(
            {
                f"{assets}/swallow-dataset-2025-07-11-10-53-04-n3oybs/grid.png": "./digital/dataset/combination/validation.md",
            }
        ),
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving/dataset/collection",
        "items": ImageItems(
            {
                f"{assets2_bluer_swallow}/2025-07-08-13-09-38-so54ao.png": "",
                f"{assets2_bluer_swallow}/2025-07-09-11-20-27-4qf255-000-2.png": "",
                f"{assets2_bluer_swallow}/2025-07-09-11-18-07-azy27w.png": f"{algo_docs}/image_classifier/dataset/sequence.md",
            }
        ),
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving/dataset/collection/validation.md"
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving/dataset/collection/one.md"
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving/dataset/combination"
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving/dataset/combination/validation.md"
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving/dataset/combination/one.md"
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving/dataset/review.md",
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving/model",
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving/model/validation.md"
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/autonomous-driving/model/one.md",
    },
    {
        "path": "../docs/bluer_swallow/digital/algo/target-tracking",
        "items": ImageItems(
            {
                f"{assets2_bluer_swallow}/target-selection.png": f"{algo_docs}/socket.md",
            }
        ),
    },
]
