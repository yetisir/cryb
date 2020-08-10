import argparse

import requests_cache
import configurator
import redis

from . import utils, entrypoints


@utils.cli_args
def main(args=None):
    """[summary]

    Args:
        args (list of str, optional): CLI args which can be manually
        overridden. If None, args is grabbed from sys.argv. Defaults to None.
    """

    # create the primary parser
    parser = argparse.ArgumentParser(description='cryb')
    subparsers = parser.add_subparsers(dest='entry_point')
    subparsers.required = True

    # get list of entry_points
    entry_points = entrypoints.initialize()

    # add a subparser for each entry_point
    for entry_point in entry_points.values():
        subparser = subparsers.add_parser(
            entry_point.name, aliases=entry_point.aliases)
        entry_point.build_parser(subparser)

    # parse the entry point
    parameters = parser.parse_args(args)

    # run the specified entry point
    entry_point = entry_points.get(parameters.entry_point)
    entry_point.run(parameters)


if __name__ == '__main__':
    main()
