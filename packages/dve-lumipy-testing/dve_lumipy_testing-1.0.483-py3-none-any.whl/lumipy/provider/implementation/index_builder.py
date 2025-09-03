import numpy as np
from cvxopt import matrix, solvers
from pandas import DataFrame, to_datetime

from lumipy.lumiflex import DType
from lumipy.provider.base_provider import BaseProvider
from lumipy.provider.context import Context
from lumipy.provider.metadata import ColumnMeta, ParamMeta, TableParam


class QuadraticProgram(BaseProvider):
    """This provider calculates weights for a collection of securities given a table of returns data. It does this by
    solving the following quadratic program

        min_w  w^T \Sigma w - \lambda \mu w

    where \Sigma is the covariance matrix of the returns series, \mu is the mean returns vector, w is the weights
    vector.

    """

    def __init__(self):

        columns = [
            ColumnMeta('Id', DType.Text, "Id that labels the security (i.e. a stock ticker)"),
            ColumnMeta('Weight', DType.Double, "Weight assigned by the quadratic optimisation."),
        ]
        parameters = [
            ParamMeta(
                'Lam',
                DType.Double,
                "Scaling parameter on the quadratic part of the objective. Sets the tradeoff between risk and returns "
                "(defaults to 1.0)",
                default_value=1.0,
            )
        ]
        table_parameters = [
            TableParam(
                'PriceData',
                columns=[
                    ColumnMeta('Id', DType.Text),
                    ColumnMeta('Date', DType.Date),
                    ColumnMeta('Price', DType.Double),
                ],
                description='A table of returns data to use in the quadratic program.'
            )
        ]

        super().__init__(
            name='Tools.Index.Quadratic.Program',
            columns=columns,
            parameters=parameters,
            table_parameters=table_parameters,
            description=self.__doc__
        )

    def get_data(self, context: Context) -> DataFrame:

        df = context.get('PriceData')
        lam = context.get('Lam')

        if df.shape[0] == 0:
            raise ValueError('Input table variable was empty.')

        df['Date'] = to_datetime(df.Date)
        df = df.sort_values(['Date']).set_index(['Date', 'Id'])

        rdf = np.log(df.unstack()).diff(axis=0).iloc[1:]

        cov_mat = rdf.cov().values
        avg_ret = rdf.mean(axis=0).values

        # Opt
        n = len(avg_ret)

        Q = matrix(cov_mat)
        p = matrix(-avg_ret) * lam

        G = matrix(np.vstack([np.diag([1.0] * n), np.diag([-1.0] * n)]))
        h = matrix([1.0] * n + [0.0] * n)

        A = matrix([1.0] * n, (1, n))
        b = matrix(1.0)

        sol = solvers.qp(Q, p, G, h, A, b)

        out_df = DataFrame({
            'Id': [c[1] for c in rdf.columns],
            'Weight': np.array(sol['x']).flatten()
        }).sort_values(
            'Weight', ascending=False
        ).reset_index(drop=True)

        return context.pandas.apply(out_df, False)
