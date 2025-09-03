from lumipy.lumiflex._column.make import make
from lumipy.lumiflex._column.case import When, Then, CaseColumn
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from pydantic import ValidationError


class TestWhen(SqlTestCase):

    def test_when_construction(self):
        table = self.make_table()
        cdn = table.col0 > 0
        when = When(parents=(cdn,))
        self.assertEqual('when', when.get_label())
        self.assertEqual(1, len(when.get_parents()))
        self.assertHashEqual(cdn, when.get_parents()[0])

    def test_when_construction_with_then(self):
        table = self.make_table()

        cdn1 = table.col0 > 0
        when1 = When(parents=(cdn1,))

        val1 = table.col0 / table.col1
        then = Then(parents=(val1, when1))

        cdn2 = table.col3 == 3
        when2 = When(parents=(cdn2, then))
        self.assertEqual(2, len(when2.get_parents()))
        self.assertHashEqual(cdn2, when2.get_parents()[0])
        self.assertHashEqual(then, when2.get_parents()[1])

    def test_when_construction_validation(self):
        table = self.make_table()

        self.assertErrorsWithMessage(
            lambda: When(),
            ValueError,
            """1 validation error for When
parents
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/missing""",
            [3]
        )
        self.assertErrorsWithMessage(
            lambda: When(parents=tuple()),
            ValueError,
            """1 validation error for When
parents
  Value error, When node must have one or two parents: (condition) or (condition, then), but received 0. [type=value_error, input_value=(), input_type=tuple]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error""",
            [3]
        )
        self.assertErrorsWithMessage(
            lambda: When(parents=(1, 2, 3)),
            ValueError,
            """1 validation error for When
parents
  Value error, When node must have one or two parents: (condition) or (condition, then), but received 3. [type=value_error, input_value=(1, 2, 3), input_type=tuple]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error""",
            [3]
        )
        self.assertErrorsWithMessage(
            lambda: When(parents=(table.col0,)),
            TypeError,
            "Condition must resolve to a boolean, but was Int."
        )
        self.assertErrorsWithMessage(
            lambda: When(parents=(table.col0 > 0, 3)),
            TypeError,
            "The second parent of When must be a Then object, but was int."
        )

    def test_when_hash_function(self):
        table = self.make_table()
        cdn = table.col0 > 0

        h1 = hash(When(parents=(cdn,)))
        h2 = hash(When(parents=(cdn,)))
        h3 = hash(When(parents=(table.col1 == 3,)))
        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h3)

    def test_when_then_method(self):
        table = self.make_table()
        cdn = table.col0 >= 0
        when = When(parents=(cdn,))
        then = when.then('positive')
        self.assertIsInstance(then, Then)
        self.assertEqual(2, len(then.get_parents()))
        self.assertHashEqual(make('positive'), then.get_parents()[0])
        self.assertHashEqual(when, then.get_parents()[1])

    def test_when_get_sql_method(self):
        table = self.make_table()
        cdn = table.col0 >= 0
        when = When(parents=(cdn,))
        sql = when.get_sql()
        self.assertEqual("WHEN [Col0] >= 0", sql)

    def test_when_with_prefixing(self):
        table = self.make_table()
        cdn = table.col0 >= 0
        when = When(parents=(cdn,))

        table_a = table.with_alias('AA')
        when_p = table_a._add_prefix(when)

        sql_p = when_p.get_sql()
        self.assertEqual("WHEN AA.[Col0] >= 0", sql_p)


