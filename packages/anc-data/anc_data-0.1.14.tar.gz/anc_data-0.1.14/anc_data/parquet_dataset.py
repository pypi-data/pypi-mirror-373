import copy
import multiprocessing.dummy as mt
import os

import pyarrow.dataset as ds
from pyarrow.fs import S3FileSystem
from pyarrow.parquet import ParquetFile


def get_inner_group_idx_from_row_idx(
    rows_accumulate, row_idx, curr_inner_group_idx, inner_group_num
):
    assert curr_inner_group_idx < inner_group_num
    if (
        rows_accumulate[curr_inner_group_idx]
        <= row_idx
        < rows_accumulate[curr_inner_group_idx + 1]
    ):
        return curr_inner_group_idx
    for i in range(inner_group_num):
        cur_gidx = (curr_inner_group_idx + i + 1) % inner_group_num
        if rows_accumulate[cur_gidx] <= row_idx < rows_accumulate[cur_gidx + 1]:
            return cur_gidx
    return -1


def get_actual_columns(parquet_file, file_system=None):
    dataset = ds.dataset(parquet_file, format="parquet", filesystem=file_system)
    return dataset.schema.names


def path_exists(path, file_system=None):
    if file_system is not None:
        # PyArrow S3FileSystem uses get_file_info() instead of exists()
        if hasattr(file_system, "get_file_info"):
            file_info = file_system.get_file_info(path)
            from pyarrow.fs import FileType

            return file_info.type != FileType.NotFound
    # TODO: for other storage, like s3, we need other methods to check if the path exists
    # for DDN, we use os.path.exists to check if the path exists
    return os.path.exists(path)


def process_filepath_columns(filepath, columns, file_system=None):
    if isinstance(filepath, str):
        # filepath is just one parquet file
        filepath = [filepath]
        if columns:
            # also add a layer to columns to match filepath
            columns = [columns]

    assert isinstance(
        filepath, list
    ), f"filepath should be a list but got {type(filepath)}"
    assert len(filepath) > 0
    # if filepath is a list of [meta, wav, ...], the first one is the main one and must exist
    # if filepath only contains one file, it must exist
    assert path_exists(filepath[0], file_system)

    if not columns:
        parquet_file = [
            ParquetFile(path, filesystem=file_system)
            for path in filepath
            if path_exists(path, file_system)
        ]
        columns = [None] * len(parquet_file)
        return parquet_file, columns

    assert len(columns) == len(
        filepath
    ), f"columns length {len(columns)} should be the same as the number of parquet files {len(filepath)}"

    valid_filepath = []
    valid_columns = []

    # filter out the columns if the parquet files are not exist
    for path, cols in zip(filepath, columns):
        if path_exists(path, file_system):
            valid_filepath.append(ParquetFile(path, filesystem=file_system))
            col_in_file = get_actual_columns(path, file_system)
            actual_columns = [col for col in cols if col in col_in_file]
            valid_columns.append(actual_columns)

    columns = valid_columns
    parquet_file = valid_filepath

    return parquet_file, columns


def create_pyarrow_s3fs(file_system_config):
    # TODO: test different block cache settings
    return S3FileSystem(
        access_key=file_system_config.get("access_key"),
        secret_key=file_system_config.get("secret_key"),
        endpoint_override=file_system_config.get("endpoint_override"),
    )


