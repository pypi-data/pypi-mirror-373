import glob
import io
import os
import pickle
import shutil
import tempfile
from contextlib import contextmanager
from io import BytesIO
from typing import Optional, List, Tuple, Union, Generator, IO, Any, Literal
from urllib.parse import urlparse

import boto3
import numpy as np
from s3fs import S3FileSystem

import sfu_torch_lib.utils as utils


ModeType = Literal['r', 'r+', 'w+', 'c']
MMapModeType = Literal['readonly', 'r', 'copyonwrite', 'c', 'readwrite', 'r+', 'write', 'w+']


def get_data_cache_path() -> Optional[str]:
    return os.getenv('DATA_PATH')


def get_data_path() -> Optional[str]:
    return os.getenv('DATA_EPHEMERAL_PATH', get_data_cache_path())


def is_development_mode() -> bool:
    return utils.to_bool_or_false(os.getenv('DEVELOPMENT_MODE'))


def get_client(endpoint_url: Optional[str] = os.getenv('S3_ENDPOINT_URL'), verify: Optional[bool] = None):
    verify = utils.to_bool(os.getenv('S3_VERIFY')) if verify is None else verify

    client = boto3.client('s3', endpoint_url=endpoint_url, verify=verify)

    return client


def get_s3fs(endpoint_url: Optional[str] = os.getenv('S3_ENDPOINT_URL'), verify: Optional[bool] = None) -> S3FileSystem:
    verify = utils.to_bool(os.getenv('S3_VERIFY')) if verify is None else verify

    filesystem = S3FileSystem(client_kwargs={'endpoint_url': endpoint_url, 'verify': verify})

    return filesystem


def get_bucket_and_key(path: str) -> Tuple[str, str]:
    url = urlparse(path)
    bucket, key = url.netloc, url.path.strip('/')

    return bucket, key


def download_s3(bucket: str, key: str, destination: str) -> None:
    directory, _ = os.path.split(destination)

    os.makedirs(directory, exist_ok=True)

    get_client().download_file(Bucket=bucket, Key=key, Filename=destination)


def upload_s3(bucket: str, key: str, source: Union[str, BytesIO]) -> None:
    client = get_client()

    if isinstance(source, str):
        client.upload_file(Filename=source, Bucket=bucket, Key=key)
    else:
        client.upload_fileobj(Fileobj=source, Bucket=bucket, Key=key)


def _get_s3_keys(bucket: str, prefix: str = '') -> Generator[str, None, None]:
    object_list = get_client().list_objects_v2(Bucket=bucket, Prefix=prefix)

    if 'Contents' not in object_list:
        return

    for file in object_list['Contents']:
        yield file['Key']

    while object_list['IsTruncated']:
        object_list = get_client().list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            ContinuationToken=object_list['NextContinuationToken'],
        )

        if 'Contents' not in object_list:
            return

        for file in object_list['Contents']:
            yield file['Key']


def _get_local_files(path: str) -> List[str]:
    paths = [path for path in glob.glob(os.path.join(path, '**'), recursive=True) if os.path.isfile(path)]

    return paths


def get_files(path: str) -> List[str]:
    if not path.startswith('s3'):
        return _get_local_files(path)

    bucket, prefix = get_bucket_and_key(path)

    paths = [f's3://{os.path.join(bucket, key)}' for key in _get_s3_keys(bucket, prefix)]

    return paths


def exists(path: str) -> bool:
    if not path.startswith('s3'):
        return os.path.exists(path)

    bucket, key = get_bucket_and_key(path)
    has_keys = sum(1 for _ in _get_s3_keys(bucket, key)) > 0

    return has_keys


def generate_path(suffix: Optional[str] = None, prefix: Optional[str] = get_data_path()) -> str:
    prefix = prefix if prefix is not None else tempfile.gettempdir()

    if not suffix:
        return prefix

    path = os.path.join(prefix, suffix)

    return path


def localize_directory(
    path: str,
    directory: Optional[str] = get_data_path(),
    prefix: Optional[str] = None,
    overwrite: bool = True,
) -> str:
    basename = os.path.basename(path)

    target = generate_path(basename) if directory is None else generate_path(basename, directory)
    target_prefixed = os.path.join(target, prefix) if prefix else target

    if not overwrite and exists(target_prefixed):
        return target

    elif path.startswith('s3'):
        bucket, key_base = get_bucket_and_key(path)
        key_base_prefixed = os.path.join(key_base, prefix) if prefix else key_base
        key_base_prefixed = key_base_prefixed if key_base_prefixed.endswith('/') else key_base_prefixed + '/'

        for key in _get_s3_keys(bucket, key_base_prefixed):
            download_s3(bucket, key, generate_path(os.path.relpath(key, key_base), target))

        return target

    elif directory is not None:
        path_prefixed = os.path.join(path, prefix) if prefix else path

        if path != target:
            shutil.copytree(path_prefixed, target_prefixed)

        return target

    else:
        return path


