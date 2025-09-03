import pandas as pd
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
import numpy as np
from string import ascii_letters
import datetime as dt
from lumipy.lumiflex._table import TableLiteralVar


class TestTableLiteral(SqlTestCase):

    def test_table_literal_def_construction(self):

        def random_val(type_ix):
            if type_ix == 0:
                return np.random.randint(-10, 10)
            if type_ix == 1:
                return np.random.uniform(-1, 1)
            if type_ix == 2:
                return bool(np.random.binomial(1, 0.5))
            if type_ix == 3:
                return ''.join(np.random.choice(list(ascii_letters), size=15))
            if type_ix == 4:
                return dt.date(2022, 1, 1) + dt.timedelta(days=np.random.randint(-10, 10))
            if type_ix == 5:
                return dt.datetime(2022, 1, 1, 15, 10, 25) + dt.timedelta(hours=np.random.uniform(-10, 10))

        np.random.seed(1989)
        df = pd.DataFrame([
            {f'Col{c}': random_val(i % 6) for i, c in enumerate('ABCDEF')}
            for _ in range(5)
        ])

        table_def = TableLiteralVar(df=df, client=self.make_dummy_client())

        table = table_def.build()
        sql = table.select('*').get_sql()
        self.assertSqlEqual(
            """
            @pandas_df_1 = SELECT
               [column1] AS [ColA], [column2] AS [ColB], [column3] AS [ColC], [column4] AS [ColD], [column5] AS [ColE], [column6] AS [ColF]
            FROM
               (VALUES
                  (0, -0.129950634350849, FALSE, 'hpAgRCWOpdxKCPH', #2022-01-05#, #2022-01-01 16:56:27.003171#),
                  (1, 0.859493478311558, FALSE, 'MrwGYzdRelTipSH', #2022-01-08#, #2022-01-01 11:47:10.715660#),
                  (-1, -0.976436246310444, TRUE, 'xJiRFMzpPBrgurG', #2021-12-28#, #2022-01-01 16:43:34.328873#),
                  (-7, 0.678061376945509, TRUE, 'twYEtMeZcctGzXY', #2021-12-26#, #2022-01-01 09:54:54.443169#),
                  (-2, -0.311448856979136, TRUE, 'cYTZaZnWxejRwnY', #2021-12-22#, #2022-01-01 19:40:59.588473#)
               );
            ------------------------------------------------------------------------------------------------

            SELECT
               [ColA], [ColB], [ColC], [ColD], [ColE], [ColF]
            FROM
               @pandas_df_1            
            """,
            sql
        )
