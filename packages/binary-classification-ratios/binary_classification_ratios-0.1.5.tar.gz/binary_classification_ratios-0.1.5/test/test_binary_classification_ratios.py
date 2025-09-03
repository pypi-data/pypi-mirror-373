"""."""

import pytest

from binary_classification_ratios import BinaryClassificationRatios


@pytest.fixture
def bcr() -> BinaryClassificationRatios:
    """."""
    return BinaryClassificationRatios(tp=10, tn=9, fp=8, fn=7)


def test_classification_ratios_init() -> None:
    """."""
    bcr = BinaryClassificationRatios()
    assert bcr.get_f1_score() == pytest.approx(0.0)
    assert bcr.get_precision() == pytest.approx(0.0)
    assert bcr.get_recall() == pytest.approx(0.0)
    assert bcr.get_accuracy() == pytest.approx(0.0)


def test_classification_ratios_meaningful(bcr: BinaryClassificationRatios) -> None:
    """."""
    assert bcr.get_f1_score() == pytest.approx(0.5714285714285715)
    assert bcr.get_precision() == pytest.approx(0.5555555555555556)
    assert bcr.get_recall() == pytest.approx(0.5882352941176471)
    assert bcr.get_accuracy() == pytest.approx(0.5588235294117647)


def test_get_summary(bcr: BinaryClassificationRatios) -> None:
    """."""
    assert (
        bcr.get_summary()
        == """Confusion matrix: TP 10 TN 9 FP 8 FN 7
     accuracy 0.559
    precision 0.556
       recall 0.588
     f1-score 0.571
"""
    )


def test_assert_min(bcr: BinaryClassificationRatios) -> None:
    """."""
    bcr.assert_min(0.558, 0.555, 0.587)
    with pytest.raises(AssertionError):
        bcr.assert_min(0.560, 0.555, 0.587)

    with pytest.raises(AssertionError):
        bcr.assert_min(0.558, 0.557, 0.587)

    with pytest.raises(AssertionError):
        bcr.assert_min(0.558, 0.555, 0.589)
