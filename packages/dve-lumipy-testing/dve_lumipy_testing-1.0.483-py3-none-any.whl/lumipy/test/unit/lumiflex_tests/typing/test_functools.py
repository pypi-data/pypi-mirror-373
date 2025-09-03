from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex._method_tools.method_tools import assemble_arguments


class TestFunctools(SqlTestCase):

    def test_assemble_arguments_with_ellipsis_option(self):

        def decorator(fn):

            def wrapper(self, *args, **kwargs):
                names, values = assemble_arguments('test', fn, self, args, kwargs, 'ellipsis')
                return fn(*values)

            return wrapper

        @decorator
        def __call__(self, a, b, c):
            return a, b, c

        res = __call__('self')
        self.assertSequenceEqual([..., ..., ...], res)

        res = __call__('self', 1, 2)
        self.assertSequenceEqual([1, 2, ...], res)

        res = __call__('self', 1, c=2)
        self.assertSequenceEqual([1, ..., 2], res)

        res = __call__('self', b=1, c=2)
        self.assertSequenceEqual([..., 1, 2], res)
