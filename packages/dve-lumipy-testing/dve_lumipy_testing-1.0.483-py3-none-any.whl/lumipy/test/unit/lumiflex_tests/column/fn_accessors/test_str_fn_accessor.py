from lumipy.lumiflex._column.accessors.str_fn_accessor import StrFnAccessor
from lumipy.lumiflex._metadata.dtype import DType
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestStrColFnAccessor(SqlTestCase):

    def test_error_on_non_text_column(self):
        self.assertErrorsWithMessage(
            lambda: self.make_int_col('col').str.lower(),
            AttributeError,
            "To use .str accessor the column must be Text type, but was Int.",
        )

    def test_str_function_accessor_ctor(self):
        s = self.make_text_col('s')
        sfa = StrFnAccessor(s)
        self.assertHashEqual(s, sfa._column)

    def test_str_function_accessor_concat(self):
        s = self.make_text_col('s')
        r = s.str.concat('ABC')
        self.assertEqual("[s] || 'ABC'", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_concat_validation(self):
        col = self.make_text_col('s')
        with self.assertRaises(TypeError) as te:
            col.str.concat(123)
        self.assertIn(
            "Invalid input detected at\n"
            "   → col.str.concat(123)\n"
            "There was 1 failed constraint on .str.concat():\n"
            "   • The input to 'other' must be Text but was Int=123",
            str(te.exception)
        )

    def test_str_function_accessor_upper(self):
        col = self.make_text_col('s')
        r = col.str.upper()
        self.assertEqual("upper([s])", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_lower(self):
        col = self.make_text_col('s')
        r = col.str.lower()
        self.assertEqual("lower([s])", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_len(self):
        col = self.make_text_col('s')
        r = col.str.len()
        self.assertEqual("length([s])", r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_str_function_accessor_trim(self):
        col = self.make_text_col('s')

        # defaults
        r = col.str.trim()
        self.assertEqual("trim([s], ' ')", r.sql)
        self.assertEqual(DType.Text, r.dtype)
        # trim non-space
        r = col.str.trim('xyz')
        self.assertEqual("trim([s], 'xyz')", r.sql)
        self.assertEqual(DType.Text, r.dtype)

        # BOTH
        # defaults
        r = col.str.trim(trim_type='both')
        self.assertEqual("trim([s], ' ')", r.sql)
        self.assertEqual(DType.Text, r.dtype)
        # trim non-space
        r = col.str.trim('xyz', 'both')
        self.assertEqual("trim([s], 'xyz')", r.sql)
        self.assertEqual(DType.Text, r.dtype)

        # LEFT
        # defaults - explicit both
        r = col.str.trim(trim_type='left')
        self.assertEqual("ltrim([s], ' ')", r.sql)
        self.assertEqual(DType.Text, r.dtype)
        # trim non-space
        r = col.str.trim('xyz', 'left')
        self.assertEqual("ltrim([s], 'xyz')", r.sql)
        self.assertEqual(DType.Text, r.dtype)

        # RIGHT
        # defaults - explicit both
        r = col.str.trim(trim_type='right')
        self.assertEqual("rtrim([s], ' ')", r.sql)
        self.assertEqual(DType.Text, r.dtype)
        # trim non-space
        r = col.str.trim('xyz', 'right')
        self.assertEqual("rtrim([s], 'xyz')", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_trim_validation(self):

        self.assertErrorsWithMessage(
            lambda: self.make_text_col('s').str.trim(trim_type='invalid'),
            ValueError,
            "trim_type must be one of left, right, both but was 'invalid'."
        )

        self.assertErrorsWithMessage(
            lambda: self.make_text_col('s').str.trim(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: self.make_text_col('s').str.trim(123),\n"
            "There was 1 failed constraint on .str.trim():\n"
            "   • The input to 'trim_str' must be Text but was Int=123"
        )

    def test_str_function_accessor_like(self):
        s = self.make_text_col('s')
        r = s.str.like('get%')
        self.assertEqual('[s] LIKE \'get%\'', r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        c = self.make_text_col('c')
        r = s.str.like(c)
        self.assertEqual('[s] LIKE [c]', r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_str_function_accessor_like_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.like(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.like(123),\n"
            "There was 1 failed constraint on .str.like():\n"
            "   • The input to 'pattern' must be Text but was Int=123"
        )

    def test_str_function_accessor_not_like(self):
        s1 = self.make_text_col('s1')
        s2 = self.make_text_col('s2')

        r = s1.str.not_like('%abc')
        self.assertEqual("[s1] NOT LIKE '%abc'", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)
        r = s1.str.not_like(s2)
        self.assertEqual("[s1] NOT LIKE [s2]", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_str_function_accessor_not_like_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.not_like(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.not_like(123),\n"
            "There was 1 failed constraint on .str.not_like():\n"
            "   • The input to 'pattern' must be Text but was Int=123"
        )

    def test_str_function_accessor_glob(self):
        s1 = self.make_text_col('s1')
        s2 = self.make_text_col('s2')

        r = s1.str.glob('*abc')
        self.assertEqual("[s1] GLOB '*abc'", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)
        r = s1.str.glob(s2)
        self.assertEqual("[s1] GLOB [s2]", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_str_function_accessor_glob_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.glob(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.glob(123),\n"
            "There was 1 failed constraint on .str.glob():\n"
            "   • The input to 'pattern' must be Text but was Int=123"
        )

    def test_str_function_accessor_not_glob(self):
        s1 = self.make_text_col('s1')
        s2 = self.make_text_col('s2')

        r = s1.str.not_glob('*abc')
        self.assertEqual("[s1] NOT GLOB '*abc'", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)
        r = s1.str.not_glob(s2)
        self.assertEqual("[s1] NOT GLOB [s2]", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_str_function_accessor_not_glob_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.not_glob(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.not_glob(123),\n"
            "There was 1 failed constraint on .str.not_glob():\n"
            "   • The input to 'pattern' must be Text but was Int=123"
        )

    def test_str_function_accessor_regexp(self):
        s1 = self.make_text_col('s1')
        s2 = self.make_text_col('s2')

        r = s1.str.regexp('<pattern>')
        self.assertEqual("[s1] REGEXP '<pattern>'", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)
        r = s1.str.regexp(s2)
        self.assertEqual("[s1] REGEXP [s2]", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_str_function_accessor_regexp_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.regexp(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.regexp(123),\n"
            "There was 1 failed constraint on .str.regexp():\n"
            "   • The input to 'pattern' must be Text but was Int=123"
        )

    def test_str_function_accessor_not_regexp(self):
        s1 = self.make_text_col('s1')
        s2 = self.make_text_col('s2')

        r = s1.str.not_regexp('<pattern>')
        self.assertEqual("[s1] NOT REGEXP '<pattern>'", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)
        r = s1.str.not_regexp(s2)
        self.assertEqual("[s1] NOT REGEXP [s2]", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_str_function_accessor_not_regexp_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.not_regexp(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.not_regexp(123),\n"
            "There was 1 failed constraint on .str.not_regexp():\n"
            "   • The input to 'pattern' must be Text but was Int=123"
        )

    def test_str_function_accessor_replace(self):
        s1 = self.make_text_col('s1')
        s2 = self.make_text_col('s2')
        s3 = self.make_text_col('s3')

        r = s1.str.replace('abc', 'cba')
        self.assertEqual("replace([s1], 'abc', 'cba')", r.sql)
        self.assertEqual(DType.Text, r.dtype)

        r = s1.str.replace(s2, s3)
        self.assertEqual("replace([s1], [s2], [s3])", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_replace_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.replace(123, 999),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: s.str.replace(123, 999),\n"
            "There were 2 failed constraints on .str.replace():\n"
            "   • The input to 'old' must be Text but was Int=123\n"
            "   • The input to 'new' must be Text but was Int=999"
        )

    def test_str_function_accessor_soundex(self):
        s = self.make_text_col('s')
        r = s.str.soundex()
        self.assertEqual("soundex([s])", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_substr(self):
        s = self.make_text_col('s')
        r = s.str.substr(start=3, length=7)
        self.assertEqual("substr([s], 3, 7)", r.sql)
        self.assertEqual(DType.Text, r.dtype)

        i1, i2 = self.make_int_col('i1'), self.make_int_col('i2')
        r = s.str.substr(start=i1, length=i2)
        self.assertEqual("substr([s], [i1], [i2])", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_substr_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.substr(),
            TypeError,
            ".str.substr() is missing a required positional argument 'start'"
        )
        self.assertErrorsWithMessage(
            lambda: s.str.substr('a', 'b'),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: s.str.substr('a', 'b'),\n"
            "There were 2 failed constraints on .str.substr():\n"
            "   • The input to 'start' must be Int/BigInt but was Text='a'\n"
            "   • The input to 'length' must be Int/BigInt but was Text='b'"
        )

    def test_str_function_accessor_unicode(self):
        s = self.make_text_col('s')
        r = s.str.unicode()
        self.assertEqual("unicode([s])", r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_str_function_accessor_replicate(self):
        s = self.make_text_col('s')
        r = s.str.replicate(3)
        self.assertEqual("replicate([s], 3)", r.sql)
        self.assertEqual(DType.Text, r.dtype)

        i = self.make_int_col('i')
        r = s.str.replicate(i)
        self.assertEqual("replicate([s], [i])", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_replicate_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.replicate('abc'),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.replicate('abc'),\n"
            "There was 1 failed constraint on .str.replicate():\n"
            "   • The input to 'times' must be Int/BigInt but was Text='abc'"
        )

    def test_str_function_accessor_reverse(self):
        s = self.make_text_col('s')
        r = s.str.reverse()
        self.assertEqual("reverse([s])", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_left_str(self):
        s = self.make_text_col('s')
        r = s.str.left_str(100)
        self.assertEqual("leftstr([s], 100)", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_right_str(self):
        s = self.make_text_col('s')
        r = s.str.right_str(100)
        self.assertEqual("rightstr([s], 100)", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_head_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.left_str('a'),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.left_str('a'),\n"
            "There was 1 failed constraint on .str.left_str():\n"
            "   • The input to 'n' must be Int/BigInt but was Text='a'"
        )

    def test_str_function_accessor_tail_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.left_str('a'),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.left_str('a'),\n"
            "There was 1 failed constraint on .str.left_str():\n"
            "   • The input to 'n' must be Int/BigInt but was Text='a'"
        )

    def test_str_function_accessor_filter(self):
        s1 = self.make_text_col('s1')

        r = s1.str.filter('ABC')
        self.assertEqual("strfilter([s1], 'ABC')", r.sql)
        self.assertEqual(DType.Text, r.dtype)

        s2 = self.make_text_col('s2')
        r = s1.str.filter(s2)
        self.assertEqual("strfilter([s1], [s2])", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_filter_validation(self):
        s1 = self.make_text_col('s1')
        self.assertErrorsWithMessage(
            lambda: s1.str.filter(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s1.str.filter(123),\n"
            "There was 1 failed constraint on .str.filter():\n"
            "   • The input to 'filter_str' must be Text but was Int=123"
        )

    def test_str_function_accessor_index(self):
        s1 = self.make_text_col('s1')
        r = s1.str.index('abc', 2)
        self.assertEqual("charindex([s1], 'abc', 2)", r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_str_function_accessor_index_validation(self):
        s1 = self.make_text_col('s1')
        self.assertErrorsWithMessage(
            lambda: s1.str.index(1, 'abc'),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: s1.str.index(1, 'abc'),\n"
            "There were 2 failed constraints on .str.index():\n"
            "   • The input to 'substr' must be Text but was Int=1\n"
            "   • The input to 'start_position' must be Int/BigInt but was Text='abc'"
        )

    def test_str_function_accessor_proper(self):
        s = self.make_text_col('s')
        r = s.str.proper()
        self.assertEqual("proper([s])", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_contains(self):
        s = self.make_text_col('s')

        # default
        r = s.str.contains('abc')
        self.assertEqual("[s] LIKE (('%' || 'abc') || '%')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # case sensitive
        r = s.str.contains('abc', True)
        self.assertEqual("[s] GLOB (('*' || 'abc') || '*')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_str_function_accessor_contains_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.contains(123, 321),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: s.str.contains(123, 321),\n"
            "There were 2 failed constraints on .str.contains():\n"
            "   • The input to 'sub_str' must be Text but was Int=123\n"
            "   • The input to 'case_sensitive' must be Boolean but was Int=321"
        )

    def test_str_function_accessor_startswith(self):
        s = self.make_text_col('s')

        # default
        r = s.str.startswith('abc')
        self.assertEqual("[s] LIKE ('abc' || '%')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # case sensitive
        r = s.str.startswith('abc', True)
        self.assertEqual("[s] GLOB ('abc' || '*')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_str_function_accessor_startswith_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.startswith(123, 321),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: s.str.startswith(123, 321),\n"
            "There were 2 failed constraints on .str.startswith():\n"
            "   • The input to 'sub_str' must be Text but was Int=123\n"
            "   • The input to 'case_sensitive' must be Boolean but was Int=321"
        )

    def test_str_function_accessor_endswith(self):
        s = self.make_text_col('s')

        # default
        r = s.str.endswith('abc')
        self.assertEqual("[s] LIKE ('%' || 'abc')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

        # case sensitive
        r = s.str.endswith('abc', True)
        self.assertEqual("[s] GLOB ('*' || 'abc')", r.sql)
        self.assertEqual(DType.Boolean, r.dtype)

    def test_str_function_accessor_endswith_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.endswith(123, 321),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: s.str.endswith(123, 321),\n"
            "There were 2 failed constraints on .str.endswith():\n"
            "   • The input to 'sub_str' must be Text but was Int=123\n"
            "   • The input to 'case_sensitive' must be Boolean but was Int=321"
        )

    def test_str_function_accessor_to_date(self):
        s = self.make_text_col('s')
        r = s.str.to_date('yyyy/mm/dd')
        self.assertEqual("to_date([s], 'yyyy/mm/dd')", r.sql)
        self.assertEqual(DType.Date, r.dtype)

    def test_str_function_accessor_to_date_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.to_date(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.to_date(123),\n"
            "There was 1 failed constraint on .str.to_date():\n"
            "   • The input to 'fmt' must be Text but was Int=123"
        )

    def test_str_function_accessor_group_concat(self):
        s = self.make_text_col('s')
        r = s.str.group_concat('|')
        self.assertEqual("group_concat([s], '|')", r.sql)
        self.assertEqual(DType.Text, r.dtype)
        self.assertEqual("aggfunc", r.get_label())

    def test_str_function_accessor_group_concat_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.group_concat(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.group_concat(123),\n"
            "There was 1 failed constraint on .str.group_concat():\n"
            "   • The input to 'separator' must be Text but was Int=123"
        )

    def test_str_function_accessor_edit_distance(self):
        s = self.make_text_col('s')
        r = s.str.edit_distance('getinsturment')
        self.assertEqual("edit_distance([s], 'getinsturment')", r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_str_function_accessor_edit_distance_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.edit_distance(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.edit_distance(123),\n"
            "There was 1 failed constraint on .str.edit_distance():\n"
            "   • The input to 'other' must be Text but was Int=123"
        )

    def test_str_function_accessor_regexp_match(self):
        s = self.make_text_col('s')
        r = s.str.regexp_match('pattern')
        self.assertEqual("regexp_match([s], 'pattern')", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_regexp_match_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.regexp_match(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.regexp_match(123),\n"
            "There was 1 failed constraint on .str.regexp_match():\n"
            "   • The input to 'pattern' must be Text but was Int=123"
        )

    def test_str_function_accessor_regexp_matches(self):
        s = self.make_text_col('s')
        r = s.str.regexp_matches('pattern')
        self.assertEqual("regexp_matches([s], 'pattern')", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_regexp_matches_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.regexp_matches(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.regexp_matches(123),\n"
            "There was 1 failed constraint on .str.regexp_matches():\n"
            "   • The input to 'pattern' must be Text but was Int=123"
        )

    def test_str_function_accessor_regexp_match_loc(self):
        s = self.make_text_col('s')
        r = s.str.regexp_match_loc('pattern')
        self.assertEqual("regexp_match_location([s], 'pattern')", r.sql)
        self.assertEqual(DType.Int, r.dtype)

    def test_str_function_accessor_regexp_matches_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.regexp_match_loc(123),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.regexp_match_loc(123),\n"
            "There was 1 failed constraint on .str.regexp_match_loc():\n"
            "   • The input to 'pattern' must be Text but was Int=123"
        )

    def test_str_function_accessor_regexp_replace(self):
        s = self.make_text_col('s')
        r = s.str.regexp_replace('pattern', 'replace')
        self.assertEqual("regexp_replace([s], 'pattern', 'replace')", r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_regexp_replace_validation(self):
        s = self.make_text_col('s')
        self.assertErrorsWithMessage(
            lambda: s.str.regexp_replace(123, 321),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: s.str.regexp_replace(123, 321),\n"
            "There were 2 failed constraints on .str.regexp_replace():\n"
            "   • The input to 'pattern' must be Text but was Int=123\n"
            "   • The input to 'value' must be Text but was Int=321"
        )

    def test_str_function_accessor_pad(self):
        s = self.make_text_col('s')

        r = s.str.pad(4, 'right')
        self.assertEqual('padr([s], 4)', r.sql)
        self.assertEqual(DType.Text, r.dtype)

        r = s.str.pad(4, 'left')
        self.assertEqual('padl([s], 4)', r.sql)
        self.assertEqual(DType.Text, r.dtype)

        r = s.str.pad(4, 'both')
        self.assertEqual('padc([s], 4)', r.sql)
        self.assertEqual(DType.Text, r.dtype)

    def test_str_function_accessor_pad_validation(self):

        s = self.make_text_col('s')

        self.assertErrorsWithMessage(
            lambda: s.str.pad('abc', 'right'),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: s.str.pad('abc', 'right'),\n"
            "There was 1 failed constraint on .str.pad():\n"
            "   • The input to 'length' must be Int/BigInt but was Text='abc'"
        )

        self.assertErrorsWithMessage(
            lambda: s.str.pad(5, 'not right'),
            ValueError,
            "pad_type must be one of left, right, both but was 'not right'."
        )
