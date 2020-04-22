import pathlib

import pytest

from cryb import common


class TestEntryPoint(common.EntryPoint):
    name = 'test'
    description = 'Cryb Test Module'

    def run(self, options):
        file_path = pathlib.Path(__file__)
        pytest.main(['-x', file_path.parent.parent.as_posix(), '--flake8'])

    def build_parser(self, parser):
        pass

if __name__ == '__main__':
    TestEntryPoint.main()
