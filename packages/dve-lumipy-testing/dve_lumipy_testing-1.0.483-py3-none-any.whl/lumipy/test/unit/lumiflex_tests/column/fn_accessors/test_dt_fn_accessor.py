from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestDtFnAccessor(SqlTestCase):

    def test_error_on_non_timelike_column(self):
        self.assertErrorsWithMessage(
            lambda: self.make_text_col('col').dt.julian_day(),
            AttributeError,
            "To use .dt accessor the column must be Date/DateTime type, but was Text."
        )

    def test_strftime_with_defaults(self):
        dt1 = self.make_datetime_col('dt')
        s = dt1.dt.strftime()
        self.assertEqual("strftime('%Y-%m-%dT%H:%M:%S', [dt])", s.sql)

    def test_strftime_with_fmt_and_pos_args(self):
        dt1 = self.make_datetime_col('dt')
        s = dt1.dt.strftime('%Y-%M-%D %H:%M:%D', 'abc', 'def', 'ghi', 'jkl')
        self.assertEqual("strftime('%Y-%M-%D %H:%M:%D', [dt], 'abc', 'def', 'ghi', 'jkl')", s.sql)

    def test_strftime_pos_args_fmt_kwarg_errors(self):
        dt1 = self.make_datetime_col('dt')
        self.assertErrorsWithMessage(
            lambda: dt1.dt.strftime('abc', 'def', 'ghi', 'jkl', fmt='%Y-%M-%D %H:%M:%D'),
            TypeError,
            "Duplicate values in .dt.strftime() for arg 'fmt' ('abc' and '%Y-%M-%D %H:%M:%D')"
        )

    def test_strftime_dtype_checks(self):
        dt1 = self.make_datetime_col('dt')
        # fmt constraint
        self.assertErrorsWithMessage(
            lambda: dt1.dt.strftime(123, 'abc', 'def'),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: dt1.dt.strftime(123, 'abc', 'def'),\n"
            "There was 1 failed constraint on .dt.strftime():\n"
            "   • The input to 'fmt' must be Text but was Int=123"
        )

        # *args constraint
        self.assertErrorsWithMessage(
            lambda: dt1.dt.strftime('%Y-%M-%D %H:%M:%D', 'abc', 'def', 2.2),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: dt1.dt.strftime('%Y-%M-%D %H:%M:%D', 'abc', 'def', 2.2),\n"
            "There was 1 failed constraint on .dt.strftime():\n"
            "   • The inputs to (args[0], args[1], args[2]) must all be Text but were "
            "(Text 'abc', Text 'def', Double 2.2)"
        )

        # fmt and *args constraint
        self.assertErrorsWithMessage(
            lambda: dt1.dt.strftime(123, 'abc', 'def', 2.2),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: dt1.dt.strftime(123, 'abc', 'def', 2.2),\n"
            "There were 2 failed constraints on .dt.strftime():\n"
            "   • The input to 'fmt' must be Text but was Int=123\n"
            "   • The inputs to (args[0], args[1], args[2]) must all be Text but were "
            "(Text 'abc', Text 'def', Double 2.2)",
        )
