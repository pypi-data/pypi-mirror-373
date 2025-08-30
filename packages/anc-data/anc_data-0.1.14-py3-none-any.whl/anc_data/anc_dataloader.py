import copy
import datetime
import logging
import multiprocessing as mp
import os
import time
from collections import defaultdict

from torch.utils.data import DataLoader

from anc_data.anc_dataset import AncDataset
from anc_data.anc_processor import AncProcessor
from anc_data.anc_sampler import AncMultiSourceSampler, AncSampler
from anc_data.utils import DataNotReady


def fake_collate(x):
    return x


def safe_qsize(queue):
    """Safely get queue size, handling NotImplementedError on macOS"""
    try:
        return queue.qsize()
    except NotImplementedError:
        # On macOS, qsize() is not implemented, so we return a default value
        # that won't affect the logging logic significantly
        return 0


class AncDataLoader:
    r"""
    A wrapper for dataloader, dataset and sampler
    It makes the handling of the data gathering logic in each subprocess easier
    It also helps handle the checkpoint load and resume logic

    Args:
        paths (list of str): files from which to load the data.
        batch_size (int): how many samples per batch to load.
        num_workers (int): how many subprocesses to use for data
            loading. ``0`` means that the data will be loaded in the main process.
        rank (int, optional): data parallel rank of current process (default: ``0``).
        world (int, optional): data parallel world size (default: ``1``).
        processor (Processor, optional): object that defines the data transform and batch transform
            logic (default ``AncProcessor`` instance which just return the input as is for both
            transform and batch transform).
        data_type (str, optional): the type of dataset that the paths represents (default ``parquet``).
        shuffle (bool, optional): set to ``True`` to have the data reshuffled
            at every epoch (default: ``False``).
        drop_last (bool, optional): set to ``True`` to drop the last incomplete batch,
            if the dataset size is not divisible by the batch size. If ``False`` and
            the size of dataset is not divisible by the batch size, then the last batch
            will be smaller. (default: ``False``).
        seed (int, optional): seed for randomness (default: ``0``).
        pin_memory (bool, optional): If ``True``, the data loader will copy Tensors
            into device/CUDA pinned memory before returning them.  If your data elements
            are a custom type, or your :attr:`collate_fn` returns a batch that is a custom type,
            see the example below.
        ds_args (dict, optional): dataset arguments for data loading, such as the columns to load
            for parquet files, etc (default ``{}``).
        repeat (bool, optional): If ``True``, data would be loaded repeatedly
        prefetch_factor (int, optional): the prefetch_factor for torch dataloader
    """

    def __init__(
        self,
        paths,
        batch_size,
        num_workers,
        rank=0,
        world=1,
        processor=AncProcessor(),
        data_type="parquet",
        shuffle=False,
        drop_last=False,
        seed=0,
        pin_memory=True,
        ds_args={},
        repeat=False,
        prefetch_factor=2,
        enable_compose=False,
        global_shuffle=False,
        max_steps=-1,
        enable_logging=True,
        ckpt_interval=None,
        ds_ratios=[1],
        chunk_granularity=-1,
        sampler_use_mem_save_mode=False,
        persistent_workers=False,
        use_spawn=False,
        always_return_first_batch=False,
    ):
        # TODO: add support to get rank and world from torch env
        self.paths = paths
        self.batch_size = batch_size
        self.num_workers = num_workers
        if num_workers > 0:
            if use_spawn:
                ctx = mp.get_context("spawn")
                self.ds_state_queues = [ctx.Queue() for _ in range(num_workers)]
            else:
                self.ds_state_queues = [mp.Queue() for _ in range(num_workers)]
        else:
            self.ds_state_queues = [mp.Queue()]
        if int(os.getenv("ANC_DISABLE_LOGGING", "0")) == 1:
            enable_logging = False
        ds_ckpt_interval = ckpt_interval
        if num_workers > 0:
            if ckpt_interval is not None:
                assert (
                    ckpt_interval % num_workers == 0
                ), "ckpt_interval must be divisible by num_workers"
            ds_ckpt_interval = (
                ckpt_interval // num_workers if ckpt_interval is not None else None
            )
        self.dataset = AncDataset(
            paths,
            processor=processor,
            dataset_type=data_type,
            ds_args=ds_args,
            enable_compose=enable_compose,
            enable_logging=enable_logging,
            state_queues=self.ds_state_queues,
            ckpt_interval=ds_ckpt_interval,
        )
        if len(ds_ratios) > 1:
            assert isinstance(
                self.paths[0], list
            ), "paths must be a list of lists under multisource mode"
            assert len(self.paths) == len(
                ds_ratios
            ), "length of paths and ds_ratios must be the same under multisource mode"
            assert repeat is True, "repeat must be true under multisource mode"
            self.sampler = AncMultiSourceSampler(
                dataset=self.dataset,
                ratios=ds_ratios,
                batch_size=batch_size,
                world=world,
                rank=rank,
                num_workers=num_workers,
                shuffle=shuffle,
                seed=seed,
                drop_last=drop_last,
                repeat=repeat,
                global_shuffle=global_shuffle,
                chunk_granularity=chunk_granularity,
                mem_save_mode=sampler_use_mem_save_mode,
            )
        else:
            self.sampler = AncSampler(
                dataset=self.dataset,
                batch_size=batch_size,
                world=world,
                rank=rank,
                num_workers=num_workers,
                shuffle=shuffle,
                seed=seed,
                drop_last=drop_last,
                repeat=repeat,
                global_shuffle=global_shuffle,
                chunk_granularity=chunk_granularity,
                mem_save_mode=sampler_use_mem_save_mode,
                max_samples=ds_args.get("max_samples"),
            )
        self.dataset.set_sampler(self.sampler)
        self.loader = DataLoader(
            self.dataset,
            num_workers=num_workers,
            pin_memory=pin_memory,
            collate_fn=fake_collate,
            prefetch_factor=prefetch_factor,
            persistent_workers=persistent_workers,
            multiprocessing_context=mp.get_context("spawn") if use_spawn else None,
        )
        self.step = 0
        self.rank = rank
        self.world = world
        self.loader_iter = None
        self.buffer = [[] for _ in range(num_workers)]
        self.last_wid = -1
        self.out_of_data_worker = set()
        self.max_steps = max_steps
        self.logging = enable_logging
        self.ckpt_interval = ckpt_interval
        self.last_ckpt = (
            {}
        )  # nemo may call get_checkpoint multiple times for the same step
        self.always_return_first_batch = always_return_first_batch
        self.first_batch = None
        # with multi val dataloader, we may get _loader_idx as _ds_idx in data, so use a dict instead of a list here
        self.ds_read_counts = defaultdict(int)

    def __iter__(self):
        logging.debug(f"pid {os.getpid()} rank {self.rank} in iter")
        self.loader_iter = iter(self.loader)
        self.out_of_data_worker = set()
        return self

    def __len__(self):
        if self.max_steps > 0:
            # maybe need to check if max_steps is less than length of sampler, or repeat is set
            return self.max_steps
        return len(self.sampler)

    def _get_next_wid(self, cur_wid):
        for i in range(self.num_workers):
            cur_wid = (cur_wid + 1) % self.num_workers
            if cur_wid not in self.out_of_data_worker:
                break
        return cur_wid

    def _empty_buffer(self):
        logging.info(
            f"All workers stop, try to get data from buffer, buffer size {sum([len(i) for i in self.buffer])}"
        )
        for i in range(self.num_workers):
            if len(self.buffer[i]) > 0:
                data = self.buffer[i].pop()
                return data
        return None

    def __next__(self):
        if self.always_return_first_batch and self.first_batch is not None:
            return self.first_batch
        now = datetime.datetime.now()
        need_logging = safe_qsize(self.loader_iter._data_queue) < self.num_workers
        t1 = time.time()
        data = None
        if len(self.out_of_data_worker) == self.num_workers:
            # TODO: better handle the exception
            data = self._empty_buffer()
            if data is None:
                raise StopIteration
        # decide which subprocess to get data from
        if self.last_wid < 0:
            cur_wid = self.step % self.num_workers
        else:
            cur_wid = (self.last_wid + 1) % self.num_workers
        if cur_wid in self.out_of_data_worker:
            cur_wid = self._get_next_wid(cur_wid)
        if data is None and len(self.buffer[cur_wid]) > 0:
            data = self.buffer[cur_wid].pop()
        elif data is None:
            cnt = 0
            while True:
                item = next(self.loader_iter)
                # since we set batch size=1 for torch dataloader,
                # the actual batch size is handled by sampler
                # we need to use index 0 to get data out
                # note: cur_data here should be a list of batch data
                cur_data_wid, cur_data, is_last_batch = item[0]
                if is_last_batch:
                    self.out_of_data_worker.add(cur_data_wid)
                    if len(self.out_of_data_worker) == self.num_workers:
                        data = self._empty_buffer()
                        if data is None:
                            raise StopIteration
                        break
                if isinstance(cur_data, DataNotReady):
                    logging.info(
                        f"next call get DataNotReady from {cur_data_wid}, is last batch {is_last_batch}"
                    )
                    if is_last_batch:
                        cur_wid = self._get_next_wid(cur_wid)
                    continue
                assert isinstance(cur_data, list)
                if cur_data_wid == cur_wid:
                    data = cur_data[0]
                    self.buffer[cur_data_wid] += cur_data[1:]
                    break
                else:
                    # store the out of order data
                    self.buffer[cur_data_wid] += cur_data
                cnt += 1
                if cnt % self.num_workers == 0:
                    logging.warning(
                        f"{self.rank} Too many loop ({cnt} times) when getting next data"
                        " for worker {cur_wid} of step {self.step}"
                    )
        self.step += 1
        self.last_wid = cur_wid
        consumed_time = time.time() - t1
        need_logging = self.logging and (need_logging or consumed_time > 0.01)
        if need_logging:
            logging.debug(
                f"__next__ called time {now} pid {os.getpid()} rank {self.rank} return step {self.step}"
                " consumed time {consumed_time} data with buffer {safe_qsize(self.loader_iter._data_queue)}"
            )
        if self.always_return_first_batch and self.first_batch is None:
            self.first_batch = data

        if "_ds_idx" in data:
            for idx in data["_ds_idx"]:
                self.ds_read_counts[idx] += 1
        return data

    def get_checkpoint(self):
        if self.step in self.last_ckpt:
            return self.last_ckpt[self.step]
        step_to_del = []
        for i in self.last_ckpt:
            if i < self.step:
                step_to_del.append(i)
        for i in step_to_del:
            del self.last_ckpt[i]
        if self.step % self.ckpt_interval != 0:
            logging.warning(
                f"Step {self.step} cannot be divided by ckpt_interval {self.ckpt_interval}, loader ckpt state"
                " will return an empty dict"
            )
            return {}
        ds_states = []
        for i in range(self.num_workers):
            ds_states.append(self.ds_state_queues[i].get())
        ckpt = self.__getstate__()
        ckpt["ds_states"] = ds_states
        self.last_ckpt[self.step] = ckpt
        return ckpt

    def set_checkpoint(self, ckpt):
        ds_states = ckpt.pop("ds_states")
        self.dataset.set_ds_states(ds_states)
        self.__setstate__(ckpt)

    def __getstate__(self):
        state = {}
        state["paths"] = self.paths
        state["batch_size"] = self.batch_size
        state["num_workers"] = self.num_workers
        state["last_wid"] = self.last_wid
        state["out_of_data_worker"] = copy.deepcopy(self.out_of_data_worker)
        state["step"] = self.step
        state["ds_read_counts"] = copy.deepcopy(self.ds_read_counts)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


if __name__ == "__main__":
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
    loader = AncDataLoader(files, 1024, num_workers=4)
    for data in loader:
        print(len(data))
