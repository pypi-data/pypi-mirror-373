from lumipy.lumiflex._window.window import OverFrame
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestOverFrame(SqlTestCase):

    def test_over_frame_create(self):
        frame = OverFrame(lower=10, upper=12, exclude='group')
        self.assertEqual('over frame', frame.get_label())
        self.assertEqual(10, frame.lower)
        self.assertEqual(12, frame.upper)
        self.assertTrue(frame.has_content())
        self.assertEqual('group', frame.exclude)

    def test_over_frame_defaults(self):
        frame = OverFrame()
        self.assertEqual('over frame', frame.get_label())
        self.assertEqual(None, frame.lower)
        self.assertEqual(0, frame.upper)
        self.assertTrue(frame.has_content())
        self.assertEqual('no others', frame.exclude)

    def test_over_frame_get_sql(self):

        frame = OverFrame(lower=10, upper=12)
        self.assertEqual("ROWS BETWEEN 10 PRECEDING AND 12 FOLLOWING EXCLUDE NO OTHERS", frame.get_sql())

        here_to_inf = OverFrame(lower=0, upper=None)
        self.assertEqual("ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING EXCLUDE NO OTHERS", here_to_inf.get_sql())

        inf_to_here = OverFrame(lower=None, upper=0)
        self.assertEqual("ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS", inf_to_here.get_sql())

        ten_to_inf = OverFrame(lower=10, upper=None)
        self.assertEqual("ROWS BETWEEN 10 PRECEDING AND UNBOUNDED FOLLOWING EXCLUDE NO OTHERS", ten_to_inf.get_sql())

        inf_to_ten = OverFrame(lower=None, upper=10)
        self.assertEqual("ROWS BETWEEN UNBOUNDED PRECEDING AND 10 FOLLOWING EXCLUDE NO OTHERS", inf_to_ten.get_sql())

        here_to_ten = OverFrame(lower=0, upper=10)
        self.assertEqual("ROWS BETWEEN CURRENT ROW AND 10 FOLLOWING EXCLUDE NO OTHERS", here_to_ten.get_sql())

        ten_to_here = OverFrame(lower=10, upper=0)
        self.assertEqual("ROWS BETWEEN 10 PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS", ten_to_here.get_sql())
