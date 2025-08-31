from bluer_ugv.README.consts import assets2

NAME = "bluer_ugv"

ICON = "🐬"

DESCRIPTION = f"{ICON} AI x ROS."

VERSION = "6.730.1"

REPO_NAME = "bluer-ugv"

MARQUEE = f"{assets2}/bluer-swallow/20250701_2206342_1.gif"

ALIAS = "@ugv"


def fullname() -> str:
    return f"{NAME}-{VERSION}"
