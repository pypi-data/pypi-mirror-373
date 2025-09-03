import json
from collections.abc import Sequence
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

import tabulate

import h2o_mlops_autogen


class UnsetType:
    pass


UNSET = UnsetType()


class Table(Sequence):
    """Table that lazy loads."""

    def __init__(  # noqa: S107
        self,
        data: List[Dict[str, Any]],
        keys: List[str],
        get_method: Optional[Callable],
        list_method: Optional[Callable] = None,
        list_args: Optional[Dict[str, Any]] = None,
        next_page_token: str = "",
        **filters: Any,
    ):
        self.__data: List[Dict[str, Any]]
        self._keys = keys
        self._get = get_method

        self._list = list_method
        self._list_args = list_args
        self._next_page_token = next_page_token
        self._first_page_data = data
        self._current_index = 0
        self._page_num = 1

        self._filters = filters
        self._data = data

    @property
    def _data(self) -> List[Dict[str, Any]]:
        return self.__data

    @_data.setter
    def _data(self, data: List[Dict[str, Any]]) -> None:
        if f := self._filters:
            self.__data = [d for d in data if all([d[k] == v for k, v in f.items()])]
        else:
            self.__data = data

    def show(self, n: int) -> None:
        print(self._show(n))

    def __getitem__(self, index: Union[int, slice]) -> Any:
        if isinstance(index, slice):
            raise TypeError(f"Index must be an integer, not {type(index)}")
        index = len(self) + index if index < 0 else index
        for i, item in enumerate(self):
            if i == index:
                return item
        raise IndexError("Index out of range")

    def __iter__(self) -> "Table":
        self._current_index = 0
        if self._page_num != 1:
            self._data = []
            self._next_page_token = None
            self._page_num = 0
        return self

    def __next__(self) -> Any:
        if self._current_index < len(self._data):
            item = self._data[self._current_index]
            self._current_index += 1
            return self._get(item) if self._get else item

        if self._next_page_token != "":  # noqa: S105
            next_table: Table = self._list(
                page_token=self._next_page_token, **self._list_args
            )
            self._data = next_table._data
            self._next_page_token = next_table._next_page_token
            self._current_index = 0
            self._page_num += 1
            return self.__next__()

        raise StopIteration

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def __bool__(self) -> bool:
        for _ in self:
            return True
        return False

    def __repr__(self) -> str:
        return self._show(n=50)

    def _show(self, n: int) -> str:
        get_method, self._get = self._get, None
        table: List[List[Any]] = []
        for i, item in enumerate(self):
            if i == n:
                break
            row = [i] + [item[key] for key in self._keys]
            table.append(row)
        self._get = get_method
        headers = [""] + self._keys
        return tabulate.tabulate(table, headers=headers, tablefmt="presto")


def _convert_metadata(metadata: Any) -> Any:
    """Converts extracted metadata into Storage compatible value objects."""
    values = {}
    for k, v in metadata.values.items():
        o = h2o_mlops_autogen.StorageValue(
            bool_value=v.bool_value,
            double_value=v.double_value,
            duration_value=v.duration_value,
            int64_value=v.int64_value,
            string_value=v.string_value,
            json_value=v.json_value,
            timestamp_value=v.timestamp_value,
        )
        values[k] = o

    return h2o_mlops_autogen.StorageMetadata(values=values)


def _convert_to_storage_value(
    value: Union[str, int, float, bool, datetime, Dict, List[Dict]],
    is_id_value: bool = False,
) -> h2o_mlops_autogen.StorageValue:
    """Convert Python value into Storage compatible value object."""
    if is_id_value:
        return h2o_mlops_autogen.StorageValue(
            id_value=value,
        )
    if isinstance(value, float):
        return h2o_mlops_autogen.StorageValue(
            double_value=value,
        )
    if isinstance(value, str):
        return h2o_mlops_autogen.StorageValue(
            string_value=value,
        )
    if isinstance(value, int):
        return h2o_mlops_autogen.StorageValue(
            int64_value=str(value),
        )
    if isinstance(value, bool):
        return h2o_mlops_autogen.StorageValue(
            bool_value=value,
        )
    if isinstance(value, (dict, list)):
        return h2o_mlops_autogen.StorageValue(
            json_value=json.dumps(value),
        )
    if isinstance(value, datetime):
        return h2o_mlops_autogen.StorageValue(
            timestamp_value=value,
        )
    raise TypeError(f"Unsupported value type: {type(value)}")


def _convert_from_storage_value(
    storage_value: h2o_mlops_autogen.StorageValue,
) -> Optional[Union[str, int, float, bool, datetime, Dict, List[Dict]]]:
    """Convert Storage compatible value object into Python value."""
    for value_type, value in storage_value.to_dict().items():
        if value is not None:
            return (
                int(value)
                if value_type == "int64_value"
                else json.loads(value) if value_type == "json_value" else value
            )
    return None


def _convert_storage_metadata_to_table(
    storage_metadata: h2o_mlops_autogen.StorageMetadata,
    **selectors: Any,
) -> Table:
    """Convert Storage compatible metadata object into _utils.Table."""
    metadata = {}
    for key, storage_value in storage_metadata.values.items():
        metadata[key] = _convert_from_storage_value(storage_value)
    data = [
        {"key": k, "value": f"{str(v)[:40]}..." if len(str(v)) > 40 else str(v)}
        for k, v in metadata.items()
    ]
    return Table(
        data=data,
        keys=["key", "value"],
        get_method=lambda x: {x["key"]: metadata[x["key"]]},
        **selectors,
    )


def _convert_resource_name_to_uid(resource_name: str) -> str:
    return resource_name.split("/")[-1]
