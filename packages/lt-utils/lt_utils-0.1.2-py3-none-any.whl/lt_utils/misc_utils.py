__all__ = [
    "default",
    "get_traceback_data",
    "log_traceback",
    "get_os_info",
    "get_system_memory",
    "get_pid_by_name",
    "get_process_memory",
    "close_process_by_id",
    "close_process_by_name",
    "clear_all_caches",
    "malloc_trim",
    "clean_memory",
    "terminal",
    "cache_wrapper",
    "get_encoding_aliases",
    "get_unicode_chars",
    "flatten_list",
    "filter_list",
    "ff_list",
    "safe_call",
    "import_functions",
    "get_current_time",
    "get_random_name",
    "args_to_kwargs",
    "filter_kwargs",
]

import gc
import re
import os

import psutil

import platform


from functools import lru_cache, wraps
from lt_utils.common import *
from typing import TypeVar, get_args

from lt_utils.type_utils import is_array, is_dict, is_union, is_pathlike
from lt_utils.file_ops import path_to_str

T = TypeVar("T")


def default(entry: Optional[T], other: T) -> T:
    return entry if entry is not None else other


def filter_kwargs(
    target: object, __return_invalid: bool = False, __ignore: List[str] = [], **kwargs
):
    import inspect

    available_kwargs = list(inspect.signature(target).parameters.keys())
    validated_kwargs = {}
    invalid_kwargs = {}
    for k, v in kwargs.items():
        if k in available_kwargs:
            if k not in __ignore:
                validated_kwargs[k] = v
        else:
            if __return_invalid:
                invalid_kwargs[k] = v
    if __return_invalid:
        return validated_kwargs, invalid_kwargs
    return validated_kwargs


def get_traceback_data(
    tb: str,
) -> Tuple[List[Dict[str, Union[str, Number]]], List[str]]:
    results: List[dict[str, Number]] = []
    unprocessed: List[str] = []
    for gp in re.finditer(r"\w+ \"([\w+:\\\.\-\_/]+)\", line (\d+), in (.+)\n(.+)", tb):
        try:
            results.append(
                {
                    "module": gp[1].strip(),
                    "line_id": int(gp[2].strip()),
                    "in": gp[3].strip(),
                    "value": gp[4].strip(),
                }
            )

        except Exception as e:
            unprocessed.append(gp.string)
    return results, unprocessed


def log_traceback(
    exception: Exception,
    title: Optional[str] = None,
    invert_traceback: bool = False,
    show_len: Optional[Union[Tuple[int, int], int]] = None,
) -> Tuple[List[Dict[str, Union[str, Number]]], List[str]]:
    """Logs the traceback stack of an exception, with optional title, limit, and inversion settings.

    Args:
        exception (Exception): The exception object.
        title (Optional[str], optional): A title for the exception that will be displayed, can be a reference that
                                        may help to locate where the error ocurred easier. Defaults to None.
        limit (Optional[int], optional): Limit for the traceback. Defaults to None.
        invert_traceback (bool, optional): If is preferred that the traceback is printed in inverse order. Defaults to False.
        show_len (Optional[Union[Tuple[int, int], int]], optional): Defines limits for the printing of the traceback.
                                            Can be set to either a tuple/list or a integer. If set with a list or tuple,
                                            for example: `[3, 5]`, then the traceback shows the first 3 items and the last 5 items.
                                            If set to a integer or a list of a single value, for example `8`, then it will only retrieve the last 8 items from the traceback. Defaults to None.

    Returns:
        Tuple[List[Dict[str, Union[str, Number]]], List[str]]: A tuple containing the dictionary of the traceback,
                                    and a list of strings that the `get_traceback_data` failed to extract from the log.
                                    It contains the entire tracing to be further looked into.
    """
    import traceback

    tb_lines = traceback.format_exception(
        type(exception), exception, exception.__traceback__, limit=None
    )
    tb_data = get_traceback_data("\n".join(tb_lines))
    if show_len is not None:
        if isinstance(show_len, (list, tuple)):
            show_len = [abs(x) for x in ff_list(show_len, int)]
            _total = len(show_len)
            if _total == 1:
                tb_lines[-show_len[0] :]
            elif _total == 2:
                _b = tb_lines[: show_len[0]]
                _e = tb_lines[-show_len[-1] :]
                tb_lines = _b + _e
        elif isinstance(show_len, int):
            tb_lines[-abs(show_len) :]

    if invert_traceback:
        tb_lines.reverse()
    print("\n===========================")
    if isinstance(title, str) and title.strip():
        print(f"-----[ {title} ]-----")
    print(f"{exception}")
    print("-------[ Traceback ]-------")
    print("\n".join(tb_lines))
    print("===========================\n")
    return tb_data


def get_os_info() -> Dict[str, str]:
    """Returns information about the operating system."""
    return {
        "os": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }


def get_system_memory() -> Dict[str, Number]:
    """Returns system memory stats in bytes."""
    vm = psutil.virtual_memory()
    return {
        "total": vm.total,
        "available": vm.available,
        "used": vm.used,
        "free": vm.free,
        "percent": vm.percent,
    }


