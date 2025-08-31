from typing import List, Union
import copy

from bluer_objects import markdown
from bluer_objects import file


class Part:
    def __init__(
        self,
        info: Union[List[str], str] = [],
        name: str = "",
        images: List[str] = [],
    ):
        self.name = name

        self.info = (
            copy.deepcopy(info)
            if isinstance(
                info,
                list,
            )
            else [info]
        )

        self.images = (
            copy.deepcopy(images)
            if isinstance(
                images,
                list,
            )
            else [images]
        )

    def filename(
        self,
        create: bool = False,
    ) -> str:
        filename = f"../docs/parts/{self.name}.md"

        if not create:
            return filename

        reference = file.path(__file__)
        full_filename = file.absolute(
            file.add_suffix(filename, "template"),
            reference,
        )

        if file.exists(full_filename):
            return filename

        assert file.copy(
            file.absolute(
                "../docs/parts/template-template.md",
                reference,
            ),
            full_filename,
            log=True,
        )

        return filename

    def image_url(
        self,
        url_prefix: str,
        filename: str = "",
    ) -> str:

        return (
            "{}/{}?raw=true".format(
                url_prefix,
                filename if filename else self.images[0],
            )
            if self.images
            else ""
        )

    def README(
        self,
        url_prefix: str,
    ) -> List[str]:
        return [f"- {info}" for info in self.info] + (
            [""]
            + markdown.generate_table(
                [
                    "![image]({})".format(
                        self.image_url(
                            url_prefix,
                            filename,
                        )
                    )
                    for filename in self.images
                ],
                cols=3,
                log=False,
            )
            if self.images
            else []
        )
