from lumipy.lumiflex._atlas.metafactory import MetaFactory
from lumipy.test.unit.lumiflex_tests.utils import SqlTestCase
from lumipy.lumiflex.table import Table
from lumipy.lumiflex._metadata.dtype import DType
from inspect import signature
from datetime import date, datetime


class TestMetaFactory(SqlTestCase):

    def test_metafactory_instance_getattribute_overload(self):
        meta = self.make_provider_meta('My.Test.Provider', n_params=4, n_tv_params=2)
        client = self.make_dummy_client()

        # Create class by instantiating metaclass
        cls = MetaFactory(meta, client)
        self.assertEqual('MyTestProviderFactory', cls.__name__)

        # Create object by instantiating class
        obj = cls()

        # normal bad attribute
        self.assertErrorsWithMessage(
            lambda: obj.not_there,
            AttributeError,
            "'MyTestProviderFactory' object has no attribute 'not_there'"
        )

        # special message for select
        self.assertErrorsWithMessage(
            lambda: obj.select(),
            AttributeError,
            "\'MyTestProviderFactory\' has no attribute \'select\'.\n"
            "To start building a query you need to make the provider table object. Try calling the atlas attribute and then chaining on .select(),\n"
            "for example:\n"
            "    t = atlas.my_test_provider()\n"
            "or\n"
            "    t = atlas[\"My.Test.Provider\"]()\n"
            "Then call .select() to start building your query\n"
            "    query = t.select(\"^\")\n"
            "and finally call .go() to run the query and get your dataframe back\n"
            "    df = query.go()"
        )

        # special message for group_by
        self.assertErrorsWithMessage(
            lambda: obj.group_by(),
            AttributeError,
            "\'MyTestProviderFactory\' has no attribute \'group_by\'.\n"
            "To start building a query you need to make the provider table object. Try calling the atlas attribute and then chaining on .group_by(),\n"
            "for example:\n"
            "    t = atlas.my_test_provider()\n"
            "or\n"
            "    t = atlas[\"My.Test.Provider\"]()\n"
            "Then call .group_by() to start building your query\n"
            "    query = t.group_by(\"^\")\n"
            "and finally call .go() to run the query and get your dataframe back\n"
            "    df = query.go()"
        )

    def test_metafactory_data_provider_generated_call_method(self):
        meta = self.make_provider_meta('My.Test.Provider', n_params=4, n_tv_params=2)
        client = self.make_dummy_client()

        # Create class by instantiating metaclass
        cls = MetaFactory(meta, client)
        self.assertEqual('MyTestProviderFactory', cls.__name__)

        # Create object by instantiating class
        obj = cls()

        # Assert that the __call__ overload has the correct form and behaviour
        call_fn = obj.__call__
        # docstring
        self.assertLineByLineEqual(
            """Create a Table instance for the My.Test.Provider provider.

            Provider Description:
                No description available

            Provider Documentation:
                No documentation link available

            Args: 
                  param0 (int): No description available
                  param1 (int): No description available
                  param2 (float): No description available
                  param3 (float): No description available
                  table_var_0 (Table): No description available
                  table_var_1 (Table): No description available

            Returns:
                Table: the Table instance for querying My.Test.Provider with the given parameter values.
            """,
            call_fn.__doc__
        )

        # signature
        sig = signature(call_fn)

        # Return type annotation
        self.assertEqual(Table, sig.return_annotation)

        # Signature param names
        obs_names = list(sig.parameters.keys())
        exp_names = [p.python_name() for p in meta.parameters + meta.table_parameters]
        self.assertSequenceEqual(exp_names, obs_names)

        values = sig.parameters.values()
        # signature param kinds
        self.assertTrue(all(p.kind == p.POSITIONAL_OR_KEYWORD for p in values))
        # signature param type annotations
        exp_types = [DType.to_pytype(p.dtype) for p in meta.parameters] + [Table] * len(meta.table_parameters)
        obs_types = [p.annotation for p in values]
        self.assertSequenceEqual(exp_types, obs_types)

        # creates the correct table with correct param values
        tv0 = self.make_table_var('A')
        tv1 = self.make_table_var('B')
        table1 = obj(param0=400, param1=100, param2=300, param3=22, table_var_0=tv0, table_var_1=tv1)
        self.assertIsInstance(table1, Table)
        meta = meta.update(columns=table1.meta_.columns)
        self.assertHashEqual(table1.meta_, meta)

        # Assert that the params are set properly
        sql = table1.select('*').get_sql()
        self.assertSqlEqual(
            """
            @test_A = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.A]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------
            @test_B = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.B]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [My.Test.Provider]
            WHERE
               [Param0] = 400
               and [Param1] = 100
               and [Param2] = 300
               and [Param3] = 22
               and [TableVar_0] = @test_A
               and [TableVar_1] = @test_B            
            """,
            sql
        )

    def test_metafactory_data_provider_generated_call_method_positional_args(self):
        meta = self.make_provider_meta(n_params=4, n_tv_params=2)

        client = self.make_dummy_client()

        # Create class by instantiating metaclass
        cls = MetaFactory(meta, client)
        # Create object by instantiation class
        my_table = cls()

        tva, tvb = self.make_table_var('a'), self.make_table_var('b')

        table = my_table(1, 1, 1.2, 3.5, tva, tvb)
        sql = table.select('*').get_sql()
        self.assertSqlEqual(
            """
            @test_a = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.a]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------
            @test_b = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.b]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [My.Table]
            WHERE
               [Param0] = 1
               and [Param1] = 1
               and [Param2] = 1.2
               and [Param3] = 3.5
               and [TableVar_0] = @test_a
               and [TableVar_1] = @test_b            
            """,
            sql
        )

    def test_metafactory_data_provider_generated_call_method_kwarg_validation(self):
        meta = self.make_provider_meta(n_params=4, n_tv_params=2)
        client = self.make_dummy_client()

        # Create class by instantiating metaclass
        cls = MetaFactory(meta, client)
        # Create object by instantiation class
        my_table = cls()
        # errors on bad kwarg name with helpful message
        self.assertErrorsWithMessage(
            lambda: my_table(not_real='abc', also_bad=3),
            ValueError,
            "Invalid keyword args given to .my_table() ('not_real', 'also_bad') at\n"
            "   → lambda: my_table(not_real='abc', also_bad=3),\n"
            "Valid keyword args for .my_table() are:\n"
            "    param0         (int)\n"
            "    param1         (int)\n"
            "    param2         (float)\n"
            "    param3         (float)\n"
            "    table_var_0    (Table)\n"
            "    table_var_1    (Table)"
        )

    def test_metafactory_data_provider_generated_call_method_type_validation(self):
        meta = self.make_provider_meta(name='My.Data.Provider', n_params=4, n_tv_params=2)
        client = self.make_dummy_client()

        # Create class by instantiating metaclass
        cls = MetaFactory(meta, client)
        # Create object by instantiation class
        my_data_provider = cls()
        self.assertErrorsWithMessage(
            lambda: my_data_provider('123', table_var_0=7),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: my_data_provider('123', table_var_0=7),\n"
            "There were 2 failed constraints on .my_data_provider():\n"
            "   • The input to 'param0' must be Int/BigInt but was Text='123'\n"
            "   • The input to 'table_var_0' must be Table object but was a Column"
        )

    def test_metafactory_data_provider_generated_call_method_missing_args(self):
        meta = self.make_provider_meta(name='My.Data.Provider', n_params=4, n_tv_params=2)
        client = self.make_dummy_client()

        # Create class by instantiating metaclass
        cls = MetaFactory(meta, client)
        # Create object by instantiation class
        my_data_provider = cls()
        tv0 = self.make_table_var('tv0')
        table = my_data_provider(123, param2=0.123, table_var_0=tv0)

        sql = table.select('*').get_sql()
        self.assertSqlEqual(
            """
            @test_tv0 = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.tv0]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [My.Data.Provider]
            WHERE
               [Param0] = 123
               and [Param2] = 0.123
               and [TableVar_0] = @test_tv0            
            """,
            sql
        )

    def test_metafactory_direct_provider_generated_call_method_with_body_param(self):
        meta = self.make_provider_meta('Direct.Provider.Body', n_cols=5, n_params=8, n_tv_params=2,
                                       type='DirectProvider')
        params = list(meta.parameters)
        params[5] = params[5].update(is_body=True)
        meta = meta.update_fields(columns=None, parameters=tuple(params))

        client = self.make_dummy_client()
        cls = MetaFactory(meta, client)
        self.assertEqual('DirectProviderBodyFactory', cls.__name__)

        factory = cls()

        tv1, tv2 = self.make_table_var('one'), self.make_table_var('two')
        table = factory(
            tv1, tv2,
            param0=3,
            param1=123,
            param2=0.123,
            param3=1.234,
            param4=False,
            param5="""
            Testing multi line string
            ...
            """,
            param6=date(2022, 1, 1),
            param7=datetime(2023, 2, 2),
            apply_limit=1000
        )

        sql = table.select('*').get_sql()
        self.assertSqlEqual(
            """
            @test_one = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.one]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------
            @test_two = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.two]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------
            @direct_provider_body_1 = use Direct.Provider.Body with @test_one, @test_two limit 1000
                  --Param0=3
                  --Param1=123
                  --Param2=0.123
                  --Param3=1.234
                  --Param4=False
                  --Param6=2022-01-01T00:00:00
                  --Param7=2023-02-02T00:00:00
                  ----
                  
                              Testing multi line string
                              ...
                              
               enduse;
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               @direct_provider_body_1
            """,
            sql
        )

    def test_metafactory_direct_provider_generated_call_method_without_body_param(self):
        meta = self.make_provider_meta('Direct.Provider.NoBody', n_cols=5, n_params=8, n_tv_params=2,
                                       type='DirectProvider')
        meta = meta.update_fields(columns=None)

        client = self.make_dummy_client()
        cls = MetaFactory(meta, client)
        self.assertEqual('DirectProviderNoBodyFactory', cls.__name__)

        factory = cls()

        tv1, tv2 = self.make_table_var('one'), self.make_table_var('two')
        table = factory(
            tv1, tv2,
            param0=3,
            param1=123,
            param2=0.123,
            param3=1.234,
            param4=False,
            param5="""
            Testing multi line string
            ...
            """,
            param6=date(2022, 1, 1),
            param7=datetime(2023, 2, 2),
            apply_limit=1000
        )

        sql = table.select('*').get_sql()
        self.assertSqlEqual(
            """
            @test_one = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.one]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------
            @test_two = SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               [my.table.two]
            WHERE
               [Param0] = 123
               and [Param1] = 1727364939238612
               and [Param2] = 3.14;
            ------------------------------------------------------------------------------------------------
            @direct_provider_nobody_1 = use Direct.Provider.NoBody with @test_one, @test_two limit 1000
                  --Param0=3
                  --Param1=123
                  --Param2=0.123
                  --Param3=1.234
                  --Param4=False
                  --Param5=
                              Testing multi line string
                              ...

                  --Param6=2022-01-01T00:00:00
                  --Param7=2023-02-02T00:00:00
               enduse;
            ------------------------------------------------------------------------------------------------

            SELECT
               [Col0], [Col1], [Col2], [Col3], [Col4], [Col5], [Col6], [Col7], [Col8], [Col9]
            FROM
               @direct_provider_nobody_1
            """,
            sql
        )

    def test_metafactory_direct_provider_generated_call_method_name_validation(self):
        meta = self.make_provider_meta('My.Direct.Provider', n_cols=5, n_params=8, n_tv_params=2, type='DirectProvider')
        meta = meta.update_fields(columns=None)

        client = self.make_dummy_client()
        cls = MetaFactory(meta, client)
        self.assertEqual('MyDirectProviderFactory', cls.__name__)

        my_direct_provider = cls()

        self.assertErrorsWithMessage(
            lambda: my_direct_provider(bad_name=3, another='abc'),
            ValueError,
            "Invalid keyword args given to .my_direct_provider() ('bad_name', 'another') at\n"
            "   → lambda: my_direct_provider(bad_name=3, another='abc'),\n"
            "Valid keyword args for .my_direct_provider() are:\n"
            "    param0         (int)\n"
            "    param1         (int)\n"
            "    param2         (float)\n"
            "    param3         (float)\n"
            "    param4         (bool)\n"
            "    param5         (str)\n"
            "    param6         (date)\n"
            "    param7         (datetime)\n"
            "    apply_limit    (int)"
        )

    def test_metafactory_direct_provider_generated_call_method_type_validation(self):
        meta = self.make_provider_meta('My.Direct.Provider', n_cols=5, n_params=8, n_tv_params=2,
                                       type='DirectProvider')
        meta = meta.update_fields(columns=None)

        client = self.make_dummy_client()
        cls = MetaFactory(meta, client)
        self.assertEqual('MyDirectProviderFactory', cls.__name__)

        my_direct_provider = cls()
#        my_direct_provider(self.make_table(), self.make_table().select('*'), 2, param0='abc')
        self.assertErrorsWithMessage(
            lambda: my_direct_provider(self.make_table(), self.make_table().select('*'), 2, param0='abc'),
            TypeError,
            "Invalid inputs detected at\n"
            "   → lambda: my_direct_provider(self.make_table(), self.make_table().select('*'), 2, param0='abc'),\n"
            "There were 4 failed constraints on .my_direct_provider():\n"
            "   • Input to *args[0] must be a table var, but was a DataProvider table. Table vars can be constructed from queries with .to_table_var().\n "
            "   • Input to *args[1] must be a table var, but was a select op. Did you need to call .to_table_var()?.\n"
            "   • Input to *args[2] must be a table var, but was int.\n"
            "   • The input to 'param0' must be Int/BigInt but was Text='abc'"
        )
