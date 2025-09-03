from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase


class TestContentMethods(SqlTestCase):

    def test_table_content_update(self):
        table = self.make_table()
        content = self.make_table_content(table)

    def test_table_content_get_columns(self):
        pass

    def test_table_content_get_sql(self):
        pass
