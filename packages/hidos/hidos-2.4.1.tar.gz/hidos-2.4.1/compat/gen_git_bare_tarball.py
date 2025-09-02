#!/usr/bin/env python3

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from hidos.cache import make_git_bare_tarball


def main(args: Any = None) -> int:
    parser = ArgumentParser()
    parser.add_argument("repo", type=str, help="git repository")
    parser.add_argument("dest", type=Path, help="Tarball destination path")
    args = parser.parse_args()
    make_git_bare_tarball(args.repo, args.dest)
    return 0


if __name__ == "__main__":
    exit(main())
