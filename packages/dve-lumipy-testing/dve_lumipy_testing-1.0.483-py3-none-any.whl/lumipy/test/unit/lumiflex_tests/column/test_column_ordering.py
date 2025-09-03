from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._column.ordering import Ordering
from pydantic import ValidationError
from inspect import signature


class TestColumnOrdering(SqlTestCase):

    def test_ordering_ctor(self):
        col = self.make_double_col('d')
        order = Ordering(label='asc', parents=(col,))
        self.assertEqual(order.get_label(), 'asc')
        self.assertEqual(len(order.get_parents()), 1)
        self.assertHashEqual(order.get_parents()[0], col)

    def test_ordering_ctor_label_validation(self):
        col1 = self.make_double_col('d1')

        self.assertErrorsWithMessage(
            lambda: Ordering(label='invalid', parents=(col1, )),
            ValidationError,
            "1 validation error for Ordering\n"
            "label\n"
            "Input should be 'asc' or 'desc' [type=literal_error, input_value='invalid', input_type=str]\n"
            "For further information visit https://errors.pydantic.dev/xxx/v/literal_error",
            [3]
        )

    def test_ordering_ctor_parents_validation(self):
        col1 = self.make_double_col('d1')
        col2 = self.make_double_col('d2')

        self.assertErrorsWithMessage(
            lambda: Ordering(label='asc', parents=(col1, col2)),
            ValueError,
            '1 validation error for Ordering\n'
            'parents\n'
            "Value error, Ordering must have exactly one parent, received 2. [type=value_error, input_value=(Column(\n"
            "label_: 'data...alse )\n"
            "sql: '[d2]'\n"
            ")), input_type=tuple]\n"
            "For further information visit https://errors.pydantic.dev/xxx/v/value_error",
            [6]
        )

        self.assertErrorsWithMessage(
            lambda: Ordering(label='asc', parents=(col1.asc(),)),
            TypeError,
            "Parent must be Column type but was Ordering."
        )

    def test_ordering_create_from_col_method(self):
        col = self.make_double_col('d')

        col_asc = col.asc()
        self.assertEqual('[d] ASC', col_asc.sql)
        self.assertIsInstance(col_asc, Ordering)
        col_asc = col.ascending()
        self.assertEqual('[d] ASC', col_asc.sql)
        self.assertIsInstance(col_asc, Ordering)

        col_desc = col.desc()
        self.assertEqual('[d] DESC', col_desc.sql)
        self.assertIsInstance(col_desc, Ordering)
        col_desc = col.descending()
        self.assertEqual('[d] DESC', col_desc.sql)
        self.assertIsInstance(col_desc, Ordering)

    def test_column_ordering_methods_have_type_hints(self):
        d = self.make_double_col('d')

        sig = signature(d.asc)
        self.assertEqual(Ordering.__name__, sig.return_annotation)
        sig = signature(d.ascending)
        self.assertEqual(Ordering.__name__, sig.return_annotation)
        sig = signature(d.desc)
        self.assertEqual(Ordering.__name__, sig.return_annotation)
        sig = signature(d.descending)
        self.assertEqual(Ordering.__name__, sig.return_annotation)
