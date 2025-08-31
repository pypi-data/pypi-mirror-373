from typing import List
from tqdm import tqdm, trange

from blueness import module
from bluer_options.logger import log_list
from bluer_objects import storage, objects
from bluer_objects.metadata import get_from_object
from bluer_objects.storage.policies import DownloadPolicy
from bluer_algo.image_classifier.dataset.dataset import ImageClassifierDataset

from bluer_ugv import NAME
from bluer_ugv import env
from bluer_ugv.logger import logger

NAME = module.name(__file__, NAME)


def combine(
    object_name: str,
    count: int = -1,
    download: bool = True,
    log: bool = True,
    verbose: bool = False,
    recent: bool = True,
    sequence: int = -1,
    split: bool = True,
    test_ratio: float = 0.1,
    train_ratio: float = 0.8,
    explicit_dataset_object_names: str = "not-given",
) -> bool:
    eval_ratio = 1 - train_ratio - test_ratio
    if eval_ratio <= 0:
        logger.error(f"eval_ratio = {eval_ratio:.2f} <= 0")
        return False

    logger.info(
        "{}.combine({}{}{}{}) -{}{}> {}".format(
            NAME,
            "all" if count == -1 else f"count={count}",
            ",download" if download else "",
            ",recent" if recent else "",
            ",split" if recent else "",
            (
                "train={:.2f}/eval={:.2f}/test={:.2f}-".format(
                    train_ratio,
                    eval_ratio,
                    test_ratio,
                )
                if split
                else ""
            ),
            ("" if sequence == -1 else f"sequence={sequence}-"),
            object_name,
        )
    )

    if explicit_dataset_object_names != "not-given":
        list_of_dataset_object_names = explicit_dataset_object_names.split(",")
    else:
        logger.info("reading from  {} ...".format(env.BLUER_UGV_SWALLOW_DATASET_LIST))
        list_of_dataset_object_names: List[str] = get_from_object(
            object_name=env.BLUER_UGV_SWALLOW_DATASET_LIST,
            key="dataset-list",
            default=[],
            download=download,
        )

    if count != -1:
        if recent:
            list_of_dataset_object_names = list_of_dataset_object_names[-count:]
        else:
            list_of_dataset_object_names = list_of_dataset_object_names[:count]

    log_list(
        logger,
        "combining",
        list_of_dataset_object_names,
        "dataset(s)",
        itemize=True,
    )

    if download:
        for dataset_object_name in tqdm(list_of_dataset_object_names):
            logger.info(f"downloading {dataset_object_name} ...")
            if not storage.download(
                dataset_object_name,
                policy=DownloadPolicy.DOESNT_EXIST,
                log=verbose,
            ):
                return False

    success, list_of_datasets = ImageClassifierDataset.load_list(
        list_of_dataset_object_names,
        log=log,
    )
    if not success:
        return success

    if sequence != -1:
        for index in trange(len(list_of_datasets)):
            success, list_of_datasets[index] = list_of_datasets[index].sequence(
                length=sequence,
                object_name=objects.unique_object(
                    "{}-{}X".format(
                        list_of_datasets[index].object_name,
                        sequence,
                    ),
                ),
                log=log,
                verbose=verbose,
            )
            if not success:
                return success

    success, dataset = ImageClassifierDataset.combine(
        list_of_datasets,
        object_name=object_name,
        split=split,
        test_ratio=test_ratio,
        train_ratio=train_ratio,
    )
    if not success:
        return success

    return dataset.save(
        metadata={
            "contains": list_of_dataset_object_names,
        },
        log=True,
    )