class TestThen(SqlTestCase):

    def test_then_construction(self):
        table = self.make_table()
        cdn = table.col0 >= 0
        when = When(parents=(cdn,))
        value = table.col1 ** 2

        then = Then(parents=(value, when))
        self.assertEqual(2, len(then.get_parents()))
        self.assertHashEqual(value, then.get_parents()[0])
        self.assertHashEqual(when, then.get_parents()[1])

    def test_then_hash(self):
        table = self.make_table()
        when1 = When(parents=(table.col0 > 0,))
        when2 = When(parents=(table.col1 > 0,))
        val1 = make(4)
        val2 = make('a')

        h1 = hash(Then(parents=(val1, when1)))
        h2 = hash(Then(parents=(val1, when1)))
        h3 = hash(Then(parents=(val1, when2)))
        h4 = hash(Then(parents=(val2, when1)))
        h5 = hash(Then(parents=(val2, when2)))

        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h3)
        self.assertNotEqual(h3, h4)
        self.assertNotEqual(h4, h5)

    def test_then_constructor_validation(self):
        self.assertErrorsWithMessage(
            lambda: Then(),
            ValueError,
            """1 validation error for Then
parents
  Field required [type=missing, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/missing
            """,
            [3]
        )
        self.assertErrorsWithMessage(
            lambda: Then(parents=tuple()),
            ValueError,
            """1 validation error for Then
parents
  Value error, Then node must have two parents: (value, then) but received 0. [type=value_error, input_value=(), input_type=tuple]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [3]
        )
        self.assertErrorsWithMessage(
            lambda: Then(parents=(1, 2, 3)),
            ValueError,
            """1 validation error for Then
parents
  Value error, Then node must have two parents: (value, then) but received 3. [type=value_error, input_value=(1, 2, 3), input_type=tuple]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [3]
        )
        self.assertErrorsWithMessage(
            lambda: Then(parents=(1, 2)),
            TypeError,
            "Value must be a Column object, but was int.",
        )

    def test_then_when_method(self):
        table = self.make_table()
        cdn1 = table.col0 >= 0
        when1 = When(parents=(cdn1,))
        value = table.col1 ** 2

        then = Then(parents=(value, when1))
        cdn2 = table.col3 == 7
        when2 = then.when(cdn2)
        self.assertIsInstance(when2, When)
        self.assertHashEqual(cdn2, when2.get_parents()[0].get_parents()[0])  # b/c auto bracket node: need to unwrap
        self.assertHashEqual(then, when2.get_parents()[1])

    def test_then_when_validation(self):
        table = self.make_table()
        cdn1 = table.col0 >= 0
        when1 = When(parents=(cdn1,))
        value = table.col1 ** 2

        then = Then(parents=(value, when1))
        cdn2 = table.col3
        self.assertErrorsWithMessage(
            lambda: then.when(cdn2),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: then.when(cdn2),\n"
            "There was 1 failed constraint on .when():\n"
            "   • The input to 'condition' must be Boolean but was Decimal=[Col3]"
        )

    def test_then_otherwise_method(self):
        table = self.make_table()

        case = When(parents=(table.col0 > 1,)).then(
            'col0_gt1'
        ).when(
            table.col0 < -1
        ).then(
            'col0_l1-1'
        ).otherwise(
            'middle'
        )

        self.assertIsInstance(case, CaseColumn)
        self.assertEqual(DType.Text, case.dtype)
        self.assertSqlEqual(
            """
            CASE
                WHEN [Col0] > 1
                THEN 'col0_gt1'
                WHEN ([Col0] < -1)
                THEN 'col0_l1-1'
                ELSE 'middle'
            END            
            """,
            case.sql
        )

    def test_then_otherwise_method_default(self):
        table = self.make_table()

        case = When(parents=(table.col0 > 1,)).then(
            999
        ).when(
            table.col0 < -1
        ).then(
            -999
        ).otherwise()

        self.assertIsInstance(case, CaseColumn)
        self.assertEqual(DType.Int, case.dtype)
        self.assertSqlEqual(
            """
            CASE
                WHEN [Col0] > 1
                THEN 999
                WHEN ([Col0] < -1)
                THEN -999
                ELSE NULL
            END            
            """,
            case.sql
        )

    def test_then_get_sql_method(self):
        table = self.make_table()
        cdn1 = table.col0 >= 0
        when1 = When(parents=(cdn1,))
        value = table.col1 ** 2

        then = Then(parents=(value, when1))

        self.assertSqlEqual("THEN power([Col1], 2)", then.get_sql())

    def test_then_get_sql_with_prefix(self):
        table = self.make_table()
        cdn1 = table.col0 >= 0
        when1 = When(parents=(cdn1,))
        value = table.col1 ** 2

        then = Then(parents=(value, when1))

        table_a = table.with_alias('AA')
        then_p = table_a._add_prefix(then)
        self.assertSqlEqual("THEN power(AA.[Col1], 2)", then_p.get_sql())


class TestCaseColumn(SqlTestCase):

    def test_case_column_construction(self):
        table = self.make_table()

        then = When(parents=(table.col0 > 1,)).then(
            999
        ).when(
            table.col0 < -1
        ).then(
            -999
        )
        default = make(0)

        case = CaseColumn(parents=(default, then))
        self.assertHashEqual(default, case.get_parents()[0])
        self.assertHashEqual(then, case.get_parents()[1])

    def test_case_column_construction_validation(self):

        self.assertErrorsWithMessage(
            lambda: CaseColumn(),
            ValueError,
            """1 validation error for CaseColumn
  Value error, Case must have two parents, but was given 0 [type=value_error, input_value={}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [2]
        )
        self.assertErrorsWithMessage(
            lambda: CaseColumn(parents=(tuple())),
            ValueError,
            """1 validation error for CaseColumn
  Value error, Case must have two parents, but was given 0 [type=value_error, input_value={'parents': ()}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [2]
        )
        self.assertErrorsWithMessage(
            lambda: CaseColumn(parents=(1, )),
            ValueError,
            """1 validation error for CaseColumn
  Value error, Case must have two parents, but was given 1 [type=value_error, input_value={'parents': (1,)}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [2]
        )

        table = self.make_table()
        then = When(parents=(table.col0 > 1,)).then(
            999
        ).when(
            table.col0 > -1
        ).then(
            -999
        )

        self.assertErrorsWithMessage(
            lambda: CaseColumn(parents=(3, then)),
            ValueError,
            """1 validation error for CaseColumn
  Value error, First parent must be a Column, but was int. [type=value_error, input_value={'parents': (3, Then(
   ...      )
      )
   )
))}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [6]
        )

        default = make(0)
        self.assertErrorsWithMessage(
            lambda: CaseColumn(parents=(default, "bad")),
            ValueError,
            """1 validation error for CaseColumn
  Value error, Second parent must be Then, but was str. [type=value_error, input_value={'parents': (Column(
   l...0
   sql: '0'
), 'bad')}, input_type=dict]
    For further information visit https://errors.pydantic.dev/xxx/v/value_error
            """,
            [5]
        )

    def test_case_column_with_table_prefix(self):

        table = self.make_table()
        table_a = table.with_alias('AA')

        then = When(parents=(table.col0 > 1,)).then(
            123
        ).when(
            ((table.col0 + table.col1) * 0.5) > 3
        ).then(
            1.23
        ).when(
            ((table.col1 - table.col2) / table.col2) < 0
        ).then(
            99
        ).otherwise(
            10
        )

        then_a = table_a._add_prefix(then)
        sql = then_a.sql

        self.assertSqlEqual(
            """
            CASE
                WHEN AA.[Col0] > 1
                THEN 123
                WHEN (((AA.[Col0] + AA.[Col1]) * 0.5) > 3)
                THEN 1.23
                WHEN (((AA.[Col1] - AA.[Col2]) / AA.[Col2]) < 0)
                THEN 99
                ELSE 10
            END            
            """,
            sql
        )

