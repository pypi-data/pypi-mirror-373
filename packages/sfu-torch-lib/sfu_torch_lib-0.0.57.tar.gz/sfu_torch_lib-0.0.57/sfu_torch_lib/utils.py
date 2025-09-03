from __future__ import annotations

import functools
import importlib
import re
from types import ModuleType
from typing import Callable, Iterable, Iterator, Sequence

import mlflow
from pytorch_lightning import LightningModule
from torch.nn import ELU, Identity, LeakyReLU, Module, ReLU, Sigmoid, Softmax, Tanh


class AttributeDict[T]:
    def __init__(self, dictionary: dict[str, T]) -> None:
        self.dictionary = dictionary

        for key, value in self.items():
            setattr(self, key.lower().replace(' ', '_'), value)

    def __getattr__(self, name):
        return getattr(self, name)

    def __getitem__(self, key):
        return self.dictionary[key]

    def __repr__(self):
        return repr(self.dictionary)

    def __len__(self):
        return len(self.dictionary)

    def __contains__(self, item):
        return item in self.dictionary

    def __iter__(self):
        return iter(self.dictionary)

    def __or__(self, other: AttributeDict[T]) -> AttributeDict[T]:
        return AttributeDict(self.dictionary | other.dictionary)

    def update(self, other: AttributeDict[T]) -> AttributeDict[T]:
        return self | other

    def keys(self):
        return self.dictionary.keys()

    def values(self):
        return self.dictionary.values()

    def items(self):
        return self.dictionary.items()


def get_pairs[T](items: Iterable[T]) -> Iterator[tuple[T, T]]:
    first = None

    for index, item in enumerate(items):
        if index % 2 == 0:
            first = item
        else:
            yield first, item  # type: ignore


def create_selector[T](indices: int | Sequence[int]) -> Callable[[Sequence[T]], T | tuple[T, ...]]:
    def select(items: Sequence[T]) -> T | tuple[T, ...]:
        if isinstance(indices, int):
            return items[indices]

        return tuple(items[index] for index in indices)

    return select


def to_list[T](*args: Sequence[T] | T) -> list[T]:
    items: list[T] = []

    for argument in args:
        if isinstance(argument, Sequence):
            items += argument
        else:
            items.append(argument)

    return items


def to_bool(value: str | None) -> bool | None:
    if value is None:
        return None

    if value == '0' or value.lower() == 'false':
        return False

    return bool(value)


def to_bool_or_false(value: str | None) -> bool:
    return to_bool(value) or False


def get_activation(name: str) -> Module:
    return {
        'elu': ELU,
        'identity': Identity,
        'relu': ReLU,
        'leaky_relu': LeakyReLU,
        'sigmoid': Sigmoid,
        'softmax': Softmax,
        'tanh': Tanh,
    }[name]


def get_class(model_type: str, default_module: ModuleType | None = None) -> type:
    if '.' in model_type:
        module_name, class_name = model_type.rsplit('.', maxsplit=1)
        module = importlib.import_module(module_name)

    elif default_module is not None:
        module = default_module
        class_name = model_type

    else:
        raise ValueError('default_module not provided')

    model_class = getattr(module, class_name)

    return model_class


def get_run_class(
    run_id: str,
    default_module: ModuleType | None = None,
    key: str = 'model-type',
) -> LightningModule:
    model_type = mlflow.get_run(run_id).data.params[key]

    model_class = get_class(model_type, default_module)

    assert isinstance(model_class, LightningModule)

    return model_class


def get_type_or_run_class(
    model_type: str | None = None,
    run_id: str | None = None,
    default_module: ModuleType | None = None,
    key: str = 'model-type',
) -> LightningModule:
    if model_type is not None:
        model_class = get_class(model_type, default_module)
        assert isinstance(model_class, LightningModule)

    else:
        assert run_id is not None
        model_class = get_run_class(run_id, default_module, key)

    return model_class


def parse_map_sequence[T](string: str, sequence_type: Callable[[str], T]) -> dict[str, Sequence[T]]:
    substrings = re.split(r'(?<=]),', string)

    output = {}

    for substring in substrings:
        key, value = substring.split(':')

        output[key] = list(map(sequence_type, value.strip('[]').split(',')))

    return output


parse_map_ints = functools.partial(parse_map_sequence, sequence_type=int)
parse_map_floats = functools.partial(parse_map_sequence, sequence_type=float)
parse_map_strings = functools.partial(parse_map_sequence, sequence_type=str)
