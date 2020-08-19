from abc import ABC, abstractmethod
import asyncio

from . import worker
from .crawlers import coingecko, fourchan


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
        print('Starting')
        loop = asyncio.get_event_loop()
        # coingecko_coins = coingecko.Coins()
        fourchan_boards = fourchan.Boards()
        # loop.run_until_complete(coingecko_coins.get())
        loop.run_until_complete(fourchan_boards.get())
        exit()

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
