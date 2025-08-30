import json
import os
import random
from typing import Callable, Dict, Iterator, Any
from typing import List, Mapping, MutableMapping, Optional, Sequence, Union

import pandas as pd
from loguru import logger

# Keep your original import; assumed available alongside this module.
from .example import Example


PathLike = Union[str, os.PathLike]
RowLike = Union[Mapping[str, Any], MutableMapping[str, Any]]
RowsLike = Sequence[Union[RowLike, Example]]


class AttackDataset:
    """
    A lightweight dataset wrapper that builds a list of `Example` objects from:
      1) In-memory rows (list of dicts or Example instances), or
      2) Local files (json, jsonl, csv, xlsx, parquet), or
      3) A special-cased 'thu-coai/AISafetyLab_Datasets/...' path that maps to a local directory.

    Parameters
    ----------
    path : Union[str, list]
        - If a list: treated as in-memory rows of dicts/Examples.
        - If a string path: treated as a local file path, or a special
          'thu-coai/AISafetyLab_Datasets/...' dataset selector.
    subset_slice : Optional[Union[int, slice, Sequence[int]]]
        - Optional subset to take from the loaded data.
          * int -> first N items
          * slice -> standard Python slice
          * list/tuple of 1-3 ints -> interpreted as slice(*subset_slice)
          * any other object supporting slicing -> passed as-is (e.g., np.s_[:10])
    local_data_dir : Optional[PathLike]
        - Base directory used when `path` contains 'thu-coai/AISafetyLab_Datasets'.
        - If not provided, will try env var 'AISAFETYLAB_DATASETS_DIR'.

    Raises
    ------
    FileNotFoundError
        If a required local file cannot be found.
    NotImplementedError
        If `path` is neither a supported local file nor a supported dataset selector.
    ValueError
        If in-memory rows are not a sequence of dict/Example.
    """

    def __init__(
        self,
        path: Union[PathLike, RowsLike],
        subset_slice: Optional[Union[int, slice, Sequence[int], Any]] = None,
        local_data_dir: Optional[PathLike] = None,
    ) -> None:
        self.data: List[Example] = []

        if isinstance(path, list):
            # In-memory rows
            self.data = self._from_sequence(path)

        elif isinstance(path, (str, os.PathLike)):
            path_str = str(path)

            if os.path.exists(path_str):
                # Local filesystem path
                self.data = self._from_local_file(path_str)

            elif "thu-coai/AISafetyLab_Datasets" in path_str:
                # Special-cased dataset mapping to a local directory
                self.data = self._from_thu_coai_local(path_str, local_data_dir)

            else:
                # Not a local path and not our supported dataset selector
                logger.error(
                    "Unsupported path. Only local files or 'thu-coai/AISafetyLab_Datasets' paths are supported."
                )
                raise NotImplementedError(
                    "Please provide a valid local file path (json, jsonl, csv, xlsx, parquet) "
                    "or a path containing 'thu-coai/AISafetyLab_Datasets/...'. "
                    "Open an issue if you need other Hugging Face datasets."
                )
        else:
            raise ValueError(
                "Parameter 'path' must be either a list of rows/Examples or a filesystem path string."
            )

        # Apply optional subsetting (after data is fully loaded)
        if subset_slice is not None:
            self._apply_subset(subset_slice)

    # -------------------------------------------------------------------------
    # Core helpers
    # -------------------------------------------------------------------------

    def _from_sequence(self, rows: RowsLike) -> List[Example]:
        """Convert a sequence of rows or Example objects into a list[Example]."""
        if not isinstance(rows, Sequence):
            raise ValueError("Expected a sequence for in-memory rows.")

        examples: List[Example] = []
        for i, r in enumerate(rows):
            if isinstance(r, Example):
                examples.append(r)
            elif isinstance(r, Mapping):
                examples.append(Example(**r))
            else:
                raise ValueError(
                    f"Row at index {i} is neither an Example nor a mapping. Got type: {type(r)!r}"
                )
        return examples

    def _from_local_file(self, file_path: str) -> List[Example]:
        """Load supported local file types and convert rows to Example objects."""
        file_path = os.path.abspath(file_path)
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if isinstance(payload, list):
                rows = payload
            elif isinstance(payload, dict):
                # If you have a dict with a top-level key (e.g., {"data": [...]})
                # adapt this block to your schema as needed.
                rows = payload.get("data", [])
            else:
                raise ValueError("Unsupported JSON payload shape.")
            return [Example(**d) for d in rows]

        if ext == ".jsonl":
            # Each line is a JSON object
            rows = pd.read_json(file_path, lines=True).to_dict("records")
            return [Example(**d) for d in rows]

        if ext == ".csv":
            rows = pd.read_csv(file_path).to_dict("records")
            return [Example(**d) for d in rows]

        if ext == ".xlsx":
            rows = pd.read_excel(file_path).to_dict("records")
            return [Example(**d) for d in rows]

        if ext == ".parquet":
            rows = pd.read_parquet(file_path).to_dict("records")
            return [Example(**d) for d in rows]

        raise NotImplementedError(
            f"Unsupported file extension: {ext}. "
            "Supported: .json, .jsonl, .csv, .xlsx, .parquet"
        )

    def _from_thu_coai_local(
        self,
        selector: str,
        local_data_dir: Optional[PathLike] = None,
    ) -> List[Example]:
        """
        Map a path containing 'thu-coai/AISafetyLab_Datasets/...' to a local directory
        and load a corresponding JSON/JSONL/CSV/XLSX/Parquet file.

        Example
        -------
        selector = 'thu-coai/AISafetyLab_Datasets/advbench'
        -> expects one of:
           <local_data_dir>/advbench.json
           <local_data_dir>/advbench.jsonl
           <local_data_dir>/advbench.csv
           <local_data_dir>/advbench.xlsx
           <local_data_dir>/advbench.parquet
        """
        # Determine base directory:
        #   1) explicit argument
        #   2) environment variable
        #   3) otherwise raise a friendly error
        base_dir = (
            str(local_data_dir)
            if local_data_dir
            else os.getenv("AISAFETYLAB_DATASETS_DIR")
        )
        if not base_dir:
            raise FileNotFoundError(
                "Cannot resolve local dataset directory for 'thu-coai/AISafetyLab_Datasets'. "
                "Provide `local_data_dir` OR set environment variable 'AISAFETYLAB_DATASETS_DIR'."
            )

        # Extract the last path segment as the dataset file stem
        # e.g., '.../advbench' -> 'advbench'
        file_stem = selector.strip("/").split("/")[-1]

        # Try known extensions in order of preference
        candidate_exts = [".json", ".jsonl", ".csv", ".xlsx", ".parquet"]
        candidates = [os.path.join(base_dir, file_stem + ext) for ext in candidate_exts]
        existing = next((p for p in candidates if os.path.exists(p)), None)

        if not existing:
            # Help the user discover what we tried
            tried = "\n  - ".join(candidates)
            raise FileNotFoundError(
                "Could not find a local dataset file for selector "
                f"'{selector}'. Tried:\n  - {tried}"
            )

        logger.info(f"Loading local AISafetyLab dataset from: {existing}")
        return self._from_local_file(existing)

    def _apply_subset(self, subset_slice: Union[int, slice, Sequence[int], Any]) -> None:
        """Uniformly apply a variety of slice formats to `self.data`."""
        if isinstance(subset_slice, int):
            # Take the first N items
            self.data = self.data[: subset_slice]
            return

        if isinstance(subset_slice, (list, tuple)):
            # Interpret as slice(*subset_slice) when 1-3 integers given
            if 1 <= len(subset_slice) <= 3 and all(
                (x is None or isinstance(x, int)) for x in subset_slice
            ):
                s = slice(*subset_slice)  # type: ignore[arg-type]
                self.data = self.data[s]
                return

        try:
            # Last resort: trust Python slicing semantics on whatever was passed
            self.data = self.data[subset_slice]  # type: ignore[index]
        except Exception as e:
            raise ValueError(
                f"Unsupported subset_slice format: {subset_slice!r}"
            ) from e

    # -------------------------------------------------------------------------
    # Python data model
    # -------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Example:
        return self.data[idx]

    def __iter__(self):
        return iter(self.data)


