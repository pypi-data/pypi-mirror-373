#!/usr/bin/env python3
import argparse
import logging
import os
import json
import logging
import os
import re
from time import sleep
import requests
import shutil
import subprocess
import sys
import uuid
import warnings

warnings.filterwarnings(
    "ignore", category=UserWarning, module="sentry_sdk.integrations.modules"
)

import psycopg
import sentry_sdk

from . import utils
from .commands.schema import PGDatabase, PGDatabaseEncoder

from .version import VERSION

BASESHIFT_ENV_VAR_NAME = "BASESHIFT_ENV"
DEFAULT_ENVIRONMENT = "production"
BASESHIFT_DSN_VAR_NAME = "BASESHIFT_SENTRY_DSN"
DEFAULT_DSN = (
    "https://a74ab2ee702347d3b4461e63a7049dc0@o604958.ingest.sentry.io/6604591"
)


sentry_sdk.init(
    dsn=os.environ.get(BASESHIFT_DSN_VAR_NAME, DEFAULT_DSN),
    environment=os.environ.get(BASESHIFT_ENV_VAR_NAME, DEFAULT_ENVIRONMENT),
    traces_sample_rate=0.0,
)


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, "%s: error: %s\n" % (self.prog, message))


logger = logging.getLogger(__name__)

DEFAULT_HOST = "https://app.dubhub.io"
DEFAULT_HOST_ENV = "BASESHIFT_HOST"


def main(cli_args=None):
    parser = argparse.ArgumentParser(description="Baseshift CLI")
    parser.add_argument("--version", action="version", version=VERSION)
    subparsers = parser.add_subparsers(dest="command", required=True)

    import pkgutil
    import inspect
    from . import commands
    from .commands.base import BaseCommand

    for _, name, _ in pkgutil.iter_modules(commands.__path__):
        if name == "base":
            continue
        module = __import__(f"baseshift.commands.{name}", fromlist=[""])
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseCommand) and obj is not BaseCommand:
                command_name = name
                command = obj()
                subparser = subparsers.add_parser(command_name)
                command.add_arguments(subparser)
                subparser.set_defaults(func=command.run)

    cli_args = cli_args or sys.argv[1:]
    args = parser.parse_args(cli_args)
    host = os.environ.get(DEFAULT_HOST_ENV, DEFAULT_HOST)

    if hasattr(args, "func"):
        args.func(args, host)
    else:
        logger.error("A command is required.")
        parser.print_help()