def get_pid_by_name(process_name: str, strict: bool = False) -> List[Dict[str, Any]]:
    if not strict:
        process_name = process_name.lower()
    results: List[Dict[str, Any]] = []
    for proc in psutil.process_iter():
        process_info = proc.as_dict(attrs=["pid", "name", "status", "ppid"])
        valid = (
            (process_name == process_info["name"])
            if strict
            else (process_name in process_info["name"].lower())
        )
        if valid:
            results.append(process_info)
    return results


def get_process_memory(pid: int = None) -> Dict[str, Any]:
    """Returns memory usage of a given process (or current one)."""
    pid = pid or os.getpid()
    proc = psutil.Process(pid)
    mem_info = proc.memory_info()
    return {
        "rss": mem_info.rss,  # Resident Set Size
        "vms": mem_info.vms,  # Virtual Memory Size
        "shared": getattr(mem_info, "shared", 0),
        "text": getattr(mem_info, "text", 0),
        "lib": getattr(mem_info, "lib", 0),
        "data": getattr(mem_info, "data", 0),
        "dirty": getattr(mem_info, "dirty", 0),
    }


def close_process_by_id(pid: int):
    """Example: `close_process("notepad.exe")`"""
    proc = psutil.Process(pid)
    process_info = proc.as_dict(attrs=["pid", "name", "status", "ppid"])
    try:
        proc.terminate()
        process_info["results"] = {"stats": "success", "reason": None}
        process_info["status"] = "terminated"

    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        # Prudently handling potential exceptions arising during process information retrieval
        process_info["results"] = {"stats": "fail_safe", "reason": str(e)}
        pass

    except Exception as e:
        process_info["results"] = {"stats": "fail", "reason": str(e)}

    return process_info


def close_process_by_name(process_name: str, strict: bool = False):
    """Example: `close_process_by_name("notepad.exe")`"""
    if not strict:
        process_name = process_name.lower()
    results: List[Dict[str, Any]] = []

    for proc in psutil.process_iter():
        process_info = proc.as_dict(attrs=["pid", "name", "status", "ppid"])
        if not strict:
            valid = process_name in process_info["name"].lower()
        else:
            valid = process_info["name"] == process_name
        if not valid:
            continue
        try:
            proc.terminate()
            process_info["results"] = {"stats": "success", "reason": None}
            process_info["status"] = "terminated"
            print(f"Instance deletion successful: {process_info}")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            process_info["results"] = {"stats": "fail_safe", "reason": str(e)}

        except Exception as e:
            print(e)
            process_info["results"] = {"stats": "fail", "reason": str(e)}
        finally:
            results.append(process_info)

    return results


def clear_all_caches(registered_funcs: Optional[list] = None):
    """Clears global caches like lru_cache and runs garbage collection."""
    gc.collect()
    if registered_funcs:
        for func in registered_funcs:
            try:
                func.cache_clear()
            except AttributeError:
                pass


def malloc_trim():
    """On Linux, frees memory from malloc() back to the OS."""
    if platform.system() == "Linux":
        import ctypes

        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)


def clean_memory(clears: Optional[list] = None):
    """Performs full memory cleanup: gc, cache clears, and malloc_trim (Linux)."""
    clear_all_caches(clears)
    malloc_trim()


def terminal(
    *commant_lines: str,
    encoding: Optional[
        Union[
            Literal[
                "ascii",
                "utf-8",
                "iso-8859-1",
                "unicode-escape",
            ],
            str,
        ]
    ] = None,
    errors: Literal[
        "ignore",
        "strict",
        "replace",
        "backslashreplace",
        "surrogateescape",
    ] = "strict",
):
    """Terminal that returns the output
    made mostly to just to save a line of code."""
    import subprocess

    return subprocess.run(
        commant_lines,
        shell=True,
        capture_output=True,
        text=True,
        encoding=encoding,
        errors=errors,
    ).stdout


def cache_wrapper(func):
    """
    A decorator to cache the function result while keeping the original documentation, variable names, etc.

    Example
        ```py
        @cache_wrapper
        def your_function(arg1:int, arg2:int) -> bool:
            \"\"\"
            compares if the first number is larger than the second number.
            args:
                arg1(int): The number that is expected to be larger than arg2.
                arg2(int): The number expected to be smaller than arg1

            return:
                bool: True if arg1 is larger than arg2 otherwise False.
            \"\"\"
            return arg1 > arg2
        ```
    """
    cached_func = lru_cache(maxsize=None)(func)

    # Apply the wraps decorator to copy the metadata from the original function
    @wraps(func)
    def wrapper(*args, **kwargs):
        return cached_func(*args, **kwargs)

    return wrapper


def get_encoding_aliases(entry: Optional[str] = None):
    from encodings.aliases import aliases

    if entry is None:
        return [(k, v) for k, v in aliases.items()]
    return [(k, v) for k, v in aliases.items() if entry in k or entry in v]


