import importlib.resources as pkg_resources
from importlib.resources.abc import Traversable
from typing import Generator, Callable


def _get_package_root_name() -> str:
    return __package__.split(".")[0]


def _load_package_text(file_name: str, *, root: str = "data") -> str:
    data_ref = pkg_resources.files(_get_package_root_name())
    for part in root.split("/"):
        data_ref = data_ref / part
    data_ref = data_ref / file_name
    with data_ref.open("r") as f:
        data = f.read()
    return data


def _get_data_cached(
    owner: object,
    *,
    file_name: str,
    root: str = "data",
) -> dict | list | str:
    """
    Get the data from the package's data directory, and cache it in the owner object.
    """
    cache_key = f"_{file_name}_data"
    if (item := getattr(owner, cache_key, None)) is None:
        item = _load_package_text(file_name, root=root)
        setattr(owner, cache_key, item)
    return item


def get_package_data(file_name: str, *, root: str = "data") -> dict | list | str:
    return _get_data_cached(_get_data_cached, file_name=file_name, root=root)


def _ignore_file(file_name: str) -> bool:
    if file_name.startswith(".") or file_name.startswith("__"):
        return True
    return False


def _enumerate_package_directory(
    dir: Traversable, path: str = "", filter: Callable[[str], bool] | None = None
) -> Generator[str, None, None]:
    for item in dir.iterdir():
        if _ignore_file(item.name) or (filter is not None and not filter(item.name)):
            continue
        if item.is_dir():
            yield from _enumerate_package_directory(item, path + item.name + "/")
        else:
            yield path + item.name


def list_package_files(root: str = "data", *, filter: Callable[[str], bool] | None = None) -> list[str]:
    data_ref = pkg_resources.files(_get_package_root_name())
    for part in root.split("/"):
        if not part:
            continue
        data_ref = data_ref / part
    return [f for f in _enumerate_package_directory(data_ref, filter=filter)]
