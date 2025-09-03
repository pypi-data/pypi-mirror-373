from . import ArgparseDecorationsTestBase
from argparse_decorations import RootCommand, Command, SubCommand, Argument, \
        ExtraArgs, parse, run, make_verbosity_argument


class TestDecorations(ArgparseDecorationsTestBase):

    def test_tests(self):
        self.assertTrue(True)

    def test_RootCommand(self):
        called = False

        @RootCommand()
        def handler():
            nonlocal called
            called = True

        args, extra_args = parse()

        run(args, extra_args)

        self.assertTrue(called)

    def test_RootCommand_with_Arguments(self):
        called = False

        @RootCommand()
        @Argument('--something', action='store_true')
        def handler(something):
            nonlocal called
            called = True

        args, extra_args = parse(['--something'])

        run(args, extra_args)

        self.assertTrue(called)

    def test_RootCommand_with_positional_argument(self):
        called = False

        @RootCommand()
        @Argument('argument')
        def handler(argument):
            nonlocal called
            called = True

        args, extra_args = parse(['value'])

        run(args, extra_args)

        self.assertTrue(called)

    def test_Command(self):
        called = False

        @Command('command')
        def handler():
            nonlocal called
            called = True

        args, extra_args = parse(['command'])

        run(args, extra_args)

        self.assertTrue(called)

    def test_call_handler_directly(self):
        @Command('command')
        def handler():
            return 31

        result = handler()

        self.assertEqual(result, 31)

    def test_SubCommand(self):
        called = False

        @Command('command')
        @SubCommand('add')
        def handler():
            nonlocal called
            called = True

        args, extra_args = parse(['command', 'add'])

        run(args, extra_args)

        self.assertTrue(called)

    def test_SubCommands_under_same_command(self):
        add_called = False
        sub_called = False

        @Command('command')
        @SubCommand('add')
        def add_handler():
            nonlocal add_called
            add_called = True

        @Command('command')
        @SubCommand('sub')
        def sub_handler():
            nonlocal sub_called
            sub_called = True

        args, extra_args = parse(['command', 'add'])

        run(args, extra_args)

        self.assertTrue(add_called)

        args, extra_args = parse(['command', 'sub'])

        run(args, extra_args)

        self.assertTrue(sub_called)

    def test_Argument(self):
        result = None

        @Command('add')
        @Argument('x', type=int)
        @Argument('y', type=int)
        def add(x, y):
            nonlocal result
            result = x + y

        args, extra_args = parse(['add', '2', '3'])

        run(args, extra_args)

        self.assertEqual(result, 5)

    def test_logging_setup(self):
        level = None

        @RootCommand()
        def handler():
            import logging
            logger = logging.getLogger(__name__)
            nonlocal level
            level = logging.getLevelName(logger.level)

        make_verbosity_argument()

        args, extra_args = parse(['-vv'])

        run(args, extra_args)

        self.assertEqual(level, 'WARNING')

    def test_extra_args(self):
        _verbosity = None
        _handler = None
        _logger = None

        @RootCommand()
        @ExtraArgs('verbosity', 'handler', 'logger')
        def __handler(verbosity, handler, logger):
            nonlocal _verbosity
            nonlocal _handler
            nonlocal _logger
            _verbosity = verbosity
            _handler = handler
            _logger = logger

        make_verbosity_argument()

        args, extra_args = parse(['-vv'])

        run(args, extra_args)

        self.assertEqual(_verbosity, 2)
        self.assertEqual(_handler, extra_args['handler'])
        self.assertIsNotNone(_logger)

    def test_logger_should_have_value_when_no_verbose(self):
        _logger = None

        @RootCommand()
        @ExtraArgs('logger')
        def __handler(logger):
            nonlocal _logger
            _logger = logger

        args, extra_args = parse()

        run(args, extra_args)

        self.assertIsNotNone(_logger)
