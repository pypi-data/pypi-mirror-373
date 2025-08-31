"""GitLab packages main module"""

import logging
import sys

from gitlab.cli_handler import CLIHandler


def cli() -> int:
    """
    Runs the main program of the glpkg.

    Uses arguments from command line and executes the given command.

    Return
    ------
    int
        Zero when everything is fine, non-zero otherwise.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[logging.FileHandler("glpkg.log")],  # , logging.StreamHandler()],
    )
    handler = CLIHandler()
    return handler.do_it()


if __name__ == "__main__":
    sys.exit(cli())
