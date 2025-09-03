import inspect
import sys
from argparse import Namespace
from typing import Callable, Optional, List, Mapping, Any, Dict

import sfu_torch_lib.utils as utils


def get_positional_arguments(argv: Optional[List[str]] = None) -> List[str]:
    argv = argv if argv else sys.argv[1:]

    arguments = []

    for argument in argv:
        if argument.startswith('-'):
            break

        arguments.append(argument)

    return arguments


def get_keyword_arguments(argv: Optional[List[str]] = None) -> Dict[str, str]:
    argv = argv if argv else sys.argv[1:]

    num_positional_arguments = len(get_positional_arguments(argv))

    passed_arguments = {
        key.lstrip('-').replace('_', '-'): value
        for key, value
        in utils.get_pairs(argv[num_positional_arguments:])
        if key.startswith('-')
    }

    return passed_arguments


def get_script_parameters(function: Callable, ignore_keyword_arguments: bool = True) -> Dict[str, Any]:
    """
    Returns the arguments of a function with its values specified by the command line or its default values.
    Underscores in the name of the arguments are transformed to dashes.
    Can optionally filter out keyword arguments obtained through the command line.

    :param function: The function to inspect.
    :param ignore_keyword_arguments: Whether to filter out keyword command line arguments.
    :return: A map from argument names to default values.
    """
    positional_arguments, keyword_arguments = get_positional_arguments(), get_keyword_arguments()
    signature = inspect.signature(function)

    arguments = {}

    for index, (name, parameter) in enumerate(signature.parameters.items()):
        transformed_name = name.replace('_', '-')

        if index < len(positional_arguments):
            arguments[transformed_name] = positional_arguments[index]

        if not ignore_keyword_arguments and transformed_name in keyword_arguments:
            arguments[transformed_name] = keyword_arguments[transformed_name]

        elif transformed_name not in keyword_arguments and parameter.default != parameter.empty:
            arguments[transformed_name] = parameter.default

    return arguments


def flatten_dictionary(parameters: Mapping[Any, Any], delimiter: str = '/') -> Dict[str, Any]:
    def _dictionary_generator(input_dictionary, prefixes=None):
        prefixes = prefixes[:] if prefixes else []

        if isinstance(input_dictionary, Mapping):
            for key, value in input_dictionary.items():
                key = str(key)

                if isinstance(value, (Mapping, Namespace)):
                    value = vars(value) if isinstance(value, Namespace) else value
                    yield from _dictionary_generator(value, prefixes + [key])

                else:
                    yield prefixes + [key, value if value is not None else str(None)]

        else:
            yield prefixes + [input_dictionary if input_dictionary is None else str(input_dictionary)]

    return {delimiter.join(keys): val for *keys, val in _dictionary_generator(parameters)}
