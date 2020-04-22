import sys
import argparse
import os
import subprocess

import pytest
import dockercompose

from . import server
from . import test

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description=('Cryb'))
    subparsers = parser.add_subparsers(dest='entry_point')
    subparsers.add_parser('server')
    subparsers.add_parser('test')
    options = parser.parse_args(args)

    if options.entry_point == 'server':
        server.run()

    if options.entry_point == 'test':
        test.run()


if __name__ == '__main__':
    main()
