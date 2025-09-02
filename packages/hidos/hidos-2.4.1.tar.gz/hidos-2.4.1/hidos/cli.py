# (c) 2024 E. Castedo Ellerman <castedo@castedo.com>
# Released under the MIT License (https://spdx.org/licenses/MIT)

"""Generic helper classes for command-line interfaces."""

from __future__ import annotations

from typing import Any, Protocol, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace


class CmdLine(Protocol):
    """CLI object instances that can be run per class-defined CLI."""

    @staticmethod
    def add_arguments(subparser: ArgumentParser) -> None: ...

    def run(self) -> int: ...


class SubCmd:
    """Helper class for running CmdLine objects with a CLI that has a subcommand."""

    @classmethod
    def add_arguments(klass, parser: ArgumentParser) -> None: ...

    @classmethod
    def cmd_map(klass, parser: ArgumentParser) -> SubCmd.Map:
        return SubCmd.Map(parser, klass.__name__)

    class Map:
        def __init__(self, parser: ArgumentParser, arg_key: str):
            self.subparsers = parser.add_subparsers(required=True)
            self.arg_key = arg_key

        def add(self, name: str, klass: type[CmdLine | SubCmd]) -> SubCmd.Map:
            subparser = self.subparsers.add_parser(name, help=klass.__doc__)
            klass.add_arguments(subparser)
            func = klass.make_cmd_line if issubclass(klass, SubCmd) else klass
            subparser.set_defaults(**{self.arg_key: func})
            return self

    @classmethod
    def make_cmd_line(klass, **vargs: Any) -> CmdLine:
        func = vargs.pop(klass.__name__)
        return cast(CmdLine, func(**vargs))

    @classmethod
    def run_cmd_line(klass, parsed_args: Namespace) -> int:
        return klass.make_cmd_line(**vars(parsed_args)).run()
