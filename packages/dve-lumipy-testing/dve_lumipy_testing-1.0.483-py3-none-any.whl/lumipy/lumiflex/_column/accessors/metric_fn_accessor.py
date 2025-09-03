from typing import Union, Optional

from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints, block_node_type
from lumipy.lumiflex.column import Column
from .base_fn_accessor import BaseFnAccessor


class MetricFnAccessor(BaseFnAccessor):

    @block_node_type(label='aggfunc', name='.stats')
    def __init__(self, column: Column):
        super().__init__('metric', column, Is.numeric)

    @input_constraints(..., Is.numeric, name='.metric.mean_squared_error()')
    def mean_squared_error(self, y: Column) -> Column:
        """Apply a mean squared error calculation between two value series.

        Args:
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'mean_squared_error({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.metric.mean_absolute_error()')
    def mean_absolute_error(self, y: Column) -> Column:
        """Apply a mean absolute error calculation between two value series.

        Args:
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'mean_absolute_error({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.metric.mean_fractional_absolute_error()')
    def mean_fractional_absolute_error(self, y: Column) -> Column:
        """Apply a mean fractional absolute error calculation between two value series.

        Args:
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'mean_fractional_absolute_error({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, Is.numeric, name='.metric.minkowski_distance()')
    def minkowski_distance(self, y: Column, p: Union[int, float]) -> Column:
        """Apply a Minkowski distance calculation between two value series.

        Notes:
            The Minkowski distance is a generalisation of the Euclidean (p=2) or Manhattan (p=1) distance to other powers p.
            See
                https://en.wikipedia.org/wiki/Minkowski_distance

        Args:
            y (Column): the other value series.
            p (Union[int, float]): the order p.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2, a3: f'minkowski_distance({a1.sql}, {a2.sql}, {a3.sql})'
        return Column(fn=fn, parents=(self._column, y, p), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.metric.chebyshev_distance()')
    def chebyshev_distance(self, y: Column) -> Column:
        """Apply a Chebyshev distance calculation between two value series.

        Notes:
            The Chebyshev distance is the greatest difference between dimension values of two vectors. It is equivalent to
            the Minkowski distance as p → ∞
            See
                https://en.wikipedia.org/wiki/Chebyshev_distance

        Args:
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'chebyshev_distance({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.metric.manhattan_distance()')
    def manhattan_distance(self, y: Column) -> Column:
        """Apply a Manhattan distance calculation between two value series.

        Notes:
            The Manhattan distance (aka the taxicab distance) is the absolute sum of differences between the elements of two
            vectors. It is analogous the distance traced out by a taxicab moving along a city grid like Manhattan where the
            diagonal distance is the sum of the sides of the squares.
            See
                https://en.wikipedia.org/wiki/Taxicab_geometry

        Args:
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'manhattan_distance({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.metric.euclidean_distance()')
    def euclidean_distance(self, y: Column) -> Column:
        """Apply a Euclidean distance calculation between two value series.

        Notes:
            The Euclidean distance is the familiar 'as the crow flies' distance. It is the square root of the sum of squared
            differences between the elements of two vectors.
            See
                https://en.wikipedia.org/wiki/Euclidean_distance

        Args:
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'euclidean_distance({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.metric.canberra_distance()')
    def canberra_distance(self, y: Column) -> Column:
        """Apply a Canberra distance calculation between two value series.

        Notes:
            The Canberra distance is the elementwise sum of absolute differences between elements divided by the sum of
            their absolute values. It can be considered a weighted version of the Manhattan distance.
            See
                https://en.wikipedia.org/wiki/Canberra_distance

        Args:
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'canberra_distance({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.metric.braycurtis_distance()')
    def braycurtis_distance(self, y: Column) -> Column:
        """Apply a Bray-Curtis distance calculation between two value series.

        Notes:
            The Bray-Curtis distance is the elementwise sum of absolute differences between elements divided by the absolute
            value of their sum. It behaves like a fractional version of the Manhattan distance.

        Args:
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'braycurtis_distance({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.metric.cosine_distance()')
    def cosine_distance(self, y: Column) -> Column:
        """Apply a cosine distance calculation between two value series.

        Notes:
            The cosine distance is the cosine of the angle between two vectors subtracted from 1.
            See
                https://en.wikipedia.org/wiki/Cosine_similarity

        Args:
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'cosine_distance({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.metric.precision_score()')
    def precision_score(self, y: Column) -> Column:
        """Apply a precision score calculation to two value series.

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
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'precision_score({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.metric.recall_score()')
    def recall_score(self, y: Column) -> Column:
        """Apply a recall score calculation to two value series.

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
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'recall_score({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, Is.numeric, name='.metric.f_score()')
    def f_score(self, y: Column, beta: Optional[float] = 1.0) -> Column:
        """Apply an F-score calculation between two value series.

        Notes:
            The F-score is classifier performance metric which measures accuracy. It is defined as the weighted harmonic
            mean of precision and recall scores. The beta parameter controls the relative weighting of these two metrics.

            The most common value of beta is 1: this is the F_1 score (aka balanced F-score). It weights precision and
            recall evenly. Values of beta greater than 1 weight recall higher than precision and less than 1 weights
            precision higher than recall.

            See
                https://en.wikipedia.org/wiki/F-score

        Args:
            y (Column): the other value series.
            beta (Optional[float]): the value of beta to use in the calculation (Defaults to 1.0).

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2, a3: f'fbeta_score({a1.sql}, {a2.sql}, {a3.sql})'
        return Column(fn=fn, parents=(self._column, y, beta), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, name='.metric.r_squared()')
    def r_squared(self, y: Column) -> Column:
        """Apply an r squared calculation between two value series.

        Args:
            y (Column): the other value series.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'r_squared({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @input_constraints(..., Is.numeric, Is.integer, name='.metric.adjusted_r_squared()')
    def adjusted_r_squared(self, y: Column, n: int) -> Column:
        """Apply an adjusted r squared calculation between two value series.

        Args:
            y (Column): the other value series.
            n (Integer): The number of predictors that the model has.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2, a3: f'adjusted_r_squared({a1.sql}, {a2.sql}, {a3.sql})'
        return Column(fn=fn, parents=(self._column, y, n), dtype=DType.Double, label='aggfunc')
