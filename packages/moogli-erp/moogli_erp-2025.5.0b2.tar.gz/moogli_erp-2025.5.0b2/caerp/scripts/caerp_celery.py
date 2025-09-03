"""
Script permettant le lancement de task celery depuis la ligne de commande
caerp-celery /config.ini run task_path option1 option2 ...

e.g:

    caerp-celery /config.ini run caerp.tasks.locks.release_lock_after_commit invoice_number
"""
import sys
import argparse
import importlib
from pyramid.paster import bootstrap

from .utils import argparse_command, CommandRegistry, AbstractCommand


class RunCommand(AbstractCommand):
    """Run a celery task from the command line"""

    name = "run"

    description = "Run a celery task from the command line"

    @classmethod
    def add_arguments(cls, parser) -> None:
        parser.add_argument(
            "command",
            help="chemin python de la commande à lancer "
            "(caerp_celery.tasks.locks.release_lock_task)",
        )
        parser.add_argument(
            "options",
            metavar="O",
            type=str,
            nargs="*",
            help="options to be passed to the task",
        )

    def __call__(self, arguments: argparse.Namespace, env: dict):
        task_path = arguments.command
        task_module, task_name = task_path.rsplit(".", 1)
        task_module = importlib.import_module(task_module)
        task = getattr(task_module, task_name)
        task.delay(*arguments.options)


class CaerpCeleryCommandsRegistry(CommandRegistry):
    BASE_COMMANDS = [RunCommand]
    EXTRA_COMMANDS = []
    description = "CAERP celery administration tool"


def celery_command_entry_point():
    def callback(arguments, env):
        func = CaerpCeleryCommandsRegistry.get_command(arguments.subcommand)
        return func(arguments, env)

    try:
        try:
            # We need to bootstrap the app in order to collect commands registered by
            # plugins. Even required to build the doc.
            ini_file = sys.argv[1]
            pyramid_env = bootstrap(ini_file)
            parser = CaerpCeleryCommandsRegistry.get_argument_parser()
            return argparse_command(callback, parser, pyramid_env)
        except IndexError:
            print("No ini file specified, plugin commands won't be listed")
            sys.exit(1)
    finally:
        pass
