from lumipy.lumiflex._metadata import DType
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex._window.window import WindowColumn
from lumipy.lumiflex.column import Column
from .base_win_fn_accessor import BaseWinFnAccessor


class LinregWinFnAccessor(BaseWinFnAccessor):

    @input_constraints(..., Is.numeric, Is.numeric, name='alpha()')
    def alpha(self, x: Column, y: Column) -> WindowColumn:
        """Apply a linear regression alpha (y intercept) calculation to two series in this window.

        Notes:
            Alpha is the y intercept of the fitted line. See https://en.wikipedia.org/wiki/Simple_linear_regression#Fitting_the_regression_line
            for more details.

        Args:
            x (Column): the independent variable.
            y (Column): the dependent variable.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'linear_regression_alpha({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='beta()')
    def beta(self, x: Column, y: Column) -> WindowColumn:
        """Apply a linear regression beta (gradient) calculation to two series in this window.

        Notes:
            Beta is the gradient of the fitted line. See https://en.wikipedia.org/wiki/Simple_linear_regression#Fitting_the_regression_line
            for more details.

        Args:
            x (Column): the independent variable.
            y (Column): the dependent variable.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'linear_regression_beta({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='alpha_std_err()')
    def alpha_std_err(self, x: Column, y: Column) -> WindowColumn:
        """Apply a linear regression alpha (y intercept) standard error calculation to two series in this window.

        Notes:
            The calculation for the standard error of alpha assumes the residuals are normally distributed and is
            calculated according to
            https://en.wikipedia.org/wiki/Simple_linear_regression#Normality_assumption

        Args:
            x (Column): the independent variable.
            y (Column): the dependent variable.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'linear_regression_alpha_error({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)

    @input_constraints(..., Is.numeric, Is.numeric, name='beta_std_err()')
    def beta_std_err(self, x: Column, y: Column) -> WindowColumn:
        """Apply a linear regression beta (gradient) standard error calculation to two series in this window.

        Notes:
            The calculation for the standard error of beta assumes the residuals are normally distributed and is
            calculated according to
            https://en.wikipedia.org/wiki/Simple_linear_regression#Normality_assumption

        Args:
            x (Column): the independent variable.
            y (Column): the dependent variable.

        Returns:
            WindowColumn: window column instance representing this value.

        """
        fn = lambda a1, a2: f'linear_regression_beta_error({a1.sql}, {a2.sql})'
        return WindowColumn(fn=fn, parents=(self._window, x, y), dtype=DType.Double)
