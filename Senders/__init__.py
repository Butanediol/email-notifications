import importlib
import inspect
import logging
import pkgutil

from Senders.base import BaseSender


def get_senders() -> list[BaseSender]:
    """Discover and instantiate all enabled senders in the Senders package."""
    senders = []

    for finder, module_name, _ in pkgutil.iter_modules(__path__):
        if module_name == 'base':
            continue

        module = importlib.import_module(f'{__name__}.{module_name}')

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, BaseSender) and cls is not BaseSender:
                if cls.enabled():
                    senders.append(cls())
                    logging.info(f'Sender enabled: {cls.__name__}')
                else:
                    logging.info(f'Sender disabled (not configured): {cls.__name__}')

    return senders
