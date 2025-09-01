#! /usr/bin/env python3

import argparse
import sys

from danoan.journal_manager.cli import utils
from danoan.journal_manager.cli.commands import build, journal, setup, template


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create, edit and manage your mkdocs journals."
    )

    list_of_commands = [build, journal, setup, template]

    subparser_action = parser.add_subparsers(
        title="journal-manager subcommands"
    )
    for command in list_of_commands:
        command.get_parser(subparser_action)

    return parser


def main():
    utils.ensure_configuration_folder_exists()
    parser = get_parser()
    args = parser.parse_args()

    if "func" in args:
        args.func(**vars(args))
    else:
        if "subcommand_help" in args:
            args.subcommand_help()
        else:
            parser.print_help(sys.stdout)


if __name__ == "__main__":
    main()
