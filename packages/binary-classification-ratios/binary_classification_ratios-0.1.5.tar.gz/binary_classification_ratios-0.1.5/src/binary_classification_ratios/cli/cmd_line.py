"""."""

from argparse import ArgumentParser
from typing import Sequence, Union


PROG = 'binary-classification-ratios'


class CmdLine:
    """."""

    def __init__(self) -> None:
        self.tp: int = 0
        self.tn: int = 0
        self.fp: int = 0
        self.fn: int = 0


def get_cmd_line(args: Union[Sequence[str], None] = None) -> CmdLine:
    """."""
    parser = ArgumentParser(PROG, f'{PROG} [OPTIONS]')
    parser.add_argument('-tp', type=int, default=0, help='Number of true positives.')
    parser.add_argument('-tn', type=int, default=0, help='Number of true negatives.')
    parser.add_argument('-fp', type=int, default=0, help='Number of false positives.')
    parser.add_argument('-fn', type=int, default=0, help='Number of false negatives.')
    namespace = CmdLine()
    parser.parse_args(args, namespace=namespace)
    return namespace
