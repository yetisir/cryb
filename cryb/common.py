import argparse
from abc import ABC, abstractmethod

from cryb import utils


class EntryPoint(ABC):

    @utils.cli_args
    def main(self, args=None):
        parser = argparse.ArgumentParser(description=self.description)
        self.build_parser(parser)
        parameters = parser.parse_args(args)
        self.run(parameters)

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
