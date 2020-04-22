import pathlib

import pytest


def run():
    file_path = pathlib.Path(__file__)

    pytest.main(['-x', file_path.parent.parent, '--flakes'])
