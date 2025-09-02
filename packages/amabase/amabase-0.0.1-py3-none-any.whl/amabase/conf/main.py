from __future__ import annotations

import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from types import ModuleType

from amabase.conf.commands.db import DbCommand
from amabase.conf.commands.settings import SettingsCommand
from amabase.django import DjangoCommand, LsDjangoCommand, WebCommand
from amabase.utils import add_command, get_description_text, use_default_subparser


def main(settings_module: ModuleType|str|None = None):
    from amabase import __doc__, __prog__, __version__

    script = Path(sys.argv[0])
    if script.name == '__main__.py':
        invoked_as = script.parent.name
    else:
        invoked_as = script.name

    parser = ArgumentParser(invoked_as, description=get_description_text(__doc__), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=f"{__prog__} {__version__}")
    parser.add_argument('-v', '--verbose', action='store_true', help="use DEBUG logging level")
    parser.add_argument('-y', '--yes', action='store_true', help="do not ask confirmation when performing sensible actions (e.g. auto install dependencies)")
    
    # Configure commands
    subparsers = parser.add_subparsers(title='commands')
    add_command(subparsers, SettingsCommand)
    add_command(subparsers, DbCommand)
    add_command(subparsers, LsDjangoCommand)
    add_command(subparsers, DjangoCommand)
    add_command(subparsers, WebCommand)

    # Parse command
    args = use_default_subparser(parser, 'django')
    args = vars(parser.parse_args(args))

    # Configure application
    from amabase.conf import settings
    settings.configure(settings_module, invoked_as=invoked_as, log_level='DEBUG' if args.pop('verbose') else None, yes=args.pop('yes'))
    
    # Run command
    if handle := args.pop('handle', None):
        handle(**args)
    else:
        print(f"Welcome to Amabase (version {__version__})")
