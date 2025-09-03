from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints, block_node_type
from lumipy.lumiflex.column import Column
from .base_fn_accessor import BaseFnAccessor


class LinregFnAccessor(BaseFnAccessor):

    @block_node_type(label='aggfunc', name='.linreg')
    def __init__(self, column: Column):
        super().__init__('linreg', column, Is.numeric)

    @block_node_type(label='aggfunc', name='.linreg.alpha()')
    @input_constraints(..., Is.numeric, name='.linreg.alpha()')
    def alpha(self, y: Column):
        """Apply a linear regression alpha (y intercept) calculation to these values.

        Notes:
            Alpha is the y intercept of the fitted line. See https://en.wikipedia.org/wiki/Simple_linear_regression#Fitting_the_regression_line
            for more details.

        Args:
            y (Column): the dependent variable.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'linear_regression_alpha({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.linreg.beta()')
    @input_constraints(..., Is.numeric, name='.linreg.beta()')
    def beta(self, y: Column):
        """Apply a linear regression beta (gradient) calculation to these values.

        Notes:
            Beta is the gradient of the fitted line. See https://en.wikipedia.org/wiki/Simple_linear_regression#Fitting_the_regression_line
            for more details.

        Args:
            y (Column): the dependent variable.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'linear_regression_beta({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.linreg.alpha_std_err()')
    @input_constraints(..., Is.numeric, name='.linreg.alpha_std_err()')
    def alpha_std_err(self, y: Column):
        """Apply a linear regression alpha standard error calculation to these values.

        Notes:
            The calculation for the standard error of alpha assumes the residuals are normally distributed and is
            calculated according to
            https://en.wikipedia.org/wiki/Simple_linear_regression#Normality_assumption

        Args:
            y (Column): the dependent variable.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'linear_regression_alpha_error({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')

    @block_node_type(label='aggfunc', name='.linreg.beta_std_err()')
    @input_constraints(..., Is.numeric, name='.linreg.beta_std_err()')
    def beta_std_err(self, y: Column):
        """Apply a linear regression beta standard error calculation to these values.

        Notes:
            The calculation for the standard error of beta assumes the residuals are normally distributed and is
            calculated according to
            https://en.wikipedia.org/wiki/Simple_linear_regression#Normality_assumption

        Args:
            y (Column): the dependent variable.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda a1, a2: f'linear_regression_beta_error({a1.sql}, {a2.sql})'
        return Column(fn=fn, parents=(self._column, y), dtype=DType.Double, label='aggfunc')
