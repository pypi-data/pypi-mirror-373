from datetime import date

from lumipy.lumiflex._column.make import make
from lumipy.lumiflex.column import Column
from lumipy.lumiflex._method_tools.decorator import input_constraints
from lumipy.lumiflex._method_tools.constraints import Is, Are
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestColDtypeCheckDecorator(SqlTestCase):

    def test_column_decorator_must_have_name(self):
        dec = input_constraints(Is.numeric, Is.text)
        with self.assertRaises(ValueError) as ve:
            # errors at runtime. pydantic doesn't like errors during class init
            dec(lambda *args: args)
        self.assertIn(
            "Function must be labelled by using name=<fn name> in @dtype_check()",
            str(ve.exception)
        )

    def test_column_decorator_input_conversion(self):

        decorator = input_constraints(Is.numeric, Is.numeric, name='test1')

        def plain_fn(self, a):
            return self, a

        decorated_fn = decorator(plain_fn)

        # Assert that the underlying dummy function is just passes them through
        self.assertEqual((1, 2), plain_fn(1, 2))

        # When literals are passed through they should be converted to Column
        _d1, _d2 = decorated_fn(1, 2)

        # Assert that they are Column and match the expected values
        self.assertIsInstance(_d1, Column)
        self.assertIsInstance(_d2, Column)

        d1, d2 = make(1), make(2)
        self.assertHashEqual(d1, _d1)
        self.assertHashEqual(d2, _d2)

    def test_column_decorator_input_type_check(self):

        decorator = input_constraints(Is.numeric, Is.numeric, name='test1')

        def plain_fn(self, a):
            return self, a

        # Assert that the underlying dummy function is just passes them through
        self.assertEqual((1, 2), plain_fn(1, 2))

        decorated_fn = decorator(plain_fn)
        self.assertErrorsWithMessage(
            lambda: decorated_fn(1, 'ABC'),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: decorated_fn(1, 'ABC'),\n"
            "There was 1 failed constraint on test1:\n"
            "   • The input to 'a' must be Int/BigInt/Double/Decimal but was Text='ABC'"
        )
        self.assertErrorsWithMessage(
            lambda: decorated_fn('CBA', 1),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: decorated_fn('CBA', 1),\n"
            "There was 1 failed constraint on test1:\n"
            "   • The input to 'self' must be Int/BigInt/Double/Decimal but was Text='CBA'"
        )

        decorated_fn = decorator(plain_fn)
        with self.assertRaises(TypeError) as ve:
            decorated_fn('CBA', 'ABC')
        self.assertIn(
            "Invalid inputs detected at\n"
            "   → decorated_fn('CBA', 'ABC')\n"
            "There were 2 failed constraints on test1:\n"
            "   • The input to 'self' must be Int/BigInt/Double/Decimal but was Text='CBA'\n"
            "   • The input to 'a' must be Int/BigInt/Double/Decimal but was Text='ABC'",
            str(ve.exception)
        )

    def test_column_decorator_conversion_skips_ellipsis_values(self):

        variants = (
            (..., Is.numeric, Is.numeric),
            (Is.numeric, ..., Is.numeric),
            (Is.numeric, Is.numeric, ...),
            (..., ..., Is.numeric),
            (..., Is.numeric, ...),
            (Is.numeric, ..., ...),
            (..., ..., ...)
        )

        def plain_fn(x, y, z):
            return x, y, z

        in_vals = (1, 2, 3)

        for constraints in variants:

            decorator = input_constraints(*constraints, name='test')

            fn = decorator(plain_fn)
            out_vals = fn(*in_vals)
            for v, v_, constr in zip(in_vals, out_vals, constraints):
                if constr is ...:
                    self.assertIsInstance(v_, type(v))
                    self.assertEqual(v, v_)
                else:
                    self.assertIsInstance(v_, Column)
                    self.assertHashEqual(make(v), v_)

    def test_column_decorator_constraint_skips_ellipsis_values(self):

        def plain_fn(x, y, z):
            return x, y, z

        in_vals = ('a', 'b', 'c')

        # No checks = no error, no conversions so you just get the same back
        decorator = input_constraints(..., ..., ..., name='test')
        fn = decorator(plain_fn)
        out_vals = fn(*in_vals)
        self.assertSequenceEqual(in_vals, out_vals)

        # Mix of ellipsis and checks
        # Errors on bad type in the middle param only
        decorator = input_constraints(..., Is.numeric, ..., name='test')
        fn = decorator(plain_fn)
        self.assertErrorsWithMessage(
            lambda: fn(*in_vals),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: fn(*in_vals),\n"
            "There was 1 failed constraint on test:\n"
            "   • The input to 'y' must be Int/BigInt/Double/Decimal but was Text='b'"
        )

        exp_vals = ('a', make(1.2), 'b')
        obs_vals = fn('a', 1.2, 'b')
        self.assertSequenceHashEqual(exp_vals, obs_vals)

    def test_column_decorator_handles_default_arguments(self):

        def plain_fn(self, a=1, b=3, c=6):
            return a, b, c

        decorator = input_constraints(..., Is.numeric, Is.integer, Is.numeric, name='test')

        fn = decorator(plain_fn)

        exp = [make(v) for v in [1, 3, 6]]
        obs = fn('self')
        self.assertSequenceHashEqual(exp, obs)

        exp = [make(v) for v in [99, 3, 6]]
        obs = fn('self', 99)
        self.assertSequenceHashEqual(exp, obs)

        exp = [make(v) for v in [99, -99, 6]]
        obs = fn('self', 99, -99)
        self.assertSequenceHashEqual(exp, obs)

        exp = [make(v) for v in [1, 99, 6]]
        obs = fn('self', b=99)
        self.assertSequenceHashEqual(exp, obs)

    def test_column_decorator_with_arg_group_constraint(self):
        def plain_fn(a, *args):
            return (a,) + args

        decorator = input_constraints(Are.comparable, name='test')

        fn = decorator(plain_fn)
        in_vals = (1, 2, 3, 4)
        out_vals = fn(*in_vals)
        for iv, ov in zip(in_vals, out_vals):
            self.assertHashEqual(make(iv), ov)

        self.assertErrorsWithMessage(
            lambda: fn('abc', 2, 3, 4),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: fn('abc', 2, 3, 4),\n"
            "There was 1 failed constraint on test:\n"
            "   • The inputs to (self, args[0], args[1], args[2]) must all be mutually-comparable types but were"
            " (Text 'abc', Int 2, Int 3, Int 4)"
        )

    def test_column_decorator_with_mixed_individual_and_group_constraints(self):
        decorator = input_constraints(Is.timelike, Are.all_text, name='test')

        def plain_fn(dt, *args):
            return (dt,) + args

        fn = decorator(plain_fn)
        exp = (date(2022, 1, 1), 'a', 'b', 'c')
        obs = fn(*exp)
        self.assertTrue(all(isinstance(v, Column) for v in obs))
        self.assertEqual(len(exp), len(obs))
        for ov, ev in zip(obs, exp):
            self.assertHashEqual(ov, make(ev))

        # Test bad single param (dt)
        self.assertErrorsWithMessage(
            lambda: fn('2023-01-01', 'a', 'b', 'c'),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: fn('2023-01-01', 'a', 'b', 'c'),\n"
            "There was 1 failed constraint on test:\n"
            "   • The input to 'self' must be Date/DateTime but was Text='2023-01-01'"
        )

        # Test bad *args
        self.assertErrorsWithMessage(
            lambda: fn(date(2022, 1, 1), 'a', 2, True),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: fn(date(2022, 1, 1), 'a', 2, True),\n"
            "There was 1 failed constraint on test:\n"
            "   • The inputs to (args[0], args[1], args[2]) must all be Text but were (Text 'a', Int 2, Boolean TRUE)"
        )

        # Test bad single params and bad *args
        self.assertErrorsWithMessage(
            lambda: fn('2023-01-01', 'a', 99, 'c'),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: fn('2023-01-01', 'a', 99, 'c'),\n"
            "There were 2 failed constraints on test:\n"
            "   • The input to 'self' must be Date/DateTime but was Text='2023-01-01'\n"
            "   • The inputs to (args[0], args[1], args[2]) must all be Text but were (Text 'a', Int 99, Text 'c')"
        )

    def test_column_decorator_error_on_empty_required_args(self):
        decorator = input_constraints(..., Is.numeric, Is.integer, Is.numeric, name='test_method()')

        def plain_fn(self, x, y=2, z=3):
            return x, y, z

        fn = decorator(plain_fn)

        self.assertErrorsWithMessage(
            lambda: fn('self'),
            TypeError,
            "test_method() is missing a required positional argument 'x'"
        )

    def test_column_decorator_error_on_duplicated_args(self):
        decorator = input_constraints(..., Is.numeric, Is.integer, Is.numeric, name='test_method()')

        def plain_fn(self, x, y=2, z=3):
            return x, y, z

        fn = decorator(plain_fn)

        self.assertErrorsWithMessage(
            lambda: fn('self', 1, 4, y=3),
            TypeError,
            "Duplicate values in test_method() for arg 'y' ('4' and '3')"
        )

    def test_column_decorator_validation_with_None(self):

        decorator = input_constraints(..., Is.any, Is.not_null, name='test_method()')

        def plain_fn(self, x, y):
            return x, y

        fn = decorator(plain_fn)

        exp = (make(None), make(2))
        obs = fn('self', None, 2)
        self.assertSequenceHashEqual(exp, obs)

        self.assertErrorsWithMessage(
            lambda: fn('self', None, None),
            TypeError,
            "Invalid input detected at\n"
            "   → lambda: fn('self', None, None),\n"
            "There was 1 failed constraint on test_method():\n"
            "   • The input to 'y' must not be Null but was Null=NULL"
        )
