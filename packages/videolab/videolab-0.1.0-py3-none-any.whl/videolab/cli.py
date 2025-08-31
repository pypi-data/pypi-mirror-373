#!/usr/bin/env python3

# Copyright (C) 2025 Kian-Meng, Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""A console program to manipulate videos.

website: https://github.com/kianmeng/videolab
changelog: https://github.com/kianmeng/videolab/blob/master/CHANGELOG.md
issues: https://github.com/kianmeng/videolab/issues
"""

import argparse
import importlib
import pkgutil

import videolab.commands

def main(argv=None):
    """
    Main function to setup and run the CLI.
    """
    parser = argparse.ArgumentParser(
        prog="videolab",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # Discover and register subcommands
    for _, name, _ in pkgutil.iter_modules(videolab.commands.__path__):
        module = importlib.import_module(f"videolab.commands.{name}")
        if hasattr(module, "register_subcommand"):
            module.register_subcommand(subparsers)

    args = parser.parse_args(argv)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
