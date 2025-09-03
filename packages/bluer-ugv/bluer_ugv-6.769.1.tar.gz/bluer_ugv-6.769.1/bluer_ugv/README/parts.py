from bluer_ugv.parts.db import db_of_parts

docs = [
    {
        "path": "../docs/parts",
        "macros": {"list:::": db_of_parts.README},
    }
] + [
    {
        "path": part.filename(create=True),
        "macros": {"info:::": part.README(db_of_parts.url_prefix)},
    }
    for part_name, part in db_of_parts.items()
    if part_name != "template"
]
