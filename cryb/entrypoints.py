from abc import ABC, abstractmethod

from . import worker


class EntryPoint(ABC):
    """Base class for CLI Entrypoints. This is an interface to
    help describe the commands and corresponding actions
    """

    aliases = []

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self):
        raise NotImplementedError

    @abstractmethod
    def run(self):
        raise NotImplementedError

    @abstractmethod
    def build_parser(self, parser):
        raise NotImplementedError


class Crawl(EntryPoint):
    name = 'crawl'
    description = 'Starts cryb crawler processes'

    def run(self, options):
        pass

    def build_parser(self, parser):
        pass


def initialize():
    """Initializes the entrypoints. Automatically instantiates all subclasses
    of common.Entrypoint"""

    entry_points = {}
    for cls in EntryPoint.__subclasses__():
        entry_points[cls.name] = cls()
        for alias in cls.aliases:
            entry_points[alias] = cls()
    return entry_points
