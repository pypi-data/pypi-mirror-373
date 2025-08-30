from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait, ALL_COMPLETED
from datetime import datetime
import hashlib
import inspect
import os
import pickle
from typing import Optional
from time import time

from typing_extensions import Literal

from tqdm import tqdm


CACHE_UPDATE_HOURS = 6


def get_guanaco_data_dir_env():
    home_dir = os.path.expanduser("~")
    return os.environ.get('GUANACO_DATA_DIR', f'{home_dir}/.chai-guanaco')


def guanaco_data_dir():
    data_dir = get_guanaco_data_dir_env()
    os.makedirs(os.path.join(data_dir, 'cache'), exist_ok=True)
    return data_dir


def print_color(text, color, **kwargs):
    colors = {
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'white': '\033[97m',
        'yellow': '\033[93m',
        'magenta': '\033[95m',
        'grey': '\033[90m',
        'black': '\033[90m',
        'default': '\033[99m'
    }
    assert color in colors.keys()
    print(f'{colors[color]}{text}\033[0m', **kwargs)


def cache(func, regenerate=False):
    def wrapper(*args, **kwargs):
        file_path = _get_cache_file_path(func, args, kwargs)
        try:
            result = _load_from_cache(file_path)
            assert not regenerate
            # ensuring file is less than N hours old, otherwise regenerate
            assert (time() - os.path.getmtime(file_path)) < 3600 * CACHE_UPDATE_HOURS
        except (FileNotFoundError, AssertionError):
            result = func(*args, **kwargs)
            _save_to_cache(file_path, result)
        return result
    return wrapper


def _get_cache_file_path(func, args, kwargs):
    cache_dir = os.path.join(guanaco_data_dir(), 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    func_name = func.__name__
    signature = _func_call_as_string(func, args, kwargs)
    signature_hexdigest = get_hexdigest(signature)
    fname = f'cache-{func_name}-{signature_hexdigest}'
    return os.path.join(cache_dir, f'{fname}.pkl')


def get_hexdigest(input_string):
    hexdigest = hashlib.md5(input_string.encode('UTF-8')).hexdigest()
    return hexdigest


def _load_from_cache(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def _save_to_cache(file_path, data):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)


def _func_call_as_string(func, args, kwargs):
    func_name = func.__name__
    param_names = list(inspect.signature(func).parameters.keys())
    arg_strs = [f'{name}={value!r}' for name, value in zip(param_names, args)]
    arg_strs += [f'{name}={value!r}' for name, value in kwargs.items()]
    return f"{func_name}({', '.join(arg_strs)})"


def get_localised_timestamp(timestamp, timezone=None):
    if not timezone:
        timezone = datetime.now().astimezone().tzinfo
    timestamp = datetime.fromisoformat(timestamp)
    timestamp = timestamp.astimezone(timezone)
    return timestamp


def parse_log_entry(log, timezone=None):
    timestamp = get_localised_timestamp(log["timestamp"], timezone)
    timestamp = timestamp.strftime("%H:%M:%S")
    message = [timestamp, log["level"], log["entry"]]
    message = ":".join(message)
    return message


def _distribute_to_multiple_workers(func, *args_iter, max_workers=2, worker_type: Literal['process', 'thread']='process', **kwargs):
    futures = []
    with tqdm(total=None) as progress:
        PoolExecutor = ProcessPoolExecutor if worker_type == 'process' else ThreadPoolExecutor
        with PoolExecutor(max_workers) as executor:
            for func_args in zip(*args_iter):
                future = executor.submit(func, *func_args, **kwargs)
                future.add_done_callback(lambda p: progress.update(1))
                futures.append(future)
            progress.total = len(futures)
            wait(futures, return_when=ALL_COMPLETED)
    results = [future.result() for future in futures]
    return results


def _distribute_to_single_worker(func, *args_iter, **kwargs):
    args_list = list(zip(*args_iter))
    results = [func(*args, **kwargs) for args in tqdm(args_list, total=len(args_list))]
    return results


def distribute_to_workers(func, *args_iter,  max_workers=1, worker_type: Literal['process', 'thread']='process', **kwargs):
    if max_workers == 1:
        return _distribute_to_single_worker(func, *args_iter, **kwargs)
    else:
        return _distribute_to_multiple_workers(func, *args_iter, max_workers=max_workers, worker_type=worker_type, **kwargs)
