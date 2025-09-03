from typing import Union

from lumipy.lumiflex._metadata import DType
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex._window.window import WindowColumn
from lumipy.lumiflex.column import Column
from .base_win_fn_accessor import BaseWinFnAccessor


class MetricsWinFnAccessor(BaseWinFnAccessor):

    @input_constraints(..., Is.numeric, Is.numeric, name='mean_squared_error()')
    def mean_squared_error(self, x: Column, y: Column) -> WindowColumn:
        """Apply a mean squared error calculation between two series in this window.

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'mean_squared_error({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='mean_absolute_error()')
    def mean_absolute_error(self, x: Column, y: Column) -> WindowColumn:
        """Apply a mean absolute error calculation between two series in this window.

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'mean_absolute_error({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='mean_fractional_absolute_error()')
    def mean_fractional_absolute_error(self, x: Column, y: Column) -> WindowColumn:
        """Apply a mean fractional absolute error calculation between two series in this window.

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'mean_fractional_absolute_error({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, Is.numeric, name='minkowski_distance()')
    def minkowski_distance(self, x: Column, y: Column, p: Union[int, float]) -> WindowColumn:
        """Apply a minkowski distance calculation between two series in this window.

        Notes:
            The Minkowski distance is a generalisation of the Euclidean (p=2) or Manhattan (p=1) distance to other powers p.
            See
                https://en.wikipedia.org/wiki/Minkowski_distance

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.
            p (Union[int, float]): the exponent value to use.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2, a3: f'minkowski_distance({a1.sql}, {a2.sql}, {a3.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y, p), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='chebyshev_distance()')
    def chebyshev_distance(self, x: Column, y: Column) -> WindowColumn:
        """Apply a Chebyshev distance calculation between two series in this window.

        Notes:
            The Chebyshev distance is the greatest difference between dimension values of two vectors. It is equivalent to
            the Minkowski distance as p → ∞
            See
                https://en.wikipedia.org/wiki/Chebyshev_distance

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'chebyshev_distance({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='manhattan_distance()')
    def manhattan_distance(self, x: Column, y: Column) -> WindowColumn:
        """Apply a Manhattan distance calculation between two series in this window.

        Notes:
            The Manhattan distance (aka the taxicab distance) is the absolute sum of differences between the elements of two
            vectors. It is analogous the distance traced out by a taxicab moving along a city grid like Manhattan where the
            diagonal distance is the sum of the sides of the squares.
            See
                https://en.wikipedia.org/wiki/Taxicab_geometry

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'manhattan_distance({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='euclidean_distance()')
    def euclidean_distance(self, x: Column, y: Column) -> WindowColumn:
        """Apply a Euclidean distance calculation between two series in this window.

        Notes:
            The Euclidean distance is the familiar 'as the crow flies' distance. It is the square root of the sum of squared
            differences between the elements of two vectors.
            See
                https://en.wikipedia.org/wiki/Euclidean_distance

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'euclidean_distance({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='canberra_distance()')
    def canberra_distance(self, x: Column, y: Column) -> WindowColumn:
        """Apply a Canberra distance calculation between two series in this window.

        Notes:
            The Canberra distance is the elementwise sum of absolute differences between elements divided by the sum of
            their absolute values. It can be considered a weighted version of the Manhattan distance.
            See
                https://en.wikipedia.org/wiki/Canberra_distance

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'canberra_distance({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='braycurtis_distance()')
    def braycurtis_distance(self, x: Column, y: Column) -> WindowColumn:
        """Apply a Bray-Curtis distance calculation between two series in this window.

        Notes:
            The Bray-Curtis distance is the elementwise sum of absolute differences between elements divided by the absolute
            value of their sum. It behaves like a fractional version of the Manhattan distance.

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'braycurtis_distance({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='cosine_distance()')
    def cosine_distance(self, x: Column, y: Column) -> WindowColumn:
        """Apply a cosine distance calculation between two series in this window.

        Notes:
            The cosine distance is the cosine of the angle between two vectors subtracted from 1.
            See
                https://en.wikipedia.org/wiki/Cosine_similarity

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'cosine_distance({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='precision_score()')
    def precision_score(self, x: Column, y: Column) -> WindowColumn:
        """Apply a precision score calculation between two series in this window.

        Notes:
            Precision is a classification performance metric which measures the fraction of true positive events in a
            set of events that a classifier has predicted to be positive. It is calculated as follows

                precision = tp / (tp + fp)

            where tp is the number of true positives and fp is the number of false positives. Precision is a measure of the
            purity of the classifier's positive predictions.
            See
                https://en.wikipedia.org/wiki/Precision_and_recall

            Precision is also known as the positive predictive value and purity.

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'precision_score({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='recall_score()')
    def recall_score(self, x: Column, y: Column) -> WindowColumn:
        """Apply a recall score calculation between two series in this window.

        Notes:
            Recall is a classification performance metric which measures the fraction of positive events that are
            successfully predicted by a classifier. It is calculated as follows

                recall = tp / (tp + fn)

            where tp is the number of true positives and fn is the number of false negatives. Recall is a measure of the
            efficiency of the classifier at retrieving positive events.
            See
                https://en.wikipedia.org/wiki/Precision_and_recall

            Recall is also known as sensitivity, hit rate, true positive rate (TPR) and efficiency.

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'recall_score({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, Is.numeric, name='f_score()')
    def f_score(self, x: Column, y: Column, beta: float = 1.0) -> WindowColumn:
        """Apply an F-Beta score calculation between two series in this window.

        Notes:
            The F-score is classifier performance metric which measures accuracy. It is defined as the weighted harmonic
            mean of precision and recall scores. The beta parameter controls the relative weighting of these two metrics.

            The most common value of beta is 1: this is the F_1 score (aka balanced F-score). It weights precision and
            recall evenly. Values of beta greater than 1 weight recall higher than precision and less than 1 weights
            precision higher than recall.

            See
                https://en.wikipedia.org/wiki/F-score

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.
            beta (float): the beta value to use in the calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2, a3: f'fbeta_score({a1.sql}, {a2.sql}, {a3.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y, beta), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='r_squared()')
    def r_squared(self, x: Column, y: Column) -> WindowColumn:
        """Apply an r squared calculation between two series in this window.

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'r_squared({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, Is.integer, name='adjusted_r_squared()')
    def adjusted_r_squared(self, x: Column, y: Column, n: int) -> WindowColumn:
        """Apply an r squared calculation between two series in this window.

        Args:
            x (Column): the first series in the metric calculation.
            y (Column): the second series in the metric calculation.
            n (Integer): The number of predictors that the model has.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2, a3: f'adjusted_r_squared({a1.sql}, {a2.sql}, {a3.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y, n), dtype=DType.Double)