def get_unicode_chars(start_hex, end_hex):
    """
    # Example:
    my_character_set = get_unicode_chars('0E00', '0E7F')
    print("".join(my_character_set))
    """
    return [chr(code) for code in range(int(start_hex, 16), int(end_hex, 16) + 1)]


def flatten_list(entry):
    """
    Example:
    ```py
    from gr1336_toolbox import flatten_list

    sample = ["test", [[[1]], [2]], 3, [{"last":4}]]
    results = flatten_list(sample)
    # results = ["test", 1, 2, 3, {"last": 4}]
    ```"""
    if is_array(entry, True):
        return [item for sublist in entry for item in flatten_list(sublist)]
    return [entry] if entry is not None else []


def filter_list(entry: Union[list, tuple], types: Union[T, tuple[T]]) -> list[T]:
    assert is_array(entry, False), "To filter a list, it must be a list or a tuple"
    if is_union(types):
        types = get_args(types)
    return [x for x in entry if isinstance(x, types)]


def ff_list(entry: Union[list, tuple], types: Union[T, tuple[T]]) -> List[T]:
    """Flattens and filters the provided list"""
    assert is_array(
        entry, False, False
    ), "To flatten and filter a list, it must be a list or a tuple"
    return filter_list(flatten_list(entry), types)


def safe_call(
    fn: Callable[[T], T],
    fn_args: List[Any] = [],
    fn_kwargs: Dict[str, Any] = {},
    safe_default: Optional[T] = None,
    verbose_exception: bool = False,
) -> T:
    """Can be used to call a function without an exception interrupting the process.

    Args:
        fn (Callable[[T, ...], T]): The function to be called safely.
        fn_args (List[Any]): Tuple or list with the args of the given function.
        fn_kwargs (Dict[str, Any]): Dictionary with the kwargs of the given function.
        safe_default (T): The value that will be returned case an exception is raised.
        verbose_exception (bool, optional): If True, logs the traceback if the function raises anything. Defaults to False.
    Returns:
        T: The output type of the given function or the default value.
    """
    is_array(fn_args, validate=True)
    is_dict(fn_kwargs, validate=True)
    try:
        return fn(*fn_args, **fn_kwargs)
    except Exception as e:
        if verbose_exception:
            try:
                fn_name = fn.__name__
            except:
                fn_name = "safe_call"
            log_traceback(e, fn_name)
        return safe_default


def import_functions(
    path: Union[str, Path],
    target_function: str,
    pattern: str = "*.py",
    deep_scan: bool = True,
    validate_path: bool = False,
):
    """
    Imports and returns all functions from .py files in the specified directory matching a certain function name.

    Args:
        path (str or Path): The path of the directories to search for the Python files.
        target_function (str): The exact string representing the function name to be searched within each file.
        pattern (str, optional): Pattern of the file to be scanned. Defaults to "*.py" with covers all files with .py extension.
        deep_scan (bool, optional): Setting this to false will make only a surface level scan in the directory, while keeping it True, will scan all the sub-folders in the given directory. Defaults to True.
        validate_path (bool, optional): If True, this function will raise an "FileNotFoundError" exception when the given path does not exist. Defaults to False.

    Returns:
        list: A list containing all the functions with the given name found in the specified directory and subdirectories.

    Example:
        >>> import_functions('/path/to/directory', 'some_function')
        [<function some_function at 0x7f036b4c6958>, <function some_function at 0x7f036b4c69a0>]
    """
    is_pathlike(path, False, validate=True)
    results = []
    path = Path(path)
    if not path.exists():
        if validate_path:
            raise FileNotFoundError(f"'{path_to_str(path)}' does not exist!")
        return results
    if path.is_dir():
        from lt_utils.file_ops import find_files

        python_files = [find_files(path, [pattern], deep=deep_scan)]
    else:
        python_files = [path]
    if python_files:
        import importlib.util

        for file in python_files:
            spec = importlib.util.spec_from_file_location(file.name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, target_function):
                results.append(getattr(module, target_function))
    return results


def get_current_time():
    """
    Returns the current date and time in a 'YYYY-MM-DD-HHMMSS' format.

    Returns:
        str: The current date and time.
    """
    from datetime import datetime

    return f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"


def get_random_name(source: Literal["time", "uuid4", "uuid4-hex"] = "uuid4"):
    from uuid import uuid4

    assert isinstance(
        source, str
    ), f'Invalid type "{type(source)}". A value for `source` needs to be a valid str'
    assert source.strip(), "Source cannot be empty!"
    source = source.lower().strip()
    assert source in [
        "time",
        "uuid4",
        "uuid-hex",
    ], f'No such source \'{source}\'. It needs to be either "time", "uuid4" or "uuid4-hex"'
    match source:
        case "time":
            return get_current_time()
        case "uuid4":
            return str(uuid4())
        case _:
            return uuid4().hex


def args_to_kwargs(*args):
    from inspect import currentframe

    frame = currentframe().f_back
    results = {}
    for name, value in frame.f_locals.items():
        if value in args:
            results[name] = value
    return results
