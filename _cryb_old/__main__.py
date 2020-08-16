import sys
import argparse

from . import server, crawl, test


def main(args=None):
    # allow main function to be called from cli or programmatically
    if args is None:
        args = sys.argv[1:]

    # create the primary parser
    parser = argparse.ArgumentParser(description='Cryb')
    subparsers = parser.add_subparsers(dest='entry_point')

    # get list of entry_points
    entry_points = [
        server.ServerEntryPoint(),
        crawl.CrawlEntryPoint(),
        test.TestEntryPoint(),
    ]

    # map entry point name to entry point object for easier access
    entry_point_map = {
            entry_point.name: entry_point for entry_point in entry_points}

    # add a subparser for each entry_point
    for entry_point in entry_points:
        subparser = subparsers.add_parser(entry_point.name)
        entry_point.build_parser(subparser)

    # parse the entry point
    parameters = parser.parse_args(args)

    # run the specified entry point
    entry_point = entry_point_map.get(parameters.entry_point)
    entry_point.run(parameters)


if __name__ == '__main__':
    main()
