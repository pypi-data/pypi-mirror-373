import unittest
from typing import *

from preparse.core import *


class TestPreparse(unittest.TestCase):

    def test_nargs_enum(self: Self) -> None:
        self.assertEqual(Nargs.NO_ARGUMENT, 0)
        self.assertEqual(Nargs.REQUIRED_ARGUMENT, 1)
        self.assertEqual(Nargs.OPTIONAL_ARGUMENT, 2)

    def test_preparser_copy(self: Self) -> None:
        parser: PreParser = PreParser()
        parser_copy: PreParser = parser.copy()
        self.assertEqual(parser.optdict, parser_copy.optdict)

    def test_preparser_todict(self: Self) -> None:
        parser: PreParser = PreParser()
        result: Any = parser.todict()
        expected_keys: list = [
            "optdict",
            "prog",
        ]
        self.assertTrue(all(key in result for key in expected_keys))

    def test_preparser_click_decorator(self: Self) -> None:
        parser: PreParser = PreParser()
        click_decorator: Click = parser.click()
        self.assertIsInstance(click_decorator, Click)
        self.assertTrue(click_decorator.cmd)
        self.assertTrue(click_decorator.ctx)
        self.assertEqual(click_decorator.parser, parser)


if __name__ == "__main__":
    unittest.main()
