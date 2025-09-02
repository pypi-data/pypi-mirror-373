from importlib import import_module
from typing import Callable, Type, Union


def import_from_dotted_path(path: str) -> Union[Type, Callable]:
    *module_path, name = path.split(".")
    return getattr(import_module(".".join(module_path)), name)


def parse_signal_received_for_module(receiver_response) -> tuple[str, any]:
    for receiver, response in receiver_response:
        if response:
            yield receiver.__module__.split(".", 1)[0], response