def localize_file(
    path: str,
    directory: Optional[str] = get_data_path(),
    basename: Optional[str] = None,
    overwrite: bool = True,
) -> str:
    basename = os.path.basename(path) if basename is None else basename
    target = generate_path(basename) if directory is None else generate_path(basename, directory)

    if not overwrite and exists(target):
        return target

    elif path.startswith('s3'):
        bucket, key = get_bucket_and_key(path)
        download_s3(bucket, key, target)

        return target

    elif directory is not None:
        if path != target:
            shutil.copy(path, target)

        return target

    else:
        return path


def localize_file_or_directory(
    path: str,
    directory: Optional[str] = get_data_path(),
    basename_or_prefix: Optional[str] = None,
    overwrite: bool = True,
) -> str:
    if '.' in os.path.basename(path):
        return localize_file(path, directory, basename_or_prefix, overwrite)
    else:
        return localize_directory(path, directory, basename_or_prefix, overwrite)


def localize_cached(
    path: str,
    basename_or_prefix: Optional[str] = None,
    overwrite: bool = False,
    cache: bool = True,
    data_cache_path: Optional[str] = get_data_cache_path(),
) -> str:
    if cache:
        assert data_cache_path is not None

    if cache and data_cache_path is not None:
        path_local = localize_file_or_directory(path, data_cache_path, basename_or_prefix, overwrite)
        path_local = localize_file_or_directory(path_local, basename_or_prefix=basename_or_prefix, overwrite=overwrite)

    else:
        path_local = localize_file_or_directory(path, basename_or_prefix=basename_or_prefix, overwrite=overwrite)

    return path_local


def localize_dataset(
    path: str,
    basename: Optional[str] = None,
    overwrite: bool = False,
    cache: bool = True,
    development_mode: bool = is_development_mode(),
) -> str:
    if development_mode:
        prefix, extension = os.path.splitext(path)
        path_development = f'{prefix}-tiny{extension}'
        path = path_development if exists(path_development) else path

    path_local = localize_cached(path, basename, overwrite, cache=cache and not development_mode)

    return path_local


def load_npy(path: str, mmap_mode: Optional[ModeType] = None) -> np.ndarray:
    return np.load(localize_file(path), mmap_mode)


def load_bin(
    path: str,
    dtype=np.uint8,
    mode: MMapModeType = 'r+',
    shape: Optional[Union[int, Tuple[int, ...]]] = None,
) -> np.ndarray:
    return np.memmap(localize_file(path), dtype, mode, shape=shape)


def open(path: str, mode: str = 'rb', encoding: Optional[str] = None, newline: Optional[str] = None) -> IO:
    open_function = get_s3fs().open if path.startswith('s3') else io.open

    file_object = open_function(path, mode=mode, encoding=encoding, newline=newline)

    return file_object  # type: ignore


def read(path: str, encoding: Optional[str] = None) -> Union[bytes, str]:
    if not path.startswith('s3'):
        if encoding:
            return io.open(path, mode='r', encoding=encoding).read()
        else:
            return io.open(path, mode='rb').read()

    bucket, key = get_bucket_and_key(path)

    content = get_client().get_object(Bucket=bucket, Key=key)['Body'].read()

    if encoding:
        return content.decode(encoding)

    return content


@contextmanager
def with_local_file(path: str) -> Generator[str, None, None]:
    local_path = generate_path(os.path.basename(path)) if path.startswith('s3') else path

    yield local_path

    if path.startswith('s3'):
        bucket, key = get_bucket_and_key(path)
        upload_s3(bucket, key, local_path)


@contextmanager
def with_local_directory(path: str) -> Generator[str, None, None]:
    local_path = generate_path(os.path.basename(path)) if path.startswith('s3') else path

    yield local_path

    if path.startswith('s3'):
        sync_remote(local_path, path)


def save_npy(path: str, data: np.ndarray) -> None:
    if not path.startswith('s3'):
        np.save(path, data)

    else:
        with open(path, mode='wb') as writer:
            np.save(writer, data)


def save_pickle(path: str, data: Any) -> None:
    if not path.startswith('s3'):
        with io.open(path, mode='wb') as file:
            pickle.dump(data, file)

    else:
        with open(path, mode='wb') as writer:
            pickle.dump(data, writer)


def sync_remote(local_path: str, remote_path: str) -> None:
    paths = (path for path in glob.glob(os.path.join(local_path, '**'), recursive=True) if os.path.isfile(path))

    for path in paths:
        path_in_remote_path = generate_path(os.path.relpath(path, local_path), remote_path)

        bucket, key = get_bucket_and_key(path_in_remote_path)
        upload_s3(bucket, key, path)
