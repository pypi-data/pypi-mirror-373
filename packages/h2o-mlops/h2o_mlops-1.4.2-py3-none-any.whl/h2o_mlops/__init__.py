import typing as _typing


def _load_module(module_name: str, library_name: _typing.Optional[str] = None) -> None:
    import importlib.util
    import pathlib
    import sys
    from h2o_mlops import __file__

    if library_name is None:
        library_name = module_name
    module_path = pathlib.Path(__file__).parent.joinpath(
        f"_autogen/{library_name}/__init__.py"
    )
    spec = importlib.util.spec_from_file_location(
        name=module_name, location=module_path
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)


def _load_autogen() -> None:
    import importlib.util

    module_name = "h2o_mlops_autogen"
    if importlib.util.find_spec(module_name) is None:
        _load_module("_h2o_mlops_client")
        _load_module("h2o_mlops_client")
        _load_module(module_name, "h2o_mlops_client")


_load_autogen()


from h2o_mlops._core import Client  # noqa: E402
from h2o_mlops._version import version as __version__  # noqa: E402, F401


__all__ = ["Client", "__version__"]
