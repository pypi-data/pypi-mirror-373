"""
This module provides the `BinaryClassificationRatios` class, which is used to calculate
and summarize classification metrics such as accuracy, precision, recall, and F1-score.
"""


class BinaryClassificationRatios(object):
    """
    A class to compute the binary classification quality metrics.

    Attributes:
        tp: Number of true positives.
        tn: Number of true negatives.
        fp: Number of false positives.
        fn: Number of false negatives.
    """

    def __init__(self, *, tp: int = 0, tn: int = 0, fp: int = 0, fn: int = 0) -> None:
        """Initializes a new instance with all zero values."""
        self.tp = tp
        self.tn = tn
        self.fp = fp
        self.fn = fn

    def get_summary(self) -> str:
        """Return a summary of the classification metrics, including accuracy,
           precision, recall, and F1-score.

        Returns:
            str: A formatted string summarizing the classification metrics.
        """
        cc = self
        return (
            f'Confusion matrix: TP {cc.tp} TN {cc.tn} FP {cc.fp} FN {cc.fn}\n'
            f'     accuracy {cc.get_accuracy():.3f}\n'
            f'    precision {cc.get_precision():.3f}\n'
            f'       recall {cc.get_recall():.3f}\n'
            f'     f1-score {cc.get_f1_score():.3f}\n'
        )

    def get_precision(self) -> float:
        """Calculate the Precision.

        Returns:
            float: The precision value, or 0.0 if the denominator is zero.
        """
        assert self.tp >= 0
        assert self.fp >= 0
        num_pos = self.tp + self.fp
        return self.tp / num_pos if num_pos > 0 else 0.0

    def get_recall(self) -> float:
        """Calculate the Recall.

        Returns:
            float: The recall value, or 0.0 if the denominator is zero.
        """
        assert self.tp >= 0
        assert self.fn >= 0
        num_corr = self.tp + self.fn
        return self.tp / num_corr if num_corr > 0 else 0.0

    def get_f1_score(self) -> float:
        """Calculate the F1-score, which is the harmonic mean of precision and recall.

        Returns:
            float: The F1-score, or 0.0 if the denominator is zero.
        """
        p = self.get_precision()
        r = self.get_recall()
        return 2 * (p * r) / (p + r) if p + r > 0 else 0.0

    def get_accuracy(self) -> float:
        """Calculate the accuracy metric.

        Returns:
            float: The accuracy value, or 0.0 if the total number of samples is zero.
        """
        tot_num = self.fn + self.fp + self.tp + self.tn
        num_accurate = self.tp + self.tn
        return 0.0 if tot_num == 0 else num_accurate / tot_num

    def assert_min(self, accuracy_min: float, precision_min: float, recall_min: float) -> None:
        """Assert that the accuracy, precision, and recall metrics meet the given minima.

        Args:
            accuracy_min: Minimum acceptable accuracy.
            precision_min: Minimum acceptable precision.
            recall_min: Minimum acceptable recall.

        Raises:
            AssertionError: If any of the metrics are below their respective thresholds.
        """
        assert self.get_accuracy() >= accuracy_min, f'{self.get_accuracy()} < {accuracy_min}'
        assert self.get_precision() >= precision_min, f'{self.get_precision()} < {precision_min}'
        assert self.get_recall() >= recall_min, f'{self.get_recall()} < {recall_min}'
