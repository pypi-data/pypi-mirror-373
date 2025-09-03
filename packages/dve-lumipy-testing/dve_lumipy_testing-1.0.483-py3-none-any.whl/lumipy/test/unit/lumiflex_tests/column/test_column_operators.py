from lumipy.lumiflex._metadata.dtype import DType
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from datetime import date


class TestSqlColumnOperators(SqlTestCase):

    def test_column_add_op_numeric(self):
        d1 = self.make_double_col('d1')
        d2 = self.make_double_col('d2')

        # col col
        r = d1 + d2
        self.assertEqual('[d1] + [d2]', r.sql)
        self.assertEqual(DType.Double, r.dtype)

        # col, py
        r = d1 + 2.3
        self.assertEqual('[d1] + 2.3', r.sql)
        self.assertEqual(DType.Double, r.dtype)

        # py, col
        r = 1.2 + d2
        self.assertEqual('1.2 + [d2]', r.sql)
        self.assertEqual(DType.Double, r.dtype)

        # types
        # int, double
        r = 1 + d2
        self.assertEqual('1 + [d2]', r.sql)
        self.assertEqual(DType.Double, r.dtype)

        # int, int
        r = 2 + self.make_int_col('i1')
        self.assertEqual('2 + [i1]', r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_column_add_op_string(self):

        s1 = self.make_text_col('s1')

        r1 = s1 + 'ABC'
        self.assertEqual("[s1] || 'ABC'", r1.sql)
        self.assertEqual(DType.Text, r1.dtype)

        r2 = 'ABC' + s1
        self.assertEqual("'ABC' || [s1]", r2.sql)
        self.assertEqual(DType.Text, r2.dtype)

        s2 = self.make_text_col('s2')
        r3 = s1 + s2
        self.assertEqual("[s1] || [s2]", r3.sql)
        self.assertEqual(DType.Text, r3.dtype)

        s1 += 'X'
        s1 += 'Y'
        self.assertEqual("([s1] || 'X') || 'Y'", s1.sql)
        self.assertEqual(DType.Text, s1.dtype)

    def test_column_add_op_validation(self):
        d = self.make_double_col('d')
        b = self.make_datetime_col('dt')
        self.assertErrorsWithMessage(
            lambda: d + b,
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: d + b,\n"
            "There was 1 failed constraint on + (addition):\n"
            "   • The input to 'other' must not be Date/DateTime but was DateTime=[dt]"
        )

    def test_column_mul_op(self):
        d0, d1 = self.make_double_cols(2)
        i1 = self.make_int_col('i1')

        # col col
        r = (d0 * d1)
        self.assertEqual("[d0] * [d1]", r.sql)
        self.assertEqual(DType.Double, r.dtype)
        r = (i1 * d0)
        self.assertEqual("[i1] * [d0]", r.sql)
        self.assertEqual(DType.Double, r.dtype)

        # lit col
        r = 1 * d0
        self.assertEqual("1 * [d0]", r.sql)
        self.assertEqual(DType.Double, r.dtype)
        r = 1 * i1
        self.assertEqual("1 * [i1]", r.sql)
        self.assertEqual(DType.Int, r.dtype)

        # col lit
        r = d0 * 1
        self.assertEqual("[d0] * 1", r.sql)
        self.assertEqual(DType.Double, r.dtype)
        r = i1 * 1
        self.assertEqual("[i1] * 1", r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_column_mul_op_validation(self):
        self.assertErrorsWithMessage(
            lambda: self.make_date_col('dt') * 'ABC',
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: self.make_date_col('dt') * 'ABC',\n"
            "There were 2 failed constraints on * (multiplication):\n"
            "   • The input to 'self' must be Int/BigInt/Double/Decimal but was Date=[dt]\n"
            "   • The input to 'other' must be Int/BigInt/Double/Decimal but was Text='ABC'"
        )

    def test_column_divide_ops(self):
        d = self.make_double_col('d')
        i = self.make_int_col('i')

        r1 = d / i
        self.assertEqual('[d] / cast([i] AS Double)', r1.sql)
        self.assertEqual(DType.Double, r1.dtype)

        r2 = d // i
        self.assertEqual('[d] / [i]', r2.sql)
        self.assertEqual(DType.Int, r2.dtype)

        r3 = d // 2
        self.assertEqual('[d] / 2', r3.sql)
        self.assertEqual(DType.Int, r3.dtype)

        r4 = d / 2.0
        self.assertEqual('[d] / 2.0', r4.sql)
        self.assertEqual(DType.Double, r4.dtype)

    def test_column_divide_op_validation(self):
        self.assertErrorsWithMessage(
            lambda: self.make_date_col('dt') / 'ABC',
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: self.make_date_col('dt') / 'ABC',\n"
            "There were 2 failed constraints on / (division):\n"
            "   • The input to 'self' must be Int/BigInt/Double/Decimal but was Date=[dt]\n"
            "   • The input to 'other' must be Int/BigInt/Double/Decimal but was Text='ABC'"
        )

    def test_column_op_bracketing(self):
        d1 = self.make_double_col('d1')
        d2 = self.make_double_col('d2')

        d3 = (d1 + d2) / 2
        self.assertEqual('([d1] + [d2]) / cast(2 AS Double)', d3.sql)

    def test_column_op_subtract_numeric(self):
        d1 = self.make_double_col('d1')
        d2 = self.make_double_col('d2')
        i1 = self.make_int_col('i1')
        i2 = self.make_int_col('i2')

        r = d1 - d2
        self.assertEqual('[d1] - [d2]', r.sql)
        self.assertEqual(DType.Double, r.dtype)

        r = 1 - d1
        self.assertEqual('1 - [d1]', r.sql)
        self.assertEqual(DType.Double, r.dtype)

        r = d1 - 1
        self.assertEqual('[d1] - 1', r.sql)
        self.assertEqual(DType.Double, r.dtype)

        r = i1 - i2
        self.assertEqual('[i1] - [i2]', r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_column_op_sub_timelike(self):
        date1 = self.make_date_col('date1')
        date2 = self.make_date_col('date2')
        datetime1 = self.make_datetime_col('datetime1')
        datetime2 = self.make_datetime_col('datetime2')

        r = date1 - date2
        self.assertEqual("((julianday([date1]) - julianday([date2])) * 3600) * 24", r.sql)
        self.assertEqual(DType.Double, r.dtype)

        r = datetime1 - date2
        self.assertEqual("((julianday([datetime1]) - julianday([date2])) * 3600) * 24", r.sql)
        self.assertEqual(DType.Double, r.dtype)

        r = date1 - datetime2
        self.assertEqual("((julianday([date1]) - julianday([datetime2])) * 3600) * 24", r.sql)
        self.assertEqual(DType.Double, r.dtype)

        r = datetime1 - datetime2
        self.assertEqual("((julianday([datetime1]) - julianday([datetime2])) * 3600) * 24", r.sql)
        self.assertEqual(DType.Double, r.dtype)

    def test_column_op_sub_validation(self):
        self.assertErrorsWithMessage(
            lambda: self.make_text_col('s1') - self.make_text_col('s2'),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: self.make_text_col('s1') - self.make_text_col('s2'),\n"
            "There were 2 failed constraints on - (subtraction):\n"
            "   • The input to 'self' must not be Text but was Text=[s1]\n"
            "   • The input to 'other' must not be Text but was Text=[s2]"
        )
        self.assertErrorsWithMessage(
            lambda: self.make_date_col('dt1') - self.make_double_col('s2'),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: self.make_date_col('dt1') - self.make_double_col('s2'),\n"
            "There was 1 failed constraint on - (subtraction):\n"
            "   • The input to 'self' must be Int/BigInt/Double/Decimal but was Date=[dt1]"
        )

    def test_column_op_equal(self):
        d1, d2 = self.make_double_col('d1'), self.make_double_col('d2')
        i1, i2 = self.make_int_col('i1'), self.make_int_col('i2')
        b1, b2 = self.make_boolean_col('b1'), self.make_boolean_col('b2')
        s1, s2 = self.make_text_col('s1'), self.make_text_col('s2')
        dt1, dt2 = self.make_date_col('dt1'), self.make_date_col('dt2')

        # col col
        self.assertEqual("[d1] = [d2]", (d1 == d2).sql)
        self.assertEqual("[i1] = [i2]", (i1 == i2).sql)
        self.assertEqual("[b1] = [b2]", (b1 == b2).sql)
        self.assertEqual("[s1] = [s2]", (s1 == s2).sql)
        self.assertEqual("[dt1] = [dt2]", (dt1 == dt2).sql)

        # lit col
        self.assertEqual("[d2] = 1.2", (1.2 == d2).sql)
        self.assertEqual("[i2] = 3", (3 == i2).sql)
        self.assertEqual("[b2] = TRUE", (True == b2).sql)
        self.assertEqual("[s2] = 'ABC'", ('ABC' == s2).sql)
        self.assertEqual("[dt2] = #2023-01-01#", (date(2023, 1, 1) == dt2).sql)

        # col lit
        self.assertEqual("[d2] = 1.2", (d2 == 1.2).sql)
        self.assertEqual("[i2] = 3", (i2 == 3).sql)
        self.assertEqual("[b2] = TRUE", (b2 == True).sql)
        self.assertEqual("[s2] = 'ABC'", (s2 == 'ABC').sql)
        self.assertEqual("[dt2] = #2023-01-01#", (dt2 == date(2023, 1, 1)).sql)

    def test_column_op_equal_validation(self):
        d = self.make_double_col('d')
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: d == s,
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: d == s,\n"
            "There was 1 failed constraint on = (equal):\n"
            "   • The inputs to (self, other) must all be mutually-comparable types but were (Double [d], Text [s])"
        )

    def test_column_op_not_equal(self):
        d1, d2 = self.make_double_col('d1'), self.make_double_col('d2')
        i1, i2 = self.make_int_col('i1'), self.make_int_col('i2')
        b1, b2 = self.make_boolean_col('b1'), self.make_boolean_col('b2')
        s1, s2 = self.make_text_col('s1'), self.make_text_col('s2')
        dt1, dt2 = self.make_date_col('dt1'), self.make_date_col('dt2')

        # col col
        self.assertEqual("[d1] != [d2]", (d1 != d2).sql)
        self.assertEqual("[i1] != [i2]", (i1 != i2).sql)
        self.assertEqual("[b1] != [b2]", (b1 != b2).sql)
        self.assertEqual("[s1] != [s2]", (s1 != s2).sql)
        self.assertEqual("[dt1] != [dt2]", (dt1 != dt2).sql)

        # lit col
        self.assertEqual("[d2] != 1.2", (1.2 != d2).sql)
        self.assertEqual("[i2] != 3", (3 != i2).sql)
        self.assertEqual("[b2] != TRUE", (True != b2).sql)
        self.assertEqual("[s2] != 'ABC'", ('ABC' != s2).sql)
        self.assertEqual("[dt2] != #2023-01-01#", (date(2023, 1, 1) != dt2).sql)

        # col lit
        self.assertEqual("[d2] != 1.2", (d2 != 1.2).sql)
        self.assertEqual("[i2] != 3", (i2 != 3).sql)
        self.assertEqual("[b2] != TRUE", (b2 != True).sql)
        self.assertEqual("[s2] != 'ABC'", (s2 != 'ABC').sql)
        self.assertEqual("[dt2] != #2023-01-01#", (dt2 != date(2023, 1, 1)).sql)

    def test_column_op_not_equal_validation(self):
        d = self.make_double_col('d')
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: d != s,
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: d != s,\n"
            "There was 1 failed constraint on != (not equal):\n"
            "   • The inputs to (self, other) must all be mutually-comparable types but were (Double [d], Text [s])"
        )

    def test_column_op_negative(self):
        d1 = self.make_double_col('d1')
        r = -d1
        self.assertEqual("-[d1]", r.sql)

    def test_column_op_negative_validation(self):
        self.assertErrorsWithMessage(
            lambda: -self.make_text_col('s'),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: -self.make_text_col('s'),\n"
            "There was 1 failed constraint on - (negative):\n"
            "   • The input to 'self' must be Int/BigInt/Double/Decimal but was Text=[s]"
        )

    def test_column_op_invert(self):
        b = self.make_boolean_col('b')
        r = ~b
        self.assertEqual("NOT [b]", r.sql)

    def test_column_op_invert_validation(self):
        self.assertErrorsWithMessage(
            lambda: ~self.make_text_col('s'),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: ~self.make_text_col('s'),\n"
            "There was 1 failed constraint on ~ (not):\n"
            "   • The input to 'self' must be Boolean but was Text=[s]"
        )

    def test_column_op_less_than(self):
        d1 = self.make_double_col('d1')
        d2 = self.make_double_col('d2')
        r = d1 < d2
        self.assertEqual('[d1] < [d2]', r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_column_op_less_than_validation(self):
        d = self.make_double_col('d')
        t = self.make_text_col('t')
        self.assertErrorsWithMessage(
            lambda: d > t,
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: d > t,\n"
            "There was 1 failed constraint on > (greater than):\n"
            "   • The inputs to (self, other) must all be mutually-comparable types but were (Double [d], Text [t])"
        )

    def test_column_op_less_than_or_equal(self):
        d1, d2 = self.make_double_col('d1'), self.make_double_col('d2')
        i1, i2 = self.make_int_col('i1'), self.make_int_col('i2')
        b1, b2 = self.make_boolean_col('b1'), self.make_boolean_col('b2')
        s1, s2 = self.make_text_col('s1'), self.make_text_col('s2')
        dt1, dt2 = self.make_date_col('dt1'), self.make_date_col('dt2')

        # col col
        self.assertEqual("[d1] <= [d2]", (d1 <= d2).sql)
        self.assertEqual("[i1] <= [i2]", (i1 <= i2).sql)
        self.assertEqual("[b1] <= [b2]", (b1 <= b2).sql)
        self.assertEqual("[s1] <= [s2]", (s1 <= s2).sql)
        self.assertEqual("[dt1] <= [dt2]", (dt1 <= dt2).sql)

        # lit col
        self.assertEqual("[d2] >= 1.2", (1.2 <= d2).sql)
        self.assertEqual("[i2] >= 3", (3 <= i2).sql)
        self.assertEqual("[b2] >= TRUE", (True <= b2).sql)
        self.assertEqual("[s2] >= 'ABC'", ('ABC' <= s2).sql)
        self.assertEqual("[dt2] >= #2023-01-01#", (date(2023, 1, 1) <= dt2).sql)

        # col lit
        self.assertEqual("[d2] <= 1.2", (d2 <= 1.2).sql)
        self.assertEqual("[i2] <= 3", (i2 <= 3).sql)
        self.assertEqual("[b2] <= TRUE", (b2 <= True).sql)
        self.assertEqual("[s2] <= 'ABC'", (s2 <= 'ABC').sql)
        self.assertEqual("[dt2] <= #2023-01-01#", (dt2 <= date(2023, 1, 1)).sql)

    def test_column_op_less_than_or_equal_validation(self):
        self.assertErrorsWithMessage(
            lambda: self.make_text_col('s') <= 3,
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: self.make_text_col('s') <= 3,\n"
            "There was 1 failed constraint on <= (less than or equal):\n"
            "   • The inputs to (self, other) must all be mutually-comparable types but were (Text [s], Int 3)"
        )

    def test_column_op_greater_than(self):
        d1, d2 = self.make_double_col('d1'), self.make_double_col('d2')
        i1, i2 = self.make_int_col('i1'), self.make_int_col('i2')
        b1, b2 = self.make_boolean_col('b1'), self.make_boolean_col('b2')
        s1, s2 = self.make_text_col('s1'), self.make_text_col('s2')
        dt1, dt2 = self.make_date_col('dt1'), self.make_date_col('dt2')

        # col col
        self.assertEqual("[d1] > [d2]", (d1 > d2).sql)
        self.assertEqual("[i1] > [i2]", (i1 > i2).sql)
        self.assertEqual("[b1] > [b2]", (b1 > b2).sql)
        self.assertEqual("[s1] > [s2]", (s1 > s2).sql)
        self.assertEqual("[dt1] > [dt2]", (dt1 > dt2).sql)

        # lit col
        self.assertEqual("[d2] < 1.2", (1.2 > d2).sql)
        self.assertEqual("[i2] < 3", (3 > i2).sql)
        self.assertEqual("[b2] < TRUE", (True > b2).sql)
        self.assertEqual("[s2] < 'ABC'", ('ABC' > s2).sql)
        self.assertEqual("[dt2] < #2023-01-01#", (date(2023, 1, 1) > dt2).sql)

        # col lit
        self.assertEqual("[d2] > 1.2", (d2 > 1.2).sql)
        self.assertEqual("[i2] > 3", (i2 > 3).sql)
        self.assertEqual("[b2] > TRUE", (b2 > True).sql)
        self.assertEqual("[s2] > 'ABC'", (s2 > 'ABC').sql)
        self.assertEqual("[dt2] > #2023-01-01#", (dt2 > date(2023, 1, 1)).sql)

    def test_column_op_greater_than_validation(self):
        self.assertErrorsWithMessage(
            lambda: self.make_text_col('s') > 3,
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: self.make_text_col('s') > 3,\n"
            "There was 1 failed constraint on > (greater than):\n"
            "   • The inputs to (self, other) must all be mutually-comparable types but were (Text [s], Int 3)"
        )

    def test_column_op_greater_than_or_equal(self):
        d1, d2 = self.make_double_col('d1'), self.make_double_col('d2')
        i1, i2 = self.make_int_col('i1'), self.make_int_col('i2')
        b1, b2 = self.make_boolean_col('b1'), self.make_boolean_col('b2')
        s1, s2 = self.make_text_col('s1'), self.make_text_col('s2')
        dt1, dt2 = self.make_date_col('dt1'), self.make_date_col('dt2')

        # col col
        self.assertEqual("[d1] >= [d2]", (d1 >= d2).sql)
        self.assertEqual("[i1] >= [i2]", (i1 >= i2).sql)
        self.assertEqual("[b1] >= [b2]", (b1 >= b2).sql)
        self.assertEqual("[s1] >= [s2]", (s1 >= s2).sql)
        self.assertEqual("[dt1] >= [dt2]", (dt1 >= dt2).sql)

        # lit col
        self.assertEqual("[d2] <= 1.2", (1.2 >= d2).sql)
        self.assertEqual("[i2] <= 3", (3 >= i2).sql)
        self.assertEqual("[b2] <= TRUE", (True >= b2).sql)
        self.assertEqual("[s2] <= 'ABC'", ('ABC' >= s2).sql)
        self.assertEqual("[dt2] <= #2023-01-01#", (date(2023, 1, 1) >= dt2).sql)

        # col lit
        self.assertEqual("[d2] >= 1.2", (d2 >= 1.2).sql)
        self.assertEqual("[i2] >= 3", (i2 >= 3).sql)
        self.assertEqual("[b2] >= TRUE", (b2 >= True).sql)
        self.assertEqual("[s2] >= 'ABC'", (s2 >= 'ABC').sql)
        self.assertEqual("[dt2] >= #2023-01-01#", (dt2 >= date(2023, 1, 1)).sql)

    def test_column_op_greater_than_or_equal_validation(self):
        self.assertErrorsWithMessage(
            lambda: self.make_text_col('s') >= 3,
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: self.make_text_col('s') >= 3,\n"
            "There was 1 failed constraint on >= (greater that or equal):\n"
            "   • The inputs to (self, other) must all be mutually-comparable types but were (Text [s], Int 3)"
        )

    def test_column_op_power(self):
        d = self.make_double_col('d')
        r = d**0.5
        self.assertEqual("power([d], 0.5)", r.sql)
        self.assertEqual(DType.Double, r.dtype)

    def test_column_op_power_validation(self):
        self.assertErrorsWithMessage(
            lambda: self.make_text_col('s') ** 2,
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: self.make_text_col('s') ** 2,\n"
            "There was 1 failed constraint on ** (power):\n"
            "   • The input to 'self' must be Int/BigInt/Double/Decimal but was Text=[s]"
        )
        self.assertErrorsWithMessage(
            lambda: self.make_double_col('d') ** 'abc',
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: self.make_double_col('d') ** 'abc',\n"
            "There was 1 failed constraint on ** (power):\n"
            "   • The input to 'power' must be Int/BigInt/Double/Decimal but was Text='abc'"
        )

    def test_column_op_and(self):
        b1, b2 = self.make_boolean_col('b1'), self.make_boolean_col('b2')

        # col col
        r = (b1 & b2)
        self.assertEqual("[b1] AND [b2]", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # lit col
        r = (True & b2)
        self.assertEqual("TRUE AND [b2]", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # col lit
        r = (b1 & True)
        self.assertEqual("[b1] AND TRUE", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_column_op_and_validation(self):
        self.assertErrorsWithMessage(
            lambda: self.make_boolean_col('b') & 123,
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: self.make_boolean_col('b') & 123,\n"
            "There was 1 failed constraint on & (and):\n"
            "   • The input to 'other' must be Boolean but was Int=123"
        )

    def test_column_op_or(self):
        b1, b2 = self.make_boolean_col('b1'), self.make_boolean_col('b2')

        # col col
        r = (b1 | b2)
        self.assertEqual("[b1] OR [b2]", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # lit col
        r = (True | b2)
        self.assertEqual("TRUE OR [b2]", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # col lit
        r = (b1 | True)
        self.assertEqual("[b1] OR TRUE", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_column_op_or_validation(self):
        self.assertErrorsWithMessage(
            lambda: self.make_boolean_col('b') | 123,
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: self.make_boolean_col('b') | 123,\n"
            "There was 1 failed constraint on | (or):\n"
            "   • The input to 'other' must be Boolean but was Int=123"
        )
