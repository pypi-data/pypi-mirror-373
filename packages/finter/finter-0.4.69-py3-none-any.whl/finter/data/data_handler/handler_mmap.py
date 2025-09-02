import fcntl
import mmap
import os
import pickle
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd


class MmapMemoryManager:
    def __init__(self, mmap_dir=None):
        if mmap_dir is None:
            self.mmap_dir = Path.home() / ".mmap_memory"
        else:
            self.mmap_dir = Path(mmap_dir)
        self.mmap_dir.mkdir(parents=True, exist_ok=True)

    def _get_mmap_path(self, name: str) -> Path:
        return self.mmap_dir / f"{name}.mmap"

    @contextmanager
    def _file_lock(self, lock_path: Path):
        lock_file = open(lock_path, "w")
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
            lock_file.close()

    def set(self, name: str, df: pd.DataFrame) -> None:
        mmap_path = self._get_mmap_path(name)
        lock_path = mmap_path.with_suffix(".lock")
        metadata_path = mmap_path.with_suffix(".meta")

        with self._file_lock(lock_path):
            if mmap_path.exists():
                os.remove(mmap_path)
            if metadata_path.exists():
                os.remove(metadata_path)

            data = df.values
            with open(mmap_path, "wb") as f:
                f.write(b"\x00" * data.nbytes)

            with open(mmap_path, "r+b") as f:
                mmap_obj = mmap.mmap(
                    f.fileno(), length=data.nbytes, access=mmap.ACCESS_WRITE
                )
                shared_array = np.ndarray(data.shape, dtype=data.dtype, buffer=mmap_obj)
                np.copyto(shared_array, data)
                mmap_obj.flush()
                mmap_obj.close()

            metadata = pickle.dumps((df.index, df.columns, data.shape, data.dtype))
            with open(metadata_path, "wb") as f:
                f.write(metadata)

    def get(self, name: str) -> pd.DataFrame:
        mmap_path = self._get_mmap_path(name)
        lock_path = mmap_path.with_suffix(".lock")

        if not mmap_path.exists() or not mmap_path.with_suffix(".meta").exists():
            # raise FileNotFoundError(f"Data or metadata for '{name}' not found.")
            return pd.DataFrame()


        with self._file_lock(lock_path):
            metadata_path = mmap_path.with_suffix(".meta")
            with open(metadata_path, "rb") as f:
                index, columns, shape, dtype = pickle.load(f)

            with open(mmap_path, "r+b") as f:
                mmap_obj = mmap.mmap(
                    f.fileno(),
                    length=os.path.getsize(mmap_path),
                    access=mmap.ACCESS_READ,
                )
                shared_array = np.ndarray(shape, dtype=dtype, buffer=mmap_obj)
                data = shared_array.copy()
                mmap_obj.close()

            return pd.DataFrame(data, index=index, columns=columns)

    def delete(self, name: str) -> None:
        mmap_path = self._get_mmap_path(name)
        metadata_path = mmap_path.with_suffix(".meta")
        lock_path = mmap_path.with_suffix(".lock")

        with self._file_lock(lock_path):
            if mmap_path.exists():
                os.remove(mmap_path)
            if metadata_path.exists():
                os.remove(metadata_path)
