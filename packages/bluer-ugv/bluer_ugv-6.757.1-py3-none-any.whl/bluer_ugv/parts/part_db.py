from typing import Dict, List, Iterator, Tuple
import copy
import os
import numpy as np
import cv2
from functools import reduce
from tqdm import tqdm

from blueness import module
from bluer_options.logger import log_list
from bluer_options import string
from bluer_objects import file
from bluer_objects import README
from bluer_objects.env import abcli_path_git

from bluer_ugv import NAME
from bluer_ugv.parts.part import Part
from bluer_ugv.README.consts import assets2
from bluer_ugv.logger import logger

NAME = module.name(__file__, NAME)


class PartDB:
    def __init__(self):
        self._db: Dict[str, Part] = {}

        self.url_prefix = f"{assets2}/bluer-ugv"

        self.path = os.path.join(
            abcli_path_git,
            "assets2/bluer-ugv",
        )

    def __iter__(self):
        return iter(self._db.values())

    def __setitem__(
        self,
        name: str,
        part: Part,
    ):
        assert isinstance(part, Part)

        self._db[name] = copy.deepcopy(part)
        self._db[name].name = name

    def __getitem__(self, name: str) -> Part:
        return self._db[name]

    def items(self) -> Iterator[Tuple[str, Part]]:
        return self._db.items()

    @property
    def README(self) -> List[str]:
        return sorted(
            [
                "- [{}](./{}.md).".format(
                    part.info[0],
                    part.name,
                )
                for part in self
            ]
        )

    def adjust(
        self,
        dryrun: bool = True,
        verbose: bool = False,
    ) -> bool:
        logger.info(
            "{}.adjust{}".format(
                NAME,
                " [dryrun]" if dryrun else "",
            )
        )

        list_of_filenames = reduce(
            lambda x, y: x + y,
            [
                [part.images[0]]
                for part_name, part in self._db.items()
                if part_name != "template" and part.images
            ],
            [],
        )
        log_list(logger, "adjusting", list_of_filenames, "images")

        max_width = 0
        max_height = 0
        for filename in tqdm(list_of_filenames):
            success, image = file.load_image(
                os.path.join(self.path, filename),
                log=verbose,
            )
            if not success:
                return success

            max_height = max(max_height, image.shape[0])
            max_width = max(max_width, image.shape[1])

        logger.info(f"size: {max_height} x {max_width}")

        for filename in tqdm(list_of_filenames):
            success, image = file.load_image(
                os.path.join(self.path, filename),
                log=verbose,
            )
            if not success:
                return success

            if image.shape[0] == max_height and image.shape[1] == max_width:
                logger.info("✅")
                continue

            image = image[:, :, :3]

            scale = min(
                max_height / image.shape[0],
                max_width / image.shape[1],
            )
            image = cv2.resize(
                image,
                dsize=(
                    int(scale * image.shape[1]),
                    int(scale * image.shape[0]),
                ),
                interpolation=cv2.INTER_LINEAR,
            )

            padded_image = (
                np.ones(
                    (max_height, max_width, 3),
                    dtype=np.uint8,
                )
                * 255
            )

            y_offset = (max_height - image.shape[0]) // 2
            x_offset = (max_width - image.shape[1]) // 2

            padded_image[
                y_offset : y_offset + image.shape[0],
                x_offset : x_offset + image.shape[1],
            ] = image

            if not dryrun:
                if not file.save_image(
                    os.path.join(self.path, filename),
                    padded_image,
                    log=verbose,
                ):
                    return False

        return True

    def as_images(
        self,
        dict_of_parts: Dict[str, str],
        reference: str = "../../parts",
    ) -> List[str]:
        return README.Items(
            [
                {
                    "name": self._db[part_name].info[0],
                    "marquee": self._db[part_name].image_url(
                        url_prefix=self.url_prefix
                    ),
                    "description": description,
                    "url": f"{reference}/{part_name}.md",
                }
                for part_name, description in dict_of_parts.items()
            ],
            sort=True,
        )

    def as_list(
        self,
        dict_of_parts: Dict[str, str],
        reference: str = "../../parts",
        log: bool = True,
    ) -> List[str]:
        if log:
            logger.info(
                "{}.as_list: {}".format(
                    self.__class__.__name__,
                    ", ".join(dict_of_parts.keys()),
                )
            )

        for part_name in dict_of_parts:
            if part_name not in self._db:
                logger.error(f"{part_name}: part not found.")
                assert False

        return sorted(
            [
                (
                    "1. [{}{}]({}).".format(
                        self._db[part_name].info[0],
                        ": {}".format(description) if description else "",
                        f"{reference}/{part_name}.md",
                    )
                )
                for part_name, description in dict_of_parts.items()
            ]
        )
