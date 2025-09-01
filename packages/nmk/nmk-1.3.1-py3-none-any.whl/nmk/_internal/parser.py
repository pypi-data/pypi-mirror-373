import logging
from argparse import ZERO_OR_MORE, ArgumentParser, Namespace
from pathlib import Path

import argcomplete

from nmk import __version__
from nmk._internal.completion import ConfigCompleter, TasksCompleter

"""
nmk CLI parsing logic
"""


class NmkParser:
    def __init__(self):
        # Prepare parser
        self.parser = ArgumentParser(description="Next-gen make-like build system")

        # Version handling
        self.parser.add_argument("-V", "--version", action="version", version=f"nmk version {__version__}")

        # Tasks
        self.parser.add_argument("tasks", metavar="task", default=[], nargs=ZERO_OR_MORE, help="build task to execute").completer = TasksCompleter()  # type: ignore

        # Logging
        lg = self.parser.add_argument_group("logging options")
        ll = lg.add_mutually_exclusive_group()
        ll.add_argument(
            "-q",
            "--quiet",
            action="store_const",
            const=logging.WARNING,
            default=logging.INFO,
            dest="log_level",
            help="quiet mode (only warning/error messages)",
        )
        ll.add_argument("--info", action="store_const", const=logging.INFO, default=logging.INFO, dest="log_level", help="default mode")
        ll.add_argument(
            "-v",
            "--verbose",
            action="store_const",
            const=logging.DEBUG,
            default=logging.INFO,
            dest="log_level",
            help="verbose mode (all messages, including debug ones)",
        )
        lg.add_argument(
            "--log-file", metavar="L", default="{PROJECTDIR_NMK}/nmk.log", help="write logs to L (default: {PROJECTDIR_NMK}/nmk.log)"
        ).completer = argcomplete.completers.FilesCompleter(directories=True)  # type: ignore
        lg.add_argument("--no-logs", action="store_true", default=False, help="disable logging")
        lg.add_argument("--log-prefix", metavar="PREFIX", default=None, help="prefix for all log messages")

        # Root folder
        rg = self.parser.add_argument_group("root folder options")
        rg.add_argument(
            "-r", "--root", metavar="R", type=Path, default=None, help="root folder (default: virtual env parent)"
        ).completer = argcomplete.completers.DirectoriesCompleter()  # type: ignore
        rg.add_argument("--no-cache", action="store_true", default=False, help="clear cache before resolving references")

        # Project
        pg = self.parser.add_argument_group("project options")
        pg.add_argument(
            "-p", "--project", metavar="P", default="nmk.yml", help="project file (default: nmk.yml)"
        ).completer = argcomplete.completers.FilesCompleter(allowednames=["*.yml", "*.yaml"], directories=True)  # type: ignore

        # Config
        cg = self.parser.add_argument_group("config options")
        cg.add_argument("--config", metavar="JSON|K=V", action="append", help="contribute or override config item(s)").completer = ConfigCompleter(False)  # type: ignore
        cg.add_argument("--print", metavar="K", action="append", help="print required config item(s) and exit").completer = ConfigCompleter()  # type: ignore

        # Build
        bg = self.parser.add_argument_group("build options")
        bg.add_argument("--dry-run", action="store_true", default=False, help="list tasks to be executed and exit")
        bg.add_argument("--force", "-f", action="store_true", default=False, help="force tasks rebuild")
        bg.add_argument("--skip", dest="skipped_tasks", action="append", default=[], help="skip specified task").completer = TasksCompleter()  # type: ignore

        # Handle completion
        argcomplete.autocomplete(self.parser)

    def parse(self, argv: list[str]) -> Namespace:
        # Parse arguments
        return self.parser.parse_args(argv)
