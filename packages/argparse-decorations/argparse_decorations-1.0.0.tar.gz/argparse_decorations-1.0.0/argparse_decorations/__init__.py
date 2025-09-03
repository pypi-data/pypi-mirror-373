# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import collections
import logging
import re
import sys
import types


# logging.basicConfig(level='DEBUG')

_initialized = False
_subparsers_added = False


def init(*args, **kwargs):
    global _initialized, _parser

    if not _initialized:
        _parser = ArgumentParser(*args, **kwargs)

        _initialized = True

    return _parser


_VERBOSITY_DEFAULT = 0  # CRITICAL


def make_verbosity_argument():
    _parser.add_argument('--verbosity', '-v', action='count',
                         default=_VERBOSITY_DEFAULT,
                         help='Verbosity level (up to 4 v\'s)')


class InvalidVersionException(Exception):

    error_message = '"version" must be an dictionary with at least "major", ' \
                    + '"minor" and "patch" keys or a string in format ' \
                    + '"major.minor.patch" (where major, minor and patch ' \
                    + 'are ints)'

    def __init__(self):
        super(InvalidVersionException, self).__init__(
                Exception, InvalidVersionException.error_message)


def make_version_command(version):
    def version_handler(full: bool):
        def format(raw):
            if isinstance(raw, str):
                return raw
            elif isinstance(raw, collections.abc.Iterable):
                return ', '.join([format(r) for r in raw])
            else:
                return str(raw)

        if not full:
            print('{major}.{minor}.{patch}'.format(**version))
        else:
            for key, raw_value in version.items():
                value = format(raw_value)
                print(f'{key}: {value}')

    if isinstance(version, str):
        data = re.findall(r'([0-9]+)(?:\.)?', version)

        if len(data) != 3:
            raise InvalidVersionException()

        version = {
                'major': data[0],
                'minor': data[1],
                'patch': data[2],
                }
    elif not isinstance(version, dict):
        raise InvalidVersionException()
    else:
        if \
                'major' not in version or \
                'minor' not in version or \
                'patch' not in version:
            raise InvalidVersionException()

    # FIXME If called before _subparsers initialization will bug
    parser = _subparsers.add_parser('version', help='Show version')
    parser.set_defaults(handler=version_handler)
    parser.add_argument('--full', '-f', action='store_true',
                        help='All version data')

    return parser


_first_level_commands = list()


class _CommandTreeLeaf(object):

    def __init__(self, name):
        self.name = name
        self.parser = None
        self.subparsers = None
        self.subcommands = list()

    def __repr__(self):
        return str(self.name)


class _AbstractDecoration(object):

    def __init__(self, *args, **kwargs):
        global _initialized

        if not _initialized:
            init(*args, **kwargs)

        self._handler = None

    def _class(self):
        return self.__class__.__name__

    def __call__(self, handler):
        logging.debug(f'in {self._class()} __call__ (of {self.name})')
        logging.debug(f'args: {handler}')

        self._handler = handler

        if isinstance(handler, types.FunctionType) \
           or isinstance(handler, ExtraArgs):
            global current_command
            current_command.parser.set_defaults(handler=handler)
            return handler

        return self

    def __str__(self):
        return f'{self._class()} of {self.name}'


class Command(_AbstractDecoration):

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO Não é legal fazer esse tipo de comparação, seria interessante ao
        # invés disso mudar a hierarquia dessas classes...
        global _subparsers_added
        if not _subparsers_added and not isinstance(self, RootCommand):
            global _parser, _subparsers
            _subparsers = _parser.add_subparsers()
            _subparsers_added = True

        logging.debug('in {self._class()} __init__')
        logging.debug('name: ' + (name or '<root command>'))

        global _first_level_commands
        global current_command
        pre_existing, current_command = Command._get_leaf_by_name(name)

        if not pre_existing:
            if name:
                current_command.parser = _subparsers.add_parser(name, *args, **kwargs)
            else:
                current_command.parser = _parser

        self.name = name

    @staticmethod
    def _get_leaf_by_name(name):
        global _first_level_commands
        for command in _first_level_commands:
            if command.name == name:
                return True, command

        newCommand = _CommandTreeLeaf(name)
        _first_level_commands.append(newCommand)
        return False, newCommand


