from __future__ import annotations

from typing import Union, Literal

from lumipy.lumiflex._metadata.dtype import DType
from lumipy.lumiflex._method_tools.constraints import Is
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex.column import Column
from .base_fn_accessor import BaseFnAccessor


class StrFnAccessor(BaseFnAccessor):

    def __init__(self, column: Column):
        super().__init__('str', column, Is.text)

    @input_constraints(..., Is.text, name='.str.concat()')
    def concat(self, other: Union[Column, str]) -> Column:
        """Apply a concatenation between this string value and another.

        Args:
            other (Union[Column, str]): the other string.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'{x.sql} || {other.sql}'
        return Column(fn=fn, parents=(self._column, other), dtype=DType.Text, label='op')

    def upper(self) -> Column:
        """Apply an upper case transform to this string. This will convert a string to all upper case.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'upper({x.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Text, label='func')

    def lower(self) -> Column:
        """Apply a lower case transform to this string. This will convert a string to all lower case.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'lower({x.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Text, label='func')

    def len(self) -> Column:
        """Apply a string length (len) calculation to this value.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x: f'length({x.sql})'
        return Column(fn=fn, parents=(self._column,), dtype=DType.Int, label='func')

    @input_constraints(..., Is.text, ..., name='.str.trim()')
    def trim(self, trim_str: Union[Column, str] = ' ', trim_type: Literal['left', 'right', 'both'] = 'both') -> Column:
        """Apply a trim operation to this string value.

        This will trim characters from the left, right or both (default = both) ends of a string.
        If no target value to trim is given the operation will trim any whitespace instead.

        Args:
            trim_str (Union[Column, str]):
            trim_type (Literal['left', 'right', 'both']):

        Returns:
            Column: column instance representing this calculation.

        """
        ok_vals = ['left', 'right', 'both']
        if trim_type not in ok_vals:
            raise ValueError(f'trim_type must be one of {", ".join(ok_vals)} but was \'{trim_type}\'.')

        char_map = {'left': 'l', 'right': 'r', 'both': ''}

        trim_type = char_map[trim_type]
        fn = lambda x, y: f'{trim_type}trim({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, trim_str), dtype=DType.Text, label='func')

    @input_constraints(..., Is.text, name='.str.like()')
    def like(self, pattern: Union[Column, str]) -> Column:
        """Apply a like condition to this string value.

        The like operation is for case-insensitive pattern matching in strings where you're looking for a value located
        somewhere in the string. There are two wildcards: '%' which matches and sequence of characters and '_' which
        matches any single character.


        Args:
            pattern (Union[Column, str]): search pattern string to use. Can be a string literal or Text-valued column.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'{x.sql} LIKE {y.sql}'
        return Column(fn=fn, parents=(self._column, pattern), dtype=DType.Boolean, label='op')

    @input_constraints(..., Is.text, name='.str.not_like()')
    def not_like(self, pattern: Union[Column, str]) -> Column:
        """Apply a not like condition to this string value.

        Not like is the logical inverse of like.
        The like operation is for case-insensitive pattern matching in strings where you're looking for a value located
        somewhere in the string. There are two wildcards: '%' which matches and sequence of characters and '_' which
        matches any single character.

        Args:
            pattern (Union[Column, str]): search pattern string to use. Can be a string literal or Text-valued column.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'{x.sql} NOT LIKE {y.sql}'
        return Column(fn=fn, parents=(self._column, pattern), dtype=DType.Boolean, label='op')

    @input_constraints(..., Is.text, name='.str.glob()')
    def glob(self, pattern: Union[Column, str]) -> Column:
        """Apply a glob condition to this string value.

        The glob operation does unix-style string pattern matching. It is case sensitive and there are two wildcards:
        '*' will match any sequence of characters '?' matches a single character.
        This expression and the argument to glob must both resolve to Text SQL value types.

        Args:
            pattern (Union[Column, str]): search pattern string to use. Can be a string literal or Text-valued column.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'{x.sql} GLOB {y.sql}'
        return Column(fn=fn, parents=(self._column, pattern), dtype=DType.Boolean, label='op')

    @input_constraints(..., Is.text, name='.str.not_glob()')
    def not_glob(self, pattern: Union[Column, str]) -> Column:
        """Apply a not glob condition to this string value.

        Negation of the glob operation that does unix-style string pattern matching. It is case sensitive and there are
        two wildcards '*' will match any sequence of characters '?' matches a single character.
        This expression and the argument to not glob must both resolve to Text SQL value types.

        Args:
            pattern (Union[Column, str]): search pattern string to use. Can be a string literal or Text-valued column.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'{x.sql} NOT GLOB {y.sql}'
        return Column(fn=fn, parents=(self._column, pattern), dtype=DType.Boolean, label='op')

    @input_constraints(..., Is.text, name='.str.regexp()')
    def regexp(self, pattern: Union[Column, str]) -> Column:
        """Apply a regexp condition to this string value.

        The regexp operation checks whether a regular expression finds a match in the input string. It is case sensitive.
        This value and the pattern arg to regexp must both resolve to Text SQL value types.

        Args:
            pattern (Union[Column, str]): search pattern string to use. Can be a string literal or Text-valued column.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'{x.sql} REGEXP {y.sql}'
        return Column(fn=fn, parents=(self._column, pattern), dtype=DType.Boolean, label='op')

    @input_constraints(..., Is.text, name='.str.not_regexp()')
    def not_regexp(self, pattern: Union[Column, str]) -> Column:
        """Apply a not regexp condition to this string value.

        The negation of the regexp condition.
        The regexp operation checks whether a regular expression finds a match in the input string. It is case sensitive.
        This value and the pattern arg to regexp must both resolve to Text SQL value types.

        Args:
            pattern (Union[Column, str]): search pattern string to use. Can be a string literal or Text-valued column.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'{x.sql} NOT REGEXP {y.sql}'
        return Column(fn=fn, parents=(self._column, pattern), dtype=DType.Boolean, label='op')

    @input_constraints(..., Is.text, Is.text, name='.str.replace()')
    def replace(self, old: Union[Column, str], new: Union[Column, str]) -> Column:
        """Apply a replace function to this string.

        Replace will replace all occurrences of a substring with a new value.

        Args:
            old (Union[Column, str]): the substring to be replaced
            new (Union[Column, str]): the value to replace the substring with.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y, z: f'replace({x.sql}, {y.sql}, {z.sql})'
        return Column(fn=fn, parents=(self._column, old, new), dtype=DType.Text, label='func')

    def soundex(self) -> Column:
        """Apply a soundex function to this string value.

        Soundex returns an English phonetic representation of a given text value.

        Returns:
            Column: column instance representing this calculation.

        """
        return Column(fn=lambda x: f'soundex({x.sql})', parents=(self._column,), dtype=DType.Text, label='func')

    @input_constraints(..., Is.integer, Is.integer, name='.str.substr()')
    def substr(self, start: Union[Column, int], length: Union[Column, int]) -> Column:
        """Apply a substring function to this string value.

        Substring will get a substring of a given length at a given location on the string.

        Args:
            start (Union[Column, int]): location of the substring.
            length (Union[Column, int]): length of the substring.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y, z: f'substr({x.sql}, {y.sql}, {z.sql})'
        return Column(fn=fn, parents=(self._column, start, length), dtype=DType.Text, label='func')

    def unicode(self) -> Column:
        """Apply a unicode function to this string value.

        Unicode SQL function returns the unicode int value for the first character in a string.

        Returns:
            Column: column instance representing this calculation.

        """
        return Column(fn=lambda x: f'unicode({x.sql})', parents=(self._column,), dtype=DType.Int, label='func')

    @input_constraints(..., Is.integer, name='.str.replicate()')
    def replicate(self, times: Union[Column, int]) -> Column:
        """Apply a replicate function to this string value.

        Replicate will return a string value repeated a give number of times. For example replicate('ABC', 3) will give
        'ABCABCABC.

        Args:
            times (Union[Column, int]): number of times to replicate.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'replicate({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, times), dtype=DType.Text, label='func')

    def reverse(self) -> Column:
        """Apply a reverse function to this string value.

        Reverse will reverse the order of the characters in a string.

        Returns:
            Column: column instance representing this calculation.

        """
        return Column(fn=lambda x: f'reverse({x.sql})', parents=(self._column,), dtype=DType.Text, label='func')

    @input_constraints(..., Is.integer, name='.str.left_str()')
    def left_str(self, n: Union[Column, int]) -> Column:
        """Apply a left string function to this string value.

        Leftstr will get the substring consisting of the first n-many character from the left.

        Args:
            n (Union[Column, int]): number of chars from the left to select.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'leftstr({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, n), dtype=DType.Text, label='func')

    @input_constraints(..., Is.integer, name='.str.right_str()')
    def right_str(self, n: Union[Column, int]) -> Column:
        """Apply a right string function to this string value.

        Rightstr will get the substring consisting of the first n-many character from the right.

        Args:
            n (Union[Column, int]): number of chars from the right to select.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'rightstr({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, n), dtype=DType.Text, label='func')

    @input_constraints(..., Is.integer, ..., name='.str.pad()')
    def pad(self, length: Union[Column, int], pad_type: Literal['left', 'right', 'both']) -> Column:
        """Apply a pad expression to this column expression.

        Pads out a string with whitespace so it reaches a given length.

        Args:
            length (Union[Column, int]): target length of padded string.
            pad_type (Literal['left', 'right', 'both']):  type of pad operation: 'right', 'left' or 'center'.

        Returns:
            Column: column instance representing this calculation.

        """
        ok_vals = ['left', 'right', 'both']
        if pad_type not in ok_vals:
            raise ValueError(f'pad_type must be one of {", ".join(ok_vals)} but was \'{pad_type}\'.')

        char_map = {
            'left': 'l',
            'right': 'r',
            'both': 'c',
        }

        pad_type = char_map[pad_type]
        fn = lambda x, y: f'pad{pad_type}({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, length), dtype=DType.Text, label='func')

    @input_constraints(..., Is.text, name='.str.filter()')
    def filter(self, filter_str: Union[Column, str]) -> Column:
        """Apply a string filter function to this string value.

        Strfilter will filter a string for the characters that exist in another string.

        Args:
            filter_str (Union[Column, str]): string or text column containing the characters to filter for.


        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'strfilter({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, filter_str), dtype=DType.Text, label='func')

    @input_constraints(..., Is.text, Is.integer, name='.str.index()')
    def index(self, substr: Union[Column, str], start_position: Union[Column, int] = 0) -> Column:
        """Apply an index function to this string value.

        Index will find the position (index) of the first occurrence of a substring after a given starting position.

        Args:
            substr (Union[Column, str]): the substring to look for.
            start_position (Union[Column, int]): the starting position for the search (defaults to 0).

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y, z: f'charindex({x.sql}, {y.sql}, {z.sql})'
        return Column(fn=fn, parents=(self._column, substr, start_position), dtype=DType.Int, label='func')

    def proper(self) -> Column:
        """Apply a proper expression to this string value.

        Proper will capitalise each word in a string delimited by spaces, so 'arthur morgan` becomes 'Arthur Morgan'

        Returns:
            Column: column instance representing this calculation.

        """
        return Column(fn=lambda x: f'proper({x.sql})', parents=(self._column,), dtype=DType.Text, label='func')

    @input_constraints(..., Is.text, Is.boolean, name='.str.contains()')
    def contains(self, sub_str: Union[Column, str], case_sensitive: bool = False) -> Column:
        """Apply a contains condition to this string value.

        Contains tests whether a string contains a substring.

        Args:
            sub_str (Union[Column, str]): the substring to look for.
            case_sensitive (bool): whether the search should be case-sensitive. Defaults to False.

        Returns:
            Column: column instance representing this calculation.

        """
        if case_sensitive.meta:
            return self._column.str.glob('*' + sub_str + '*')
        return self._column.str.like('%' + sub_str + '%')

    @input_constraints(..., Is.text, Is.boolean, name='.str.startswith()')
    def startswith(self, sub_str: Union[Column, str], case_sensitive: Union[Column, bool] = False) -> Column:
        """Apply a starts with condition to this string value.

        Startswith tests whether a string starts with a given substring.

        Args:
            sub_str (Union[Column, str]): the substring to look for.
            case_sensitive (bool): whether the search should be case-sensitive. Defaults to False.

        Returns:
            Column: column instance representing this calculation.

        """
        if case_sensitive.meta:
            return self._column.str.glob(sub_str + '*')
        return self._column.str.like(sub_str + '%')

    @input_constraints(..., Is.text, Is.boolean, name='.str.endswith()')
    def endswith(self, sub_str: Union[Column, str], case_sensitive: Union[Column, bool] = False) -> Column:
        """Apply an ends with condition to this string value.

        Endswith tests whether a string ends with a given substring.

        Args:
            sub_str (Union[Column, str]): the substring to look for.
            case_sensitive (bool): whether the search should be case-sensitive. Defaults to False.

        Returns:
            Column: column instance representing this calculation.

        """
        if case_sensitive.meta:
            return self._column.str.glob('*' + sub_str)
        return self._column.str.like('%' + sub_str)

    @input_constraints(..., Is.text, name='.str.to_date()')
    def to_date(self, fmt: Union[Column, str]) -> Column:
        """Apply a to date transform to this string value.

        To date will convert a string into a date object given a format string.

        Args:
            fmt (Union[Column, str]): the format string to use. Can be a string literal or a text valued column.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'to_date({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, fmt), dtype=DType.Date, label='func')

    @input_constraints(..., Is.text, name='.str.regexp_match()')
    def regexp_match(self, pattern: Union[Column, str]) -> Column:
        """Apply a regexp match function to this string value.

        Regexp match returns the first part of the string that matches the given regexp pattern. Defaults to NULL when
        there is no match.

        Args:
            pattern (Union[Column, str]): search pattern string to use. Can be a string literal or Text-valued column.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'regexp_match({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, pattern), dtype=DType.Text, label='func')

    @input_constraints(..., Is.text, name='.str.regexp_matches()')
    def regexp_matches(self, pattern: Union[Column, str]) -> Column:
        """Apply a regexp matches function to this string value.

        Regexp match returns the parts of the string that matches the given regexp pattern as a comma-separated list.
        Defaults to NULL when there is no match.

        Args:
            pattern (Union[Column, str]): search pattern string to use. Can be a string literal or Text-valued column.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'regexp_matches({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, pattern), dtype=DType.Text, label='func')

    @input_constraints(..., Is.text, name='.str.regexp_match_loc()')
    def regexp_match_loc(self, pattern: Union[Column, str]) -> Column:
        """Apply a regexp match location function to this string value.

        Regexp match location returns the location of the first matching substring of the given regexp pattern.
        Defaults to NULL when there is no match.

        Args:
            pattern (Union[Column, str]): search pattern string to use. Can be a string literal or Text-valued column.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'regexp_match_location({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, pattern), dtype=DType.Int, label='func')

    @input_constraints(..., Is.text, Is.text, name='.str.regexp_replace()')
    def regexp_replace(self, pattern: Union[Column, str], value: Union[Column, str]):
        """Apply a regexp replace function to this string value.

        Replaces the portions of the search string that match the regular expression with the replacement value.

        Args:
            pattern (Union[Column, str]): search pattern string to use. Can be a string literal or Text-valued column.
            value (Union[Column, str): the value to replace substring matches with.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y, z: f'regexp_replace({x.sql}, {y.sql}, {z.sql})'
        return Column(fn=fn, parents=(self._column, pattern, value), dtype=DType.Text, label='func')

    @input_constraints(..., Is.text, name='.str.group_concat()')
    def group_concat(self, separator: Union[Column, str] = ',') -> Column:
        """Apply a group concat function to these string values.

        Group concat is an aggregate function that concatenates all non-null strings in a column with a given separator.

        Args:
            separator (Union[Column, str]): the separator to use between the strings. Defaults to ','.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'group_concat({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, separator), dtype=DType.Text, label='aggfunc')

    @input_constraints(..., Is.text, name='.str.edit_distance()')
    def edit_distance(self, other: Union[Column, str]) -> Column:
        """Apply an edit distance (Levenshtein distance) between two string values.

        The edit distance is a measure of distance between two strings. It is the number of single character edits
        required to turn one string into the other (insertions, deletions, substitutions). The edit distance function
        in Luminesce is case-insensitive.

        Args:
            other (Union[Column, str]): the other string to calculate the distance to.

        Returns:
            Column: column instance representing this calculation.

        """
        fn = lambda x, y: f'edit_distance({x.sql}, {y.sql})'
        return Column(fn=fn, parents=(self._column, other), dtype=DType.Int, label='func')

    # todo: check for missing pandas equivalents
