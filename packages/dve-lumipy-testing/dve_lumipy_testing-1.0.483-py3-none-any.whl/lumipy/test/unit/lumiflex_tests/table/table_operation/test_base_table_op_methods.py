from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._table.content import CoreContent
from lumipy.lumiflex.table import Table


# noinspection SqlNoDataSourceInspection,SqlResolve
class TestBaseTableOpMethods(SqlTestCase):

    def test_table_op_content_property(self):
        table = self.make_table()

        q = table.select('*').where(table.col0 > 4)

        self.assertIsInstance(q.content, CoreContent)
        self.assertHashEqual(q.get_parents()[-1], q.content)

    def test_table_op_to_table_var(self):
        table = self.make_table()
        tv = table.select('^').to_table_var('x')

        self.assertIsInstance(tv, Table)

        sql = tv.select('*').get_sql()
        self.assertSqlEqual(
            """
            @x = SELECT
               [Col0], [Col2], [Col4], [Col6], [Col8]
            FROM
               [My.Test.Table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            --===========================================================================================--

            SELECT
               [Col0], [Col2], [Col4], [Col6], [Col8]
            FROM
               @x            
            """,
            sql
        )

    def test_table_op_to_scalar_var(self):

        table = self.make_table()
        total = table.select(Total=table.col0.sum()).to_scalar_var()
        q = table.select(table.col0, Frac=table.col0/total)

        self.assertSqlEqual(
            """
            @@sv_1 = SELECT
               total([Col0]) AS [Total]
            FROM
               [My.Test.Table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            --===========================================================================================--

            SELECT
               [Col0], ([Col0] / cast(@@sv_1 AS Double)) AS [Frac]
            FROM
               [My.Test.Table]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14
            """,
            q.get_sql()
        )

    def test_table_op_repr_markdown(self):

        table = self.make_table()
        q = table.select('^').where(table.col0 > 4)

        markdown = q._repr_markdown_()

        self.assertLineByLineEqual(
            """
            #### Luminesce SQL

            ```SQLite

                SELECT
                   [Col0], [Col2], [Col4], [Col6], [Col8]
                FROM
                   [My.Test.Table]
                WHERE
                   ([Param0] = 123
                   and [Param1] = 1727364939238612
                   and [Param2] = 3.14)
                   and (([Col0] > 4))
            ```

            ---

            #### Column Content

            >| | Name | Data Type |
            | --- | :- | :- |
            | 0 | Col0 | Int |
            | 1 | Col2 | Double |
            | 2 | Col4 | Boolean |
            | 3 | Col6 | Date |
            | 4 | Col8 | Int |

            ---

            ℹ️ Call `.go()` to send this query to Luminesce.

            ---
            """,
            markdown
        )
        pass

    def test_table_op_to_drive(self):
        table = self.make_table(n_params=0)
        q = table.select('^').where(table.col0 > 4).to_drive('/testing/path/to/query.csv')

        sql = q.get_sql()

        self.assertSqlEqual(
            """
            @drive_input_1 = SELECT
               [Col0], [Col2], [Col4], [Col6], [Col8]
            FROM
               [My.Test.Table]
            WHERE
               ([Col0] > 4);
            -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - --
            @drive_write_1 = use Drive.SaveAs with @drive_input_1
                      --type=csv
                      --path=/testing/path/to
                      --fileNames=query
                    enduse;
            --===========================================================================================--

            SELECT
               [VariableName], [FileName], [RowCount], [Skipped]
            FROM
               @drive_write_1            
            """,
            sql
        )

    def test_table_op_setup_view(self):
        table = self.make_table(n_params=0)
        q = table.select('^').where(table.col0 > 4).setup_view('testing.table.view')

        sql = q.get_sql()

        self.assertSqlEqual(
            """
            @make_view_1 = use Sys.Admin.SetupView
                --provider=testing.table.view
                -----------
                    SELECT
                       [Col0], [Col2], [Col4], [Col6], [Col8]
                    FROM
                       [My.Test.Table]
                    WHERE
                       ([Col0] > 4)
            enduse;
            --===========================================================================================--

            SELECT
               [Col0], [Col2], [Col4], [Col6], [Col8]
            FROM
               @make_view_1
            """,
            sql
        )

    def test_table_op_sample(self):
        table = self.make_table()

        q1 = table.select('^').where(table.col0 > 4).sample(prob=0.5)
        sql1 = q1.get_sql()

        self.assertSqlEqual(
            """
            @sample_tv_1 = SELECT
               [Col0], [Col2], [Col4], [Col6], [Col8]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 4));
            -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - --
            @sample_tv_2 = SELECT
               [Col0], [Col2], [Col4], [Col6], [Col8]
            FROM
               @sample_tv_1
            WHERE
               ((0.5  + random()/CAST(-18446744073709551616 AS REAL)) <= 0.5)
            ORDER BY
               (0.5  + random()/CAST(-18446744073709551616 AS REAL)) ASC;
            --===========================================================================================--

            SELECT
               [Col0], [Col2], [Col4], [Col6], [Col8]
            FROM
               @sample_tv_2            
            """,
            sql1
        )

        q2 = table.select('^').where(table.col0 > 4).sample(n=100)
        sql2 = q2.get_sql()

        self.assertSqlEqual(
            """
            @sample_tv_1 = SELECT
               [Col0], [Col2], [Col4], [Col6], [Col8]
            FROM
               [My.Test.Table]
            WHERE
               ([Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14)
               and (([Col0] > 4));
            -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - --
            @sample_tv_3 = SELECT
               [Col0], [Col2], [Col4], [Col6], [Col8]
            FROM
               @sample_tv_1
            ORDER BY
               (0.5  + random()/CAST(-18446744073709551616 AS REAL)) ASC
            LIMIT 100;
            --===========================================================================================--

            SELECT
               [Col0], [Col2], [Col4], [Col6], [Col8]
            FROM
               @sample_tv_3 
            """,
            sql2
        )
