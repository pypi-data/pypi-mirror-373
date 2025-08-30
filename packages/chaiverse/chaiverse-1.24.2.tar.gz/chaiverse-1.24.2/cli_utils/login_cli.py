import functools
import inspect
import os

from chaiverse.utils import guanaco_data_dir


def developer_login():
    cached_key_path = _get_cached_key_path()
    text = f"""Welcome to Chaiverse 🚀!
By logging in, we will create a file under {cached_key_path}.
Please enter your developer key: """
    developer_key = input(text)
    with open(cached_key_path, 'w') as file:
        file.write(developer_key)


def developer_logout():
    cached_key_path = _get_cached_key_path()
    if os.path.exists(cached_key_path):
        os.remove(cached_key_path)
    print('Logged out!')


def auto_authenticate(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args, kwargs = _update_developer_key(func, args, kwargs)
        return func(*args, **kwargs)
    return wrapper


def _update_developer_key(func, args, kwargs):
    if 'developer_key' not in kwargs and _developer_key_not_in_args(func, args):
        developer_key = get_developer_key_from_cache()
        kwargs['developer_key'] = developer_key
    return args, kwargs


def _developer_key_not_in_args(func, args):
    func_args = inspect.signature(func).parameters
    positional_args = list(func_args.keys())[:len(args)]
    return 'developer_key' not in positional_args


def get_developer_key_from_cache():
    developer_key = _get_cached_key()
    return developer_key


def _get_cached_key():
    try:
        cached_key_path = _get_cached_key_path()
        with open(cached_key_path, 'r') as f:
            developer_key = f.read().strip()
    except FileNotFoundError:
        print(f"Warning: No developer_key found stored in {cached_key_path}!")
        developer_key = None
    return developer_key


def _get_cached_key_path():
    data_dir = guanaco_data_dir()
    return os.path.join(data_dir, 'developer_key.json')
