import copy
import itertools
import logging

import torch
from torch.utils.data import IterableDataset

from anc_data.anc_composer import AncComposer
from anc_data.anc_processor import Processor
from anc_data.anc_sampler import AncSampler
from anc_data.jsonl_dataset import JsonlDataset
from anc_data.parquet_dataset import ParquetConcateDataset
from anc_data.utils import DataNotReady, EndOfIteration


def assert_2_layer_list(x):
    assert isinstance(x, list) and all(isinstance(i, list) for i in x), (
        "For parquet, AncDataset's filepaths should be a 2-layer list: list of datasets (ParquetConcateDataset) -> "
        "list of ParquetDataset. ParquetDataset accepts both a single str filepath and a list of filepaths for cases "
        "including correlated files such as wav"
    )


class AncDataset(IterableDataset):
    r"""
    A class defines the pipeline of data loading and data transform

    Args:
        filepaths (list of str): files from which to load the data.
        processor (Processor): object that defines the data transform and batch transform logic.
        sampler: object that control the data loader order
        dataset_type (str, optional): the type of dataset that the paths represents (default ``parquet``).
        ds_args (dict, optional): dataset arguments for data loading, such as the columns to load
            for parquet files, etc (default ``{}``).
        repeat (bool, optional): if set to True, the data will be loaded repeatedly
    """

    def __init__(
        self,
        filepaths,
        processor: Processor,
        sampler=None,
        dataset_type="parquet",
        ds_args={},
        enable_compose=False,
        enable_logging=True,
        state_queues=None,
        ckpt_interval=None,
    ):
        assert isinstance(
            processor, Processor
        ), "processor must be an anc_processor.Processor"
        self.filepaths = filepaths
        self.dataset_type = dataset_type
        processor.ds_args = ds_args
        # TODO: support more types of dataset
        decode_fn = processor.decode_fn if hasattr(processor, "decode_fn") else None
        if dataset_type == "parquet":
            assert_2_layer_list(filepaths)
            # each filepath represents a dataset
            self.ds = [
                ParquetConcateDataset(
                    filepath,
                    columns=ds_args.get("columns"),
                    file_system_config=ds_args.get("file_system"),
                )
                for filepath in filepaths
            ]
        elif dataset_type == "jsonl":
            assert isinstance(
                filepaths[0], str
            ), "jsonl dataset does not support multisources"
            assert len(filepaths) == 1, (
                f"jsonl dataset only support single file, but got {len(filepaths)}. "
                "Please convert jsonl dataset to parquet first"
            )
            # TODO: support file_system for jsonl dataset
            self.ds = [JsonlDataset(filepaths[0], decode_fn=decode_fn)]
        self.processor = processor
        self.sampler = sampler
        self.enable_compose = enable_compose
        self.processor.enable_compose = enable_compose
        self.composer = None
        if self.enable_compose:
            assert hasattr(processor, "get_token_length_fn")
            assert hasattr(processor, "max_seq_len")
            split_config = None
            split_fn = None
            if getattr(processor, "seq_split_config", None) is not None:
                assert hasattr(processor, "split_fn")
                split_config = processor.seq_split_config
                split_fn = processor.split_fn
            self.composer = AncComposer(
                max_seq_len=processor.max_seq_len,
                get_token_length_fn=processor.get_token_length_fn,
                seq_split_config=split_config,
                split_fn=split_fn,
                enable_logging=enable_logging,
            )
        self.enable_logging = enable_logging
        self.cur_step = 0
        self.state_queues = state_queues
        self.ckpt_interval = ckpt_interval
        self.ds_states = None
        self.remain_data = []
        self.raw_data = []

    def set_sampler(self, sampler):
        self.sampler = sampler

    def __iter__(self):
        worker_info = torch.utils.data.get_worker_info()
        wid = worker_info.id if worker_info is not None else 0
        num_workers = worker_info.num_workers if worker_info is not None else 1
        if self.ds_states is not None:
            self._set_ckpt(self.ds_states[wid])
        logging.debug(
            f"iter information: len(sampler) - {len(self.sampler)}, worker id - {wid}, num_workers - {num_workers}"
        )
        # use islice to get the iterator of sampler only for current worker
        sampler_iter = itertools.islice(
            iter(self.sampler), wid, len(self.sampler), num_workers
        )
        yield from self.get_generator(sampler_iter, wid, num_workers)

    def get_generator(self, sampler_iter, wid, num_workers):
        while True:
            indices = next(sampler_iter, EndOfIteration)
            if indices is EndOfIteration:
                logging.warning(
                    f"worker {wid} of {num_workers} get EndOfIteration from sampler, return DataNotReady"
                )
                yield (wid, DataNotReady(), True)
                break
            item_generator = self._getitem(indices)
            is_last = False
            while True:
                result = next(item_generator, EndOfIteration)
                if result is EndOfIteration:
                    if is_last:
                        yield (wid, DataNotReady(), True)
                    break
                next_data, is_last = result
                if isinstance(next_data, DataNotReady):
                    continue

                yield (wid, [next_data], False)
                self.cur_step += 1
                if (
                    self.ckpt_interval is not None
                    and self.cur_step % self.ckpt_interval == 0
                ):
                    if self.state_queues is not None:
                        self.state_queues[wid].put(self._get_ckpt())
            if is_last:
                break

    def _getitem(self, idxs):
        if len(idxs) == 2:
            idxs, is_last_batch = idxs
            ds_idx = 0
        else:
            ds_idx, idxs, is_last_batch = idxs
        if isinstance(idxs, int):
            idxs = [idxs]
        if len(idxs) == 0:
            yield (DataNotReady(), is_last_batch)
            return
        raw_data = self.remain_data + [self.ds[ds_idx][idx] for idx in idxs]
        self.remain_data = []
        if self.processor.transform:
            processed_data = []
            for data_idx, data in enumerate(raw_data):
                self.raw_data = raw_data[data_idx + 1 :]
                is_last_sample = is_last_batch and data_idx == len(raw_data) - 1
                if isinstance(data, dict) and "_ds_idx" not in data:
                    # TODO: create a reserved key list for "data", add _ds_idx and filepath to the list
                    data["_ds_idx"] = ds_idx
                processed = self.processor.transform(data, is_last_sample)
                if self.enable_compose:
                    processed = self.composer(processed, is_last_sample)
                if processed is None and not is_last_sample:
                    continue
                if isinstance(processed, list):
                    processed_data += processed
                else:
                    if processed is None:
                        processed = []
                    # processed_data is a generator
                    if self.processor.batch_transform:
                        # batch_processed is a generator too
                        batch_processed = self.processor.batch_transform(
                            processed, is_last_sample
                        )
                        if batch_processed is not None:
                            for batch in batch_processed:
                                yield (batch, is_last_sample)
        else:
            processed_data = raw_data
        if processed_data and self.processor.batch_transform:
            batch_processed = self.processor.batch_transform(
                processed_data, is_last_batch
            )
            if batch_processed is None:
                batch_processed = []
        else:
            batch_processed = []
        assert isinstance(batch_processed, list)
        for batch in batch_processed:
            yield (batch, is_last_batch)

    def _get_ckpt(self):
        state = {}
        # it's possible that the sampler or composer is not initialized
        if self.sampler is not None:
            state["sampler"] = self.sampler._get_ckpt()
        if self.enable_compose:
            state["composer"] = self.composer._get_ckpt()
        state["cur_step"] = self.cur_step
        state["remain_data"] = self.raw_data
        # return a deep copied state to avoid it being modified
        return copy.deepcopy(state)

    def _set_ckpt(self, state):
        if "sampler" in state and self.sampler is not None:
            sampler_state = state.pop("sampler")
            self.sampler._set_ckpt(sampler_state)
        if "composer" in state and self.enable_compose:
            composer_state = state.pop("composer")
            self.composer._set_ckpt(composer_state)
        self.__dict__.update(state)

    def __len__(self):
        return len(self.ds)

    def num_rows_per_ds(self):
        return [len(ds) for ds in self.ds]

    def get_sub_lengths(self, idx=0):
        if self.dataset_type == "parquet":
            level = "row_group"
        else:
            level = "file"
        return self.ds[idx].get_sub_lengths(level)

    def set_ds_states(self, ds_states):
        self.ds_states = ds_states


if __name__ == "__main__":
    from anc_data.anc_processor import AncProcessor

    folder = "/mnt/personal/parquet_demo_data"
    fnames = [
        "01_0001.parquet",
        "02_0001.parquet",
        "03_0001.parquet",
        "04_0001.parquet",
        "05_0001.parquet",
        "06_0001.parquet",
        "07_0001.parquet",
    ]
    files = [f"{folder}/{fname}" for fname in fnames]
    ds = AncDataset(files, AncProcessor())
    sampler = AncSampler(ds, 1)
    ds.set_sampler(sampler)
    assert sum([sum(i) for i in ds.get_sub_lengths()]) == len(ds)
    ds_iter = iter(ds)
    for i in range(10):
        wid, data, is_last_batch = next(ds_iter)
        print(data[0][0]["filepath"])