class RootCommand(Command):

    def __init__(self, *args, **kwargs):
        logging.debug('in {self._class()} __init__')

        super().__init__(None, *args, **kwargs)

        super().__call__(None)


class SubCommand(_AbstractDecoration):

    def __init__(self, name, *args, **kwargs):
        super().__init__()

        logging.debug(f'in {self._class()} __init__')
        logging.debug(f'name: {name}')

        global current_command
        super_command = current_command
        pre_existing, current_command = SubCommand._get_leaf_by_name(name)

        if not pre_existing:
            if not super_command.subparsers:
                super_command.subparsers = super_command.parser.add_subparsers()
            current_command.parser = super_command.subparsers.add_parser(name, *args, **kwargs)

        self.name = name

    @staticmethod
    def _get_leaf_by_name(name):
        global current_command
        for command in current_command.subcommands:
            if command.name == name:
                return True, command

        newCommand = _CommandTreeLeaf(name)
        current_command.subcommands.append(newCommand)
        return False, newCommand


class Argument(_AbstractDecoration):

    def __init__(self, name, *args, **kwargs):
        super().__init__()

        logging.debug(f'in {self._class()} __init__')
        logging.debug('name: ' + str(name))

        global current_command
        if not current_command:
            _, current_command = Command._get_leaf_by_name(name)
        current_command.parser.add_argument(name, *args, **kwargs)

        self.name = name


class ExtraArgs(object):

    def __init__(self, *params):
        self.params = params
        self.extra_args = {}
        self._initialized = False

    def __call__(self, *args, **kwargs):
        if not self._initialized:
            self.method = args[0]
            self._initialized = True

            return self

        for param in ['verbosity', 'logger', 'handler']:
            if param in self.params:
                kwargs[param] = self.extra_args[param]

        return self.method(*args, **kwargs)


exception_handlers = list()


class ExceptionHandler(object):

    def __init__(self, method):
        exception_handlers.append(self)
        self.method = method

    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)


def _default_exception_handler(args, extra_args, exception):
    if extra_args.get('verbosity', 0) == 4:
        raise exception

    logging.error(exception)

    return 1


def parse(*args, **kwargs):
    parser_args = _parser.parse_args(*args, **kwargs)
    args = dict(parser_args.__dict__)

    extra_args = dict()

    for param in ['verbosity', 'logger', 'handler']:
        if param in args:
            extra_args[param] = args.pop(param)

    return args, extra_args


def _setup_logger(handler, verbosity):
    logger = logging.getLogger(handler.__module__)

    verbosity_levels = {
        0: "CRITICAL",
        1: "ERROR",
        2: "WARNING",
        3: "INFO",
        4: "DEBUG",
    }

    if verbosity not in verbosity_levels.keys():
        raise Exception(f'Invalid verbosity value ("{verbosity}"), pass '
                        'between 0 and 4')

    level = verbosity_levels[verbosity]
    logger.setLevel(level=level)

    logging.debug('Command logger setup to \"%s\"', level)

    return logger


def run(args, extra_args={}):
    handler = extra_args.get('handler', None)

    if not handler:
        _parser.print_help()
        return 0

    verbosity = extra_args.get('verbosity', _VERBOSITY_DEFAULT)
    extra_args['logger'] = _setup_logger(handler, verbosity)

    if isinstance(handler, ExtraArgs):
        handler.extra_args = extra_args

    try:
        return handler(**args)
    except Exception as e:
        if len(exception_handlers) == 0:
            result = _default_exception_handler(args, extra_args, e)
        else:
            for handler in exception_handlers:
                result = handler(args, extra_args, e)

        if isinstance(result, int):
            sys.exit(result)


def parse_and_run(*args, **kwargs):
    args, extra_args = parse(*args, **kwargs)
    return run(args, extra_args)


def finish():
    """
    No need to call this in production code, created for tests
    """
    global _first_level_commands, _initialized, _parser, _subparsers, \
        _subparsers_added, current_command

    _first_level_commands = list()
    _initialized = False
    _parser = None
    _subparsers = None
    _subparsers_added = False
    current_command = None
