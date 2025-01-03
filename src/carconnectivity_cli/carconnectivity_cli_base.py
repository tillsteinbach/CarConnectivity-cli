"""Module containing the commandline interface for the carconnectivity package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum
import sys
import os
import argparse
import logging
import tempfile
import cmd
import json
import time
from datetime import datetime

from carconnectivity import carconnectivity, errors, util, objects, attributes, observable
from carconnectivity._version import __version__ as __carconnectivity_version__

from carconnectivity_cli._version import __version__

if TYPE_CHECKING:
    from typing import Literal, List
    from carconnectivity.objects import GenericObject
    from carconnectivity.attributes import GenericAttribute

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
DEFAULT_LOG_LEVEL = "ERROR"

LOG = logging.getLogger("carconnectivity-cli")


class Formats(Enum):
    """
    Formats is an enumeration that defines the output formats supported by the application.

    Attributes:
        STRING (str): Represents the string format.
        JSON (str): Represents the JSON format.
    """
    STRING = 'string'
    JSON = 'json'

    def __str__(self) -> str:
        return self.value


def main() -> None:  # noqa: C901 # pylint: disable=too-many-statements,too-many-branches,too-many-locals
    """
    Entry point for the carconnectivity-cli command-line interface.

    This function sets up the argument parser, handles logging configuration, and processes commands
    such as 'list', 'get', 'set', 'save', and 'shell'. It interacts with the CarConnectivity service
    to perform various operations based on the provided arguments.

    Commands:
        - list: Lists available resource IDs and exits.
        - get: Retrieves resources by ID and exits.
        - set: Sets resources by ID and exits.
        - save: Saves resources by ID to a file.
        - shell: Starts the WeConnect shell.

    Arguments:
        --version: Displays the version of the CLI and CarConnectivity.
        config: Path to the configuration file.
        --tokenfile: File to store the token (default: system temp directory).
        -v, --verbose: Increases logging verbosity.
        --logging-format: Specifies the logging format (default: '%(asctime)s:%(levelname)s:%(message)s').
        --logging-date-format: Specifies the logging date format (default: '%Y-%m-%dT%H:%M:%S%z').
        --hide-repeated-log: Hides repeated log messages from the same module.
    """
    parser = argparse.ArgumentParser(
        prog='carconectivity-cli',
        description='Commandline Interface to interact with Car Services of various brands')
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {__version__} (using CarConnectivity {__carconnectivity_version__})')
    parser.add_argument('config', help='Path to the configuration file')

    default_temp = os.path.join(tempfile.gettempdir(), 'carconnectivity.token')
    parser.add_argument('--tokenfile', help=f'file to store token (default: {default_temp})', default=default_temp)
    default_cache_temp = os.path.join(tempfile.gettempdir(), 'carconnectivity.cache')
    parser.add_argument('--cachefile', help=f'file to store cache (default: {default_cache_temp})', default=default_cache_temp)

    logging_group = parser.add_argument_group('Logging')
    logging_group.add_argument('-v', '--verbose', action="append_const", help='Logging level (verbosity)', const=-1,)
    logging_group.add_argument('--logging-format', dest='logging_format', help='Logging format configured for python logging '
                               '(default: %%(asctime)s:%%(module)s:%%(message)s)', default='%(asctime)s:%(levelname)s:%(message)s')
    logging_group.add_argument('--logging-date-format', dest='logging_date_format', help='Logging format configured for python logging '
                               '(default: %%Y-%%m-%%dT%%H:%%M:%%S%%z)', default='%Y-%m-%dT%H:%M:%S%z')
    logging_group.add_argument('--hide-repeated-log', dest='hide_repeated_log', help='Hide repeated log messages from the same module', action='store_true')

    parser.set_defaults(command='shell')

    subparsers = parser.add_subparsers(title='commands', description='Valid commands',
                                       help='The following commands can be used')
    parser_list: argparse.ArgumentParser = subparsers.add_parser('list', aliases=['l'], help='List available ressource ids and exit')
    parser_list.add_argument('-s', '--setters', help='List attributes that can be set', action='store_true')
    parser_list.set_defaults(command='list')
    parser_get: argparse.ArgumentParser = subparsers.add_parser('get', aliases=['g'], help='Get ressources by id and exit')
    parser_get.add_argument('id', metavar='ID', type=str, help='Id to fetch')
    parser_get.add_argument('--format', type=Formats, default=Formats.STRING, help='Output format', choices=list(Formats))
    parser_get.set_defaults(command='get')
    parser_set: argparse.ArgumentParser = subparsers.add_parser('set', aliases=['s'], help='Set ressources by id and exit')
    parser_set.add_argument('id', metavar='ID', type=str, help='Id to set')
    parser_set.add_argument('value', metavar='VALUE', type=str, help='Value to set')
    parser_set.set_defaults(command='set')
    parser_save: argparse.ArgumentParser = subparsers.add_parser('save', help='Save ressources by id to file')
    parser_save.add_argument('id', metavar='ID', type=str, help='Id to save')
    parser_save.add_argument('filename', metavar='FILENAME', type=str, help='File to save to')
    parser_events = subparsers.add_parser(
        'events', aliases=['e'], help='Continously retrieve events and show on console')
    parser_events.set_defaults(command='events')
    parser_shell: argparse.ArgumentParser = subparsers.add_parser(
        'shell', aliases=['sh'], help='Start WeConnect shell')
    parser_shell.set_defaults(command='shell')

    args = parser.parse_args()
    log_level = LOG_LEVELS.index(DEFAULT_LOG_LEVEL)
    for adjustment in args.verbose or ():
        log_level = min(len(LOG_LEVELS) - 1, max(log_level + adjustment, 0))

    logging.basicConfig(level=LOG_LEVELS[log_level], format=args.logging_format, datefmt=args.logging_date_format)
    if args.hide_repeated_log:
        for handler in logging.root.handlers:
            handler.addFilter(util.DuplicateFilter())

    try:  # pylint: disable=too-many-nested-blocks
        with open(file=args.config, mode='r', encoding='utf-8') as config_file:
            config_dict = json.load(config_file)
            car_connectivity = carconnectivity.CarConnectivity(config=config_dict, tokenstore_file=args.tokenfile, cache_file=args.cachefile)

            if args.command == 'shell':
                try:
                    car_connectivity.startup()
                    CarConnectivityShell(car_connectivity).cmdloop()
                except KeyboardInterrupt:
                    pass
            elif args.command == 'list':
                car_connectivity.fetch_all()
                all_elements: List[GenericAttribute] = car_connectivity.get_attributes(recursive=True)
                for element in all_elements:
                    if args.setters:
                        if isinstance(element, attributes.ChangeableAttribute):
                            print(element.get_absolute_path())
                    else:
                        print(element.get_absolute_path())
            elif args.command == 'get':
                car_connectivity.fetch_all()
                element: carconnectivity.GenericObject | objects.GenericAttribute | bool = car_connectivity.get_by_path(args.id)
                if element:
                    if args.format == Formats.STRING:
                        if isinstance(element, dict):
                            print('\n'.join([str(value) for value in element.values()]))
                        else:
                            print(element)
                    # elif args.format == Formats.JSON:
                    #     print(element.toJSON())
                    else:
                        print('Unknown format')
                        sys.exit('Unknown format')
                else:
                    print(f'id {args.id} not found', file=sys.stderr)
                    sys.exit('id not found')
            elif args.command == 'set':
                car_connectivity.fetch_all()
                element: carconnectivity.GenericObject | objects.GenericAttribute | bool = car_connectivity.get_by_path(args.id)
                if element:
                    try:
                        if isinstance(element, attributes.ChangeableAttribute):
                            element.value = args.value
                        else:
                            print(f'id {args.id} cannot be set.  You can see all changeable entries with "list -s', file=sys.stderr)
                    except ValueError as value_error:
                        print(f'id {args.id} cannot be set: {value_error}', file=sys.stderr)
                        sys.exit('id cannot be set')
                    except NotImplementedError:
                        print(f'id {args.id} cannot be set. You can see all changeable entries with "list -s"', file=sys.stderr)
                        sys.exit('id cannot be set')
                    except errors.SetterError as err:
                        print(f'id {args.id} cannot be set: {err}', file=sys.stderr)
                        sys.exit('id cannot be set')
                else:
                    print(f'id {args.id} not found', file=sys.stderr)
                    sys.exit('id not found')
            elif args.command == 'events':
                car_connectivity.startup()
                def observer(element, flags):
                    if flags & observable.Observable.ObserverEvent.ENABLED:
                        print(str(datetime.now()) + ': ' + element.get_absolute_path() + ': new object created')
                    elif flags & observable.Observable.ObserverEvent.DISABLED:
                        print(str(datetime.now()) + ': ' + element.get_absolute_path() + ': object not available anymore')
                    elif flags & observable.Observable.ObserverEvent.VALUE_CHANGED:
                        print(str(datetime.now()) + ': ' + element.get_absolute_path() + ': new value: ' + str(element))
                    elif flags & observable.Observable.ObserverEvent.UPDATED_NEW_MEASUREMENT:
                        print(str(datetime.now()) + ': ' + element.get_absolute_path()
                              + ': was updated from vehicle but did not change: ' + str(element))
                    elif flags & observable.Observable.ObserverEvent.UPDATED:
                        print(str(datetime.now()) + ': ' + element.get_absolute_path()
                              + ': was updated from server but did not change: ' + str(element))
                    else:
                        print(str(datetime.now()) + ' (' + str(flags) + '): '
                              + element.get_absolute_path() + ': ' + str(element))
                car_connectivity.add_observer(observer, observable.Observable.ObserverEvent.ALL,
                                              priority=observable.Observable.ObserverPriority.USER_MID)
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    LOG.info('Keyboard interrupt received, shutting down...')
            else:
                LOG.error('command not implemented')
                sys.exit('command not implemented')

            car_connectivity.shutdown()
    except json.JSONDecodeError as e:
        LOG.critical('Could not load configuration file %s (%s)', args.config, e)
        sys.exit('Could not load configuration file')
    except errors.AuthenticationError as e:
        LOG.critical('There was a problem when authenticating with one or multiple services: %s', e)
        sys.exit('There was a problem when communicating with one or multiple services')
    except errors.APICompatibilityError as e:
        LOG.critical('There was a problem when communicating with one or multiple services.'
                     ' If this problem persists please open a bug report: %s', e)
        sys.exit('There was a problem when communicating with one or multiple services')
    except errors.RetrievalError as e:
        LOG.critical('There was a problem when communicating with one or multiple services: %s', e)
        sys.exit('There was a problem when communicating with one or multiple services')
    except errors.ConfigurationError as e:
        LOG.critical('There was a problem with the configuration: %s', e)
        sys.exit('There was a problem with the configuration')
    except KeyboardInterrupt:
        sys.exit("killed")


class CarConnectivityShell(cmd.Cmd):
    """
    CarConnectivityShell is a command-line interface (CLI) shell for interacting with car connectivity data.

    Attributes:
        prompt (str): The command prompt string.
        intro (str): The introductory message displayed when the shell starts.
        car_connectivity (Any): The car connectivity object to interact with.
        pwd (Any): The current working directory within the car connectivity data.

    Methods:
        __init__(car_connectivity): Initializes the shell with the given car connectivity object.
        set_prompt(path): Sets the command prompt based on the given path.
        help_exit(): Displays help information for the 'exit' command.
        do_exit(arguments): Exits the shell.
        help_cd(): Displays help information for the 'cd' command.
        do_cd(arguments): Changes the current working directory.
        complete_cd(text, line, begidx, endidx): Provides tab completion for the 'cd' command.
        help_ls(): Displays help information for the 'ls' command.
        do_ls(arguments): Lists subelements of the current path.
        help_pwd(): Displays help information for the 'pwd' command.
        do_pwd(arguments): Displays the current path.
        help_update(): Displays help information for the 'update' command.
        do_update(arguments): Updates the data from the server.
        help_cat(): Displays help information for the 'cat' command.
        do_cat(arguments): Prints the content of the current or specified element.
        help_find(): Displays help information for the 'find' command.
        do_find(arguments): Lists all elements recursively.
        default(line): Handles unrecognized commands.
        do_EOF(): Exits the shell on EOF (Ctrl-D).
        help_EOF(): Displays help information for the EOF command.
    """
    prompt = 'error'
    intro = "Welcome! Type ? to list commands"

    def __init__(self, car_connectivity: carconnectivity.CarConnectivity) -> None:
        self.car_connectivity: carconnectivity.CarConnectivity = car_connectivity
        self.pwd: GenericObject | GenericAttribute = car_connectivity

        super().__init__()
        # Set the prompt to the current path
        self.set_prompt(self.car_connectivity.get_absolute_path())

    def set_prompt(self, path) -> None:
        """
        Sets the command prompt for the CarConnectivityShell.

        Args:
            path (str): The current path to be displayed in the prompt. If an empty string is provided, it defaults to '/'.

        """
        if path == '':
            path = '/'
        CarConnectivityShell.prompt = f'ccs:{path}$'

    def help_exit(self) -> None:
        """
        Prints the help message for the 'exit' command.

        This method provides information on how to exit the application,
        including the shorthand commands: 'x', 'q', and 'Ctrl-D'.
        """
        print('exit the application. Shorthand: x q Ctrl-D.')

    def do_exit(self, arguments) -> Literal[True]:
        """
        Exits the CLI application.

        Args:
            arguments: The arguments passed to the command. This parameter is not used.

        Returns:
            bool: Always returns True to indicate the command should exit.
        """
        del arguments
        print("Bye")
        return True

    def help_cd(self):
        """
        Prints the help message for the 'cd' command.

        This method is used to provide help information about changing the location
        in the tree structure.
        """
        print('change location in tree')

    def do_cd(self, arguments):
        """
        Change the current directory to the specified path.

        Args:
            arguments (str): The path to change to. If None or an empty string is provided,
                             the path will default to '/'.

        Behavior:
            - If the provided path starts with '/', it is treated as an absolute path.
            - If the provided path does not start with '/', it is treated as a relative path
              from the current directory.
            - If the specified path exists and is accessible, the current directory is updated
              to the new path and the prompt is set accordingly.
            - If the specified path does not exist or is not accessible, an error message is printed.

        Example:
            do_cd('/new/path')
            do_cd('relative/path')
        """
        # If no arguments are provided, set the path to '/'
        if arguments is None or arguments == '':
            arguments = '/'
        # If the path starts with '/', treat it as an absolute path
        if arguments.startswith('/'):
            path = arguments
        else:
            path = f'{self.pwd.get_absolute_path()}/{arguments}'
        # Get the object at the specified path
        new_pwd = self.car_connectivity.get_by_path(path)
        # If the object exists and is accessible, update the current directory and prompt
        if new_pwd is not None and new_pwd is not False:
            self.pwd = new_pwd
            path = self.pwd.get_absolute_path()
            if path == '':
                path = '/'
            self.set_prompt(path)
        else:
            # Print an error message if the path does not exist or is not accessible
            print(f'*** {arguments} does not exist or is not accessible')

    def complete_cd(self, text, line, begidx, endidx):
        """
        Autocompletion method for the 'cd' command.

        This method provides suggestions for directory names based on the current input text.
        If the input text starts with '/', it suggests absolute paths from the root directory.
        Otherwise, it suggests directory IDs from the current working directory.

        Args:
            text (str): The current input text for the 'cd' command.
            line (str): The entire input line (unused).
            begidx (int): The beginning index of the input text (unused).
            endidx (int): The ending index of the input text (unused).

        Returns:
            list: A list of suggested directory names or paths.
        """
        del line
        del begidx
        del endidx
        if text.startswith('/'):
            # Return absolute paths from the root directory
            root: carconnectivity.GenericObject | objects.GenericAttribute = self.pwd.get_root()
            if isinstance(root, objects.GenericObject):
                return [child.get_absolute_path() for child in root.children if child.get_absolute_path().startswith(text)]
        # Return directory IDs from the current working directory
        if isinstance(self.pwd, objects.GenericObject):
            return [child.id for child in self.pwd.children if child.id.startswith(text)]
        return []

    def help_ls(self):
        """
        Prints the help message for the 'ls' command

        This method is intended to provide help or guidance to the user about the 'ls' command,
        which lists subelements of the current path.
        """
        print('list subelements of current path')

    def do_ls(self, arguments):
        """
        Lists the contents of the current directory.

        Args:
            arguments: Command-line arguments (not used).

        Prints:
            The parent directory indicator ('..') if the current directory has a parent.
            The IDs of the children of the current directory.
        """
        del arguments
        if self.pwd.parent is not None:
            print('..')
        if isinstance(self.pwd, objects.GenericObject):
            for child in self.pwd.children:
                print(child.id)

    def help_pwd(self):
        """
        Prints the help message for the 'pwd' command.

         This method is intended to provide help or guidance to the user about the 'pwd' command,
        which displays the current path.
        """
        print('show current path')

    def do_pwd(self, arguments):
        """
        Prints the current working directory.

        Args:
            arguments: Command line arguments (not used).

        Returns:
            None
        """
        del arguments
        path = self.pwd.get_absolute_path()
        if path == '':
            path = '/'
        print(path)

    def help_update(self):
        """
        Prints the help message for the 'update' command.

        This method provides a simple help message for the update command.
        """
        print('update the data from the server')

    def do_update(self, arguments):
        """
        Updates the car connectivity data by fetching all available data.

        Args:
            arguments: Command-line arguments passed to the update command.
        """
        del arguments
        self.car_connectivity.fetch_all()
        print('update done')

    def help_cat(self):
        """
        Prints the help message for the 'cat' command.

        This method is used to display the help information related to the cat command that prints content.
        """
        print('Print content')

    def do_cat(self, arguments):
        """
        Display the content of a specified path.

        If no arguments are provided, this method prints the content of the current working directory.
        If a path is provided as an argument, it prints the content of the specified path
        if it exists and is accessible. Otherwise, it prints an error message.

        Args:
            arguments (str): The path to the element to be displayed. If None or empty,
                             the current working directory is displayed.
        """
        if arguments is None or arguments.strip() == '':
            print(str(self.pwd))
        else:
            element = self.pwd.get_by_path(arguments.strip())
            if element is not None and element is not False:
                print(str(element))
            else:
                print(f'*** {arguments} does not exist or is not accessible')

    def help_find(self):
        """
        Prints a message describing the functionality of the 'find' command.

        This method provides a brief description of what the 'find' command does,
        which is to list all elements recursively.
        """
        print('Find lists all elements recursively')

    def do_find(self, arguments):
        """
        Finds and prints the absolute paths of attributes in the current working directory.

        Args:
            arguments (str): Command line arguments. If '-s' is passed, only attributes
                             that are changeable will be printed.

        Returns:
            None
        """
        setters = bool(arguments.strip() == '-s')
        all_elements = self.pwd.get_attributes(recursive=True)
        for element in all_elements:
            if setters:
                if isinstance(element, attributes.ChangeableAttribute):
                    print(element.get_absolute_path())
            else:
                print(element.get_absolute_path())

    def default(self, line):
        """
        Handle the default case for unrecognized commands.

        If the input line is 'x' or 'q', it triggers the exit command.
        Otherwise, it calls the default method of the superclass.

        Args:
            line (str): The input command line.

        Returns:
            The result of the exit command if 'x' or 'q' is input, otherwise the result of the superclass's default method.
        """
        if line in ('x', 'q'):
            self.do_exit(line)
            return None
        return super().default(line)

    do_EOF = do_exit
    help_EOF = help_exit
