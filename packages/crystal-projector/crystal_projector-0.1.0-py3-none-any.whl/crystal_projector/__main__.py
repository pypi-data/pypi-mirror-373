import argparse
import os
import sys
import typing

import crystal_projector


def main(argv: typing.List[str] = sys.argv) -> int:
    parser = argparse.ArgumentParser(
        os.path.basename(argv[0]), description="Manipulate Crystal Project data."
    )

    parser.add_argument(
        "--version", "-v", action="store_true", help="show version and exit"
    )

    args = parser.parse_args(argv[1:])

    if args.version:
        print(crystal_projector.__version__)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
