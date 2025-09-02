import logging
from pathlib import Path
from typing import Optional, Union

import datasets
from datasets import get_dataset_config_names, load_dataset
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, PreTrainedTokenizer

logger = logging.getLogger(__name__)


def create_data_loader(
    tokenizer: Union[str, PreTrainedTokenizer],
    dataset_name_or_path: Union[str, Path],
    *,
    dataset_config_name: Optional[str] = None,
    dataset_split: Optional[str] = None,
    dataset_field: Optional[str] = None,
    batch_size: int = 1,
    num_samples: int = 64,
    max_sample_length: int = 512,
    seed: int = 42,
    **kwargs,
) -> DataLoader:
    """
    Create a DataLoader for the given dataset and tokenizer.

    Args:
        tokenizer: A tokenizer or a model name for the tokenizer.
        dataset_name_or_path: A dataset name or path.
        dataset_config_name: A dataset config name. If None, the last dataset config name is used.
        dataset_split: A dataset split. If None, the test split is used.
        dataset_field: A dataset field. If None, the first column is used.
        batch_size: A batch size (default: 1).
        num_samples: A number of samples (default: 1).
        max_sample_length: A maximum sample length (default: 512).
        seed: A random seed (default: 42).
        **kwargs: Additional keyword arguments.

    Returns:
        DataLoader: A DataLoader for the given dataset and tokenizer
    """
    if isinstance(tokenizer, str):
        tokenizer = AutoTokenizer.from_pretrained(tokenizer)

    if tokenizer.pad_token is None:
        if tokenizer.eos_token is not None:
            tokenizer.pad_token = tokenizer.eos_token
        else:
            raise ValueError(
                "We do not support padding_to_max_length feature for current tokenizer. "
            )

    if dataset_config_name is None:
        dataset_config_name = get_dataset_config_names(dataset_name_or_path)[-1]
        logger.info(f"Using dataset config {dataset_config_name} for {dataset_name_or_path}")

    dataset = load_dataset(dataset_name_or_path, dataset_config_name, **kwargs)

    if dataset_split is None:
        dataset_split = datasets.Split.TEST
    if dataset_split not in dataset.keys():
        raise ValueError(
            f"Dataset {dataset_name_or_path} does not have {dataset_split} split. Please specify 'dataset_split'."
        )
    data_split = dataset[dataset_split]
    data_split = data_split.shuffle(seed=seed)

    if dataset_field is None:
        # FIXME: The first column is a dataset field according to observations.
        #  Please check if this is always the case.
        dataset_field = data_split.column_names[0]
        logger.info(
            f"Using {dataset_field} as dataset field. To use another field, please specify 'dataset_field'."
        )

    input_ids_list = []
    n_run = 0
    for data_item in data_split[dataset_field]:
        data_item = data_item.strip()

        input_ids = tokenizer.encode(
            data_item,
            truncation=True,
            padding="max_length",
            max_length=max_sample_length,
            return_tensors="pt",
        )
        # Make sure the input_ids has the max_sample_length with padding
        assert input_ids.shape[1] == max_sample_length

        if input_ids.numel() == 0:
            continue
        input_ids_list.append(input_ids)
        n_run += 1
        if n_run == num_samples:
            break

    # To truncate the input_ids_list to the multiple of batch_size
    max_num_batch = len(input_ids_list) - len(input_ids_list) % batch_size

    forward_inputs = []
    for data in input_ids_list[:max_num_batch]:
        forward_inputs.append(
            {
                'input_ids': data[0],
                'attention_mask': torch.ones(
                    (max_sample_length), dtype=torch.bool, device=data[0].device
                ),
            }
        )

    return DataLoader(forward_inputs, batch_size=batch_size)  # type: ignore
