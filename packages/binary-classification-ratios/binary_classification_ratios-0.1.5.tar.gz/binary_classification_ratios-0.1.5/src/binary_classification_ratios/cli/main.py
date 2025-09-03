"""."""

from typing import Sequence, Union

from binary_classification_ratios import BinaryClassificationRatios

from .cmd_line import get_cmd_line


def run(args: Union[Sequence[str], None] = None) -> float:
    """."""
    cli = get_cmd_line(args)
    bcr = BinaryClassificationRatios(tp=cli.tp, tn=cli.tn, fp=cli.fp, fn=cli.fn)
    print(bcr.get_summary())
    return bcr.get_f1_score()


def main() -> None:
    """."""
    run()  # pragma: no cover