class ParquetDataset:
    r"""
    Given a path of parquet file, return target data by index
    Note: This class only implements an efficient way to return sample by index
        The index order is controlled by sampler, not here.

    Args:
        filepath (str or tuple of str): file from which to load the data. If is tuple of str, each
            each str represents a single parquet file, and corresponding rows across those files together
            form a sample
        columns (list of str, optional), columns to load (default: ``None`` means load all columns)
    """

    def __init__(self, filepath, columns=None, file_system_config=None):
        self.filepath = filepath
        self.file_system_config = file_system_config or {}
        self.file_system = None  # defaults to local
        fs_type = self.file_system_config.get("type")
        if fs_type:
            if fs_type != "pyarrow_s3":
                raise ValueError(f"Unsupported file system type: {fs_type}")
            self.file_system = create_pyarrow_s3fs(self.file_system_config)
        self.parquet_files, self.columns = process_filepath_columns(
            self.filepath, columns, self.file_system
        )
        self.num_row_groups = self.parquet_files[0].num_row_groups
        self.row_groups = list(range(self.num_row_groups))
        self.row_group_rows = [
            self.parquet_files[0].metadata.row_group(i).num_rows
            for i in self.row_groups
        ]

        self.row_group_rows_accumulate = []
        rows = 0
        for i in self.row_groups:
            self.row_group_rows_accumulate.append(rows)
            rows += self.row_group_rows[i]
        self.row_group_rows_accumulate.append(rows)
        self.cur_row_group = 0
        self.cache = {}

        self.num_rows = self.parquet_files[0].metadata.num_rows
        # ensure that the metadata of the group files is same
        for idx, pf in enumerate(self.parquet_files):
            assert self.num_row_groups == pf.num_row_groups, (
                f"parquet file {self.filepath[idx]} has {pf.num_row_groups} row groups but "
                "{self.filepath[0]} has {self.num_row_groups}"
            )
            assert self.row_group_rows == [
                pf.metadata.row_group(rid).num_rows for rid in self.row_groups
            ], f"parquet file {self.filepath[idx]} has different rows in row group than {self.filepath[0]}"

        if fs_type in ["pyarrow_s3"]:
            self.file_system = None
            self.parquet_files = []
            self.columns = columns

    # S3FileSystem is not fork-safe, initialize it again in the subprocess
    def __iter__init__(self):
        if self.file_system:
            return
        if (
            self.file_system_config
            and self.file_system_config.get("type") == "pyarrow_s3"
        ):
            self.file_system = create_pyarrow_s3fs(self.file_system_config)
            self.parquet_files, self.columns = process_filepath_columns(
                self.filepath, self.columns, self.file_system
            )

    def _read_row_group(self, row_group):
        rows = []
        for idx, pf in enumerate(self.parquet_files):
            row_group_data = pf.read_row_group(row_group, columns=self.columns[idx])
            group_data = row_group_data.to_pandas()
            cur_rows = group_data.to_dict("records")
            if len(rows) == 0:
                rows = cur_rows
            else:
                assert len(rows) == len(
                    cur_rows
                ), "row group of each file should be the same"
                for i in range(len(rows)):
                    rows[i].update(cur_rows[i])
        return rows

    def __iter__(self):
        self.__iter__init__()
        for row_group in self.row_groups:
            rows = self._read_row_group(row_group)
            yield from rows

    def _clean_cache(self):
        # TODO: maybe a better way to find out which row groups to delete
        gidx_to_delete = [i for i in self.cache]
        for i in gidx_to_delete:
            del self.cache[i]

    def __getitem__(self, idx):
        self.__iter__init__()
        assert (
            0 <= idx < self.num_rows
        ), f"idx shoud be in [0, {self.num_rows}) but get {idx}"
        cur_row_group = get_inner_group_idx_from_row_idx(
            self.row_group_rows_accumulate, idx, self.cur_row_group, self.num_row_groups
        )
        assert cur_row_group >= 0, f"invalid row group {cur_row_group} for idx {idx}"
        self.cur_row_group = cur_row_group
        if cur_row_group not in self.cache:
            cur_rows = self._read_row_group(cur_row_group)
            self._clean_cache()
            self.cache[cur_row_group] = cur_rows
        else:
            cur_rows = self.cache[cur_row_group]
        sample = cur_rows[idx - self.row_group_rows_accumulate[cur_row_group]]
        if "row_idx" not in sample:
            sample["row_idx"] = idx
        return copy.deepcopy(sample)

    def __len__(self):
        return self.num_rows

    def close(self):
        del self.cache
        for pf in self.parquet_files:
            pf.close()

    def get_sub_lengths(self):
        return self.row_group_rows


class ParquetConcateDataset:
    r"""
    Given multiple parquet files as a whole dataset, return target data by index
    Note: This class only implements an efficient way to return sample by index.
        The index order is controlled by sampler, not here.

    Args:
        filepaths (list of str): files from which to load the data.
        columns (list of str, optional), columns to load (default: ``None`` means load all columns)
    """

    def __init__(self, filepaths, columns=None, file_system_config=None):
        self.filepaths = filepaths
        self.num_files = len(filepaths)
        self.columns = columns
        rows = []
        rows_per_group = []
        self.file_system_config = file_system_config
        with mt.Pool(16) as p:
            sub_ds_info = p.map(self._get_sub_ds_length, self.filepaths)
        rows = [i[0] for i in sub_ds_info]
        rows_per_group = [i[1] for i in sub_ds_info]
        self.rows_per_file = rows
        self.rows_per_group = rows_per_group
        self.num_rows = sum(self.rows_per_file)
        self.num_rows_accumulate = []
        cur_rows = 0
        for i in range(self.num_files):
            self.num_rows_accumulate.append(cur_rows)
            cur_rows += rows[i]
        self.num_rows_accumulate.append(cur_rows)
        self.cur_ds_idx = 0
        self.cache = {}

    def _get_sub_ds_length(self, path):
        ds = ParquetDataset(path, file_system_config=self.file_system_config)
        row = len(ds)
        row_groups = ds.get_sub_lengths()
        ds.close()
        return row, row_groups

    def __len__(self):
        return self.num_rows

    def _clean_cache(self):
        ds_idx_to_delete = [i for i in self.cache]
        for i in ds_idx_to_delete:
            self.cache[i].close()
            del self.cache[i]

    def __getitem__(self, idx):
        if idx < 0:
            idx += len(self)
        assert 0 <= idx < len(self), f"idx should be in [0, {len(self)}) but get {idx}"
        cur_ds_idx = get_inner_group_idx_from_row_idx(
            self.num_rows_accumulate, idx, self.cur_ds_idx, self.num_files
        )
        assert cur_ds_idx >= 0, f"invalid file idx {cur_ds_idx} for row idx {idx}"
        self.cur_ds_idx = cur_ds_idx
        if cur_ds_idx not in self.cache:
            cur_ds = ParquetDataset(
                self.filepaths[cur_ds_idx], self.columns, self.file_system_config
            )
            self._clean_cache()
            self.cache[cur_ds_idx] = cur_ds
        else:
            cur_ds = self.cache[cur_ds_idx]
        data = cur_ds[idx - self.num_rows_accumulate[cur_ds_idx]]
        if "filepath" not in data:
            data["filepath"] = self.filepaths[cur_ds_idx]
        return data

    def get_sub_lengths(self, level="row_group"):
        assert level in {"row_group", "file"}
        if level == "row_group":
            return self.rows_per_group
        else:
            return self.rows_per_file


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
    dataset = ParquetConcateDataset(files)
    assert [sum(i) for i in dataset.rows_per_group] == dataset.rows_per_file
    assert sum(dataset.rows_per_file) == len(dataset)
    for i in range(10):
        data = dataset[i * 500]
        print(data["filepath"])
