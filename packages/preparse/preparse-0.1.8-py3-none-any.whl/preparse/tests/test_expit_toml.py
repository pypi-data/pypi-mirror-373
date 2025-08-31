import math
import tomllib
import unittest
from importlib import resources
from typing import *

import click
from click.testing import CliRunner

from preparse.core import *


class expit:

    def function(x: float) -> float:
        try:
            p = math.exp(-x)
        except OverflowError:
            p = float("+inf")
        return 1 / (1 + p)

    @PreParser(reconcilesorders=True, expectsposix=False).click()
    @click.command(add_help_option=False)
    @click.help_option("-h", "--help")
    @click.version_option("1.2.3", "-V", "--version")
    @click.argument("x", type=float)
    def main(x: float) -> None:
        """applies the expit function to x"""
        click.echo(expit.function(x))


class utils:
    def get_data() -> dict:
        text: str = resources.read_text("preparse.tests", "expit.toml")
        data: dict = tomllib.loads(text)
        return data

    def istestable(x: Any) -> bool:
        if not isinstance(x, float):
            return True
        if not math.isnan(x):
            return True
        return False


class TestMainFunction(unittest.TestCase):

    def parse(
        self: Self,
        *,
        query: Any,
        exit_code: Any,
        output: Any,
        prog: Any,
        stdout: Any,
        stderr: Any,
    ) -> None:
        runner: CliRunner = CliRunner()
        extra: dict = dict()
        extra["cli"] = expit.main
        extra["args"] = query
        if utils.istestable(prog):
            extra["prog_name"] = prog
        result: Any = runner.invoke(**extra)
        if utils.istestable(exit_code):
            self.assertEqual(exit_code, result.exit_code)
        if utils.istestable(output):
            self.assertEqual(output, result.output)
        if utils.istestable(stdout):
            self.assertEqual(stdout, result.stdout)
        if utils.istestable(stderr):
            self.assertEqual(stderr, result.stderr)

    def test_0(self: Self) -> None:
        data: dict = utils.get_data()
        name: str
        kwargs: dict
        for name, kwargs in data.items():
            with self.subTest(msg=name, **kwargs):
                self.parse(**kwargs)


if __name__ == "__main__":
    unittest.main()
