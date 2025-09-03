from bluer_objects import README

from bluer_ugv.README.consts import (
    assets2,
    assets2_bluer_eagle,
    assets2_bluer_robin,
    assets2_bluer_sparrow,
    assets2_bluer_swallow,
)

items = README.Items(
    [
        {
            "name": "bluer-swallow",
            "marquee": f"{assets2_bluer_swallow}/20250701_2206342_1.gif?raw=true",
            "description": "based on power wheels.",
            "url": "./bluer_ugv/docs/bluer_swallow",
        },
        {
            "name": "bluer-sparrow",
            "marquee": f"{assets2_bluer_sparrow}/VID-20250830-WA0000~3_1.gif?raw=true",
            "description": "[bluer-swallow](./bluer_ugv/docs/bluer_swallow)'s little sister.",
            "url": "./bluer_ugv/docs/bluer_sparrow",
        },
        {
            "name": "bluer-robin",
            "marquee": f"{assets2_bluer_robin}/20250723_095155~2_1.gif?raw=true",
            "description": "remote control car kit for teenagers.",
            "url": "./bluer_ugv/docs/bluer_robin",
        },
        {
            "name": "bluer-eagle",
            "marquee": f"{assets2_bluer_eagle}/file_0000000007986246b45343b0c06325dd.png?raw=true",
            "description": "a remotely controlled ballon.",
            "url": "./bluer_ugv/docs/bluer_eagle",
        },
        {
            "name": "bluer-fire",
            "marquee": "https://github.com/kamangir/assets/raw/main/bluer-ugv/bluer-fire.png?raw=true",
            "description": "based on a used car.",
            "url": "./bluer_ugv/docs/bluer_fire",
        },
        {
            "name": "bluer-beast",
            "marquee": "https://github.com/waveshareteam/ugv_rpi/raw/main/media/UGV-Rover-details-23.jpg",
            "description": "based on [UGV Beast PI ROS2](https://www.waveshare.com/wiki/UGV_Beast_PI_ROS2).",
            "url": "./bluer_ugv/docs/bluer_beast",
        },
    ]
)