# -----------------------------------------------------------------------------
# Optional: AugmentDataLoader (kept close to original intent, but safer)
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Torch-free mini DataLoader with optional augmentation
# -----------------------------------------------------------------------------

class AugmentDataLoader:
    """
    A lightweight, torch-free batch loader that:
      - Iterates over an AttackDataset
      - Batches items
      - (Optionally) augments the 'target' field in-batch
      - Yields a dict-of-lists (keys are union of all item fields)

    Parameters
    ----------
    dataset : AttackDataset
    batch_size : int
    shuffle : bool
        Shuffle indices at the start of each iteration.
    augment_target : bool
        If True, apply each function in `augment_fns` to every string in the 'target'
        list with independent 50% probability per function.
    augment_fns : Optional[Sequence[Callable[[str], str]]]
        Callables that each take and return a string. Defaults mimic your original logic.
    drop_last : bool
        If True, drop the final smaller batch when len(dataset) % batch_size != 0.
    """

    def __init__(
        self,
        dataset: "AttackDataset",
        batch_size: int,
        shuffle: bool,
        augment_target: bool = False,
        augment_fns: Optional[Sequence[Callable[[str], str]]] = None,
        drop_last: bool = False,
    ) -> None:
        self.dataset = dataset
        self.batch_size = int(batch_size)
        self.shuffle = bool(shuffle)
        self.augment_target = bool(augment_target)
        self.drop_last = bool(drop_last)

        # Default augmentation functions (match the original behavior)
        default_augments = (
            lambda s: s.replace("Sure, here is", "Sure, here's"),
            lambda s: s.replace("Sure, h", "H"),
        )
        self.augment_fns: List[Callable[[str], str]] = list(augment_fns or default_augments)

        if self.batch_size <= 0:
            raise ValueError("batch_size must be a positive integer.")

    def __len__(self) -> int:
        """Number of batches per full pass (drops last if configured)."""
        n = len(self.dataset)
        if self.drop_last:
            return n // self.batch_size
        return (n + self.batch_size - 1) // self.batch_size

    def __iter__(self) -> Iterator[Dict[str, List[Any]]]:
        n = len(self.dataset)
        if n == 0:
            return
            yield  # pragma: no cover (satisfy generator type checker)

        indices = list(range(n))
        if self.shuffle:
            random.shuffle(indices)

        for start in range(0, n, self.batch_size):
            end = start + self.batch_size
            if end > n and self.drop_last:
                break
            batch_indices = indices[start:end]
            items = [self.dataset[i] for i in batch_indices]
            yield self._collate(items)

    # ------------------------------ helpers ---------------------------------

    @staticmethod
    def _item_to_dict(item: Any) -> Dict[str, Any]:
        """
        Convert a dataset item (Example or Mapping) into a plain dict.
        - If it's a Mapping: shallow-copy to dict.
        - Else: try vars(item) to get attribute dict.
        - Fallback to {'value': item!r}.
        """
        from collections.abc import Mapping as _Mapping

        if isinstance(item, _Mapping):
            return dict(item)

        try:
            return dict(vars(item))
        except Exception:
            return {"value": item}

    def _collate(self, items: List[Any]) -> Dict[str, List[Any]]:
        """
        Turn a list of Example/Mapping items into a dict-of-lists.
        Missing keys are filled with None to keep list lengths aligned.
        Applies optional 'target' augmentation.
        """
        dicts = [self._item_to_dict(it) for it in items]

        # Union of keys
        keys: set[str] = set()
        for d in dicts:
            keys.update(d.keys())

        batch: Dict[str, List[Any]] = {k: [d.get(k, None) for d in dicts] for k in keys}

        # Optional augmentation on 'target'
        if self.augment_target and "target" in batch:
            augmented: List[Any] = []
            for t in batch["target"]:
                if isinstance(t, str):
                    for fn in self.augment_fns:
                        if random.random() < 0.5:
                            t = fn(t)
                augmented.append(t)
            batch["target"] = augmented

        return batch


def get_dataloader(
    data_pth: Union[PathLike, RowsLike],
    batch_size: int = 8,
    shuffle: bool = True,
    augment_target: bool = False,
    augment_fns: Optional[Sequence[Callable[[str], str]]] = None,
    local_data_dir: Optional[PathLike] = None,
    subset_slice: Optional[Union[int, slice, Sequence[int], Any]] = None,
    drop_last: bool = False,
) -> AugmentDataLoader:
    """
    Build an AttackDataset and a torch-free AugmentDataLoader.

    Returns
    -------
    AugmentDataLoader
        Iterates batches as dict-of-lists (e.g., batch["target"] is a List[str|Any]).
    """
    dataset = AttackDataset(
        path=data_pth, subset_slice=subset_slice, local_data_dir=local_data_dir
    )
    return AugmentDataLoader(
        dataset=dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        augment_target=augment_target,
        augment_fns=augment_fns,
        drop_last=drop_last,
    )
