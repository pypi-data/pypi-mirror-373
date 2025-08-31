from blueness.pypi import setup

from bluer_ugv import NAME, VERSION, DESCRIPTION, REPO_NAME

setup(
    filename=__file__,
    repo_name=REPO_NAME,
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    packages=[
        NAME,
        f"{NAME}.help",
        f"{NAME}.help.swallow",
        f"{NAME}.parts",
        f"{NAME}.README",
        # kinds
        f"{NAME}.eagle",
        f"{NAME}.fire",
        f"{NAME}.robin",
        f"{NAME}.swallow",
        f"{NAME}.swallow.dataset",
        f"{NAME}.swallow.session",
        f"{NAME}.swallow.session.classical",
        f"{NAME}.swallow.session.classical.camera",
        f"{NAME}.swallow.session.classical.motor",
        f"{NAME}.sparrow",
    ],
    include_package_data=True,
    package_data={
        NAME: [
            "config.env",
            "sample.env",
            ".abcli/**/*.sh",
        ],
    },
)
