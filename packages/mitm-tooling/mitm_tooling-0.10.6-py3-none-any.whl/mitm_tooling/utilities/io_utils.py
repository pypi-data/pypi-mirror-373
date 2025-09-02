from __future__ import annotations

import io
import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, BinaryIO, TextIO

import pydantic

from .python_utils import recursively_pick_from_mapping


def ensure_directory_exists(path: FilePath) -> None:
    dirname = os.path.dirname(path)
    if dirname != '' and not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)


def ensure_ext(path, desired_ext, override_ext=True):
    p, e = os.path.splitext(path)
    if e is None or e == '' or (override_ext and (e != desired_ext)):
        return path + desired_ext
    else:
        return path


FilePath = str | os.PathLike
ReadOnlyByteSource = bytes | memoryview
ByteSource = FilePath | BinaryIO | io.BufferedIOBase | ReadOnlyByteSource
TextSource = FilePath | TextIO | io.TextIOBase
DataSource = ByteSource | TextSource

ByteSink = FilePath | BinaryIO | io.BufferedIOBase
TextSink = FilePath | TextIO | io.TextIOBase
DataSink = ByteSink | TextSink


@contextmanager
def open_readonly_byte_buffer(arg: ReadOnlyByteSource) -> Generator[io.BytesIO, None, None]:
    if isinstance(arg, memoryview):
        arg = arg.tobytes()
    if isinstance(arg, bytes):
        with io.BytesIO(arg) as f:
            yield f


@contextmanager
def open_file(
    arg: FilePath,
    expected_file_ext: str,
    mode,
    create_file_if_necessary: bool = False,
    encoding: str | None = 'utf-8',
    **kwargs,
) -> Generator[BinaryIO | TextIO, None, None]:
    arg = ensure_ext(arg, desired_ext=expected_file_ext, override_ext=False)
    if create_file_if_necessary:
        ensure_directory_exists(arg)
    with open(arg, mode, encoding=encoding, **kwargs) as f:
        yield f


@contextmanager
def use_bytes_io(
    arg: ByteSource | ByteSink, expected_file_ext='.zip', mode='rb', create_file_if_necessary: bool = False
) -> Generator[io.BytesIO | BinaryIO, None, None]:
    if isinstance(arg, ReadOnlyByteSource):
        assert mode == 'rb'
        with open_readonly_byte_buffer(arg) as buf:
            yield buf
    elif isinstance(arg, str | os.PathLike):
        with open_file(
            arg,
            expected_file_ext=expected_file_ext,
            mode=mode,
            create_file_if_necessary=create_file_if_necessary,
            encoding=None,
        ) as buf:
            yield buf
    else:
        yield arg


@contextmanager
def use_string_io(
    arg: DataSource | DataSink, expected_file_ext, mode='r', encoding='utf-8', create_file_if_necessary=False, **kwargs
) -> Generator[io.TextIOBase | TextIO, None, None]:
    if isinstance(arg, ReadOnlyByteSource):
        assert mode == 'r'
        with open_readonly_byte_buffer(arg) as f:
            kwargs.pop('newline', None)
            yield io.TextIOWrapper(f, encoding=encoding, newline=None, **kwargs)
    elif isinstance(arg, str | os.PathLike):
        with open_file(
            arg,
            expected_file_ext=expected_file_ext,
            mode=mode,
            create_file_if_necessary=create_file_if_necessary,
            encoding=encoding,
            **kwargs,
        ) as f:
            yield f
    elif isinstance(arg, io.BufferedIOBase | BinaryIO):
        kwargs.pop('newline', None)
        yield io.TextIOWrapper(arg, encoding=encoding, newline=None, **kwargs)
    else:
        yield arg


@contextmanager
def use_for_pandas_io(arg: DataSource | DataSink) -> Generator[FilePath | TextIO | BinaryIO, None, None]:
    if isinstance(arg, ReadOnlyByteSource):
        with open_readonly_byte_buffer(arg) as bf:
            yield bf
    else:
        yield arg


def load_yaml(arg: DataSource, swallow_exceptions: bool = True) -> Any | None:
    from ruamel.yaml import YAML, YAMLError

    try:
        with use_string_io(arg, expected_file_ext='.yaml', mode='r') as source:
            with YAML() as yaml:
                return yaml.load(source)
    except YAMLError as e:
        if swallow_exceptions:
            return None
        else:
            raise e


def load_json(arg: DataSource, swallow_exceptions: bool = True) -> Any | None:
    import json
    from json import JSONDecodeError

    try:
        with use_string_io(arg, expected_file_ext='.json', mode='r') as source:
            return json.load(source)
    except JSONDecodeError as e:
        if swallow_exceptions:
            return None
        else:
            raise e


def load_serialized(
    arg: DataSource,
    swallow_exceptions: bool = True,
    use_yaml: bool | None = None,
    subpath: tuple[str, ...] | None = None,
) -> Any | None:
    if use_yaml is None:
        if isinstance(arg, str | os.PathLike):
            _, ext = os.path.splitext(arg)
            use_yaml = ext in {'.yaml', '.yml'}
    if use_yaml:
        obj = load_yaml(arg, swallow_exceptions=swallow_exceptions)
    else:
        obj = load_json(arg, swallow_exceptions=swallow_exceptions)
    if obj and subpath:
        return recursively_pick_from_mapping(obj, subpath)
    else:
        return obj


def dump_serialized(arg: Any, target: DataSink, use_yaml: bool | None = None) -> None:
    import json

    from ruamel.yaml import YAML

    if use_yaml is None:
        if isinstance(target, str | os.PathLike):
            _, ext = os.path.splitext(target)
            use_yaml = ext in {'.yaml', '.yml'}
    if use_yaml:
        with use_string_io(target, expected_file_ext='.yaml', mode='w') as sink:
            with YAML(output=sink) as yaml:
                yaml.indent(mapping=2, sequence=4, offset=2)
                yaml.dump(arg)
    else:
        with use_string_io(target, expected_file_ext='.json', mode='w') as sink:
            json.dump(arg, sink, indent=2)


def dump_serialized_to_str(arg: Any, use_yaml: bool = True) -> str:
    s = io.StringIO()
    dump_serialized(arg, s, use_yaml=use_yaml)
    return s.getvalue()


def load_pydantic[T: pydantic.BaseModel](
    model: type[T],
    source: DataSource,
    throw: bool = False,
    use_yaml: bool | None = None,
    subpath: tuple[str, ...] | None = None,
    by_alias=True,
    **kwargs,
) -> T | None:
    try:
        x = load_serialized(source, use_yaml=use_yaml, subpath=subpath, swallow_exceptions=False)
        return model.model_validate(x, by_alias=by_alias, **kwargs)
    except Exception as e:
        if throw:
            raise e
        else:
            return None


def dump_pydantic(
    model: pydantic.BaseModel, target: DataSink, use_yaml: bool | None = None, by_alias=True, round_trip=True, **kwargs
) -> None:
    serialized = model.model_dump(mode='json', by_alias=by_alias, round_trip=round_trip, **kwargs)
    dump_serialized(serialized, target, use_yaml=use_yaml)


def dump_pydantic_to_str(model: pydantic.BaseModel, use_yaml: bool = True, **kwargs) -> str:
    s = io.StringIO()
    dump_pydantic(model, s, use_yaml=use_yaml, **kwargs)
    return s.getvalue()
