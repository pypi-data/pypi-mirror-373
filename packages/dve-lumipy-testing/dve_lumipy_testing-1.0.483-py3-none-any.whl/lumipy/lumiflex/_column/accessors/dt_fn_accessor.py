from lumipy import when
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._method_tools.constraints import Is, Are
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex.column import Column
from .base_fn_accessor import BaseFnAccessor


class DtFnAccessor(BaseFnAccessor):

    def __init__(self, column: Column):
        super().__init__('dt', column, Is.timelike)

    @input_constraints(..., Is.text, Are.all_text, name='.dt.strftime()')
    def strftime(self, fmt: str = '%Y-%m-%dT%H:%M:%S', *args: str) -> Column:
        """Apply a strftime function to this date/datetime value. Strftime will convert a datetime to a string
        given a format and some optional modifiers.

        Notes:
            https://www.sqlite.org/lang_datefunc.html

        Args:
            fmt (Optional[str]): the format to use when converting to string. Defaults to "YYYY-MM-DDTHH:MM:SS"
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this conversion.

        """
        fn = lambda *xs: f'strftime({", ".join(a.sql for a in xs)})'
        return Column(fn=fn, parents=(fmt, self._column) + args, dtype=DType.Text, label='func')

    @input_constraints(..., Are.all_text, name='.dt.date_str()')
    def date_str(self, *args: str) -> Column:
        """Apply a date function to this date/datetime. Date will take the date part of the date/datetime value, and some
        optional modifiers, then convert it to a string.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this conversion.

        """
        fn = lambda *xs: f'date({", ".join(a.sql for a in xs)})'
        return Column(fn=fn, parents=(self._column,) + args, dtype=DType.Text, label='func')

    @input_constraints(..., Are.all_text, name='.dt.time_str()')
    def time_str(self, *args: str) -> Column:
        """Apply a time function to this date/datetime. Time will take the time part of the date/datetime value, and some
        optional modifiers, then convert it to a string.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this conversion.

        """
        fn = lambda *xs: f'time({", ".join(a.sql for a in xs)})'
        return Column(fn=fn, parents=(self._column,) + args, dtype=DType.Text, label='func')

    @input_constraints(..., Are.all_text, name='.dt.julian_day()')
    def julian_day(self, *args: str) -> Column:
        """Apply a julian day function to this date/datetime value. The julian day function returns the fractional
        number of days since noon GMT on Nov 24 4714 B.C., given an optional set of modifier strings.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda *xs: f'julianday({", ".join(a.sql for a in xs)})'
        return Column(fn=fn, parents=(self._column,) + args, dtype=DType.Double, label='func')

    @input_constraints(..., Are.all_text, name='.dt.unix_epoch()')
    def unix_epoch(self, *args: str) -> Column:
        """Apply a unix epoch function to this date/datetime. This will compute a unix timestamp - the number of seconds
        since midnight UTC 1970-01-01, given an optional set of modifier strings.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda *xs: f'strftime(\'%s\', {", ".join(a.sql for a in xs)})'
        return Column(fn=fn, parents=(self._column,) + args, dtype=DType.Int, label='func')

    @input_constraints(..., Are.all_text, name='.dt.year()')
    def year(self, *args: str) -> Column:
        """Apply a year function to this date/datetime. This will return the value of the year as an int.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        return self.strftime('%Y', *args).cast(int)

    @input_constraints(..., Are.all_text, name='.dt.month_of_year()')
    def month_of_year(self, *args: str) -> Column:
        """Apply a month of year function to this date/datetime. This will return the number of the month as an int where
        1 == January.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        return self.strftime('%m', *args).cast(int)

    @input_constraints(..., Are.all_text, name='.dt.week_of_year()')
    def week_of_year(self, *args: str) -> Column:
        """Apply a week of year function to this date/datetime. This will return the number of the week in the year
        as an int starting from 0.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        return self.strftime('%W', *args).cast(int)

    @input_constraints(..., Are.all_text, name='.dt.day_of_year()')
    def day_of_year(self, *args: str) -> Column:
        """Apply a day of year function to this date/datetime. This will return the day of the year as an int starting
        from 1 for the 1st of January.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        return self.strftime('%j', *args).cast(int)

    @input_constraints(..., Are.all_text, name='.dt.day_of_month()')
    def day_of_month(self, *args: str) -> Column:
        """Apply a day of month function to this date/datetime. This will return the number of the day in the month as
        an integer.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        return self.strftime('%d', *args).cast(int)

    @input_constraints(..., Are.all_text, name='.dt.day_of_week()')
    def day_of_week(self, *args: str) -> Column:
        """Apply a day of the week function to this date/datetime. This will return the day of the week as an integer
        starting with 0 (Monday) and ending with 6 (Sunday).

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        # plus 6 mod 7 because SQLite starts with Sunday=0. This way it matches pandas.
        return (self.strftime('%w', *args).cast(int) + 6) % 7

    @input_constraints(..., Are.all_text, name='.dt.hour_of_day()')
    def hour_of_day(self, *args: str) -> Column:
        """Apply an hour of day function to this date/datetime. This will return the hour of the day as an integer.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        return self.strftime('%H', *args).cast(int)

    @input_constraints(..., Are.all_text, name='.dt.minute_of_hour()')
    def minute_of_hour(self, *args: str) -> Column:
        """Apply a minute of the hour function to this date/datetime. This will return the number of minutes past the
        hour as an integer.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        return self.strftime('%M', *args).cast(int)

    @input_constraints(..., Are.all_text, name='.dt.second_of_minute()')
    def second_of_minute(self, *args: str) -> Column:
        """Apply a second of the minute function to this date/datetime. This will return the number of seconds elapsed
        in the given minute as an integer.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        return self.strftime('%S', *args).cast(int)

    @input_constraints(..., Are.all_text, name='.dt.day_name()')
    def day_name(self, *args: str) -> Column:
        """Apply a day name function to this date/datetime. This will return the name of the day of the week as a string.

        Args:
            *args (str): an optional set of modifier strings. See https://www.sqlite.org/lang_datefunc.html

        Returns:
            Column: column instance representing this calculation.

        """
        day_num = self.day_of_week(*args)
        names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        named_day = when(day_num == 0).then(names[0])
        for i, day in enumerate(names[1:]):
            named_day = named_day.when(day_num == i + 1).then(day)
        return named_day.otherwise(None)

    # todo: further coverage of the set of pandas equivalents...
