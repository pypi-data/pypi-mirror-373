from . import ArgparseDecorationsTestBase
from argparse_decorations import Command, parse_and_run, \
        make_version_command, InvalidVersionException
import io
from unittest.mock import patch


class TestMakeVersionCommand(ArgparseDecorationsTestBase):

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_version(self, mocked_stdout):
        # BUG Must have at least one command before creating version
        @Command('command')
        def handler():
            pass

        make_version_command('1.2.3')

        parse_and_run(['version'])

        out = mocked_stdout.getvalue()

        self.assertEqual(out, '1.2.3\n')

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_full_version(self, mocked_stdout):
        @Command('command')
        def handler():
            pass

        make_version_command({
            'major': 1,
            'minor': 2,
            'patch': 3,
            'git_hash': 'abcdef',
            'git_tags': ['v1.2.3', 'v1.2.2']
            })

        parse_and_run(['version', '--full'])

        out = mocked_stdout.getvalue().split('\n')

        self.assertEqual(out[0], 'major: 1')
        self.assertEqual(out[1], 'minor: 2')
        self.assertEqual(out[2], 'patch: 3')
        self.assertEqual(out[3], 'git_hash: abcdef')
        self.assertEqual(out[4], 'git_tags: v1.2.3, v1.2.2')
        self.assertEqual(out[5], '')
        self.assertEqual(len(out), 6)

    def test_version_invalid_string(self):
        @Command('command')
        def handler():
            pass

        with self.assertRaises(InvalidVersionException):
            make_version_command('_')

    def test_dict_version_without_major(self):
        @Command('command')
        def handler():
            pass

        with self.assertRaises(InvalidVersionException):
            make_version_command({
                'minor': 2,
                'patch': 3,
                })

    def test_dict_version_without_minor(self):
        @Command('command')
        def handler():
            pass

        with self.assertRaises(InvalidVersionException):
            make_version_command({
                'major': 1,
                'patch': 3,
                })

    def test_dict_version_without_patch(self):
        @Command('command')
        def handler():
            pass

        with self.assertRaises(InvalidVersionException):
            make_version_command({
                'major': 1,
                'minor': 2,
                })

    def test_non_dict_version(self):
        @Command('command')
        def handler():
            pass

        with self.assertRaises(InvalidVersionException):
            make_version_command(123)
