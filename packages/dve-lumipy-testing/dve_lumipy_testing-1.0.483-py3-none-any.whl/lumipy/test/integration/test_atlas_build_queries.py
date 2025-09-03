import pandas as pd

from lumipy.test.test_infra import BaseIntTest
from lumipy.lumiflex._atlas.query import atlas_queries


class AtlasBuildQueryTests(BaseIntTest):

    def test_atlas_queries_function(self):

        data, direct = atlas_queries(self.client)

        self.assertIsInstance(data, pd.DataFrame)
        exp = [
            'Description', 'Category', 'DocumentationLink', 'FieldName', 'DataType', 'FieldType', 'IsMain',
            'IsPrimaryKey', 'ParamDefaultValue', 'TableParamColumns', 'Description_fld', 'TableName', 'Type',
            'AllowedValues', 'ConditionUsage', 'SampleValues', 'ProvAttributes', 'NamespaceLevel'
           ]
        obs = data.columns.tolist()
        self.assertSequenceEqual(exp, obs)
        self.assertGreater(data.shape[0], 0)

        self.assertIsInstance(direct, pd.DataFrame)
        exp = [
            'Description',
            'DocumentationLink',
            'Type',
            'Category',
            'TableName',
            'CustomSyntax',
            'ProvAttributes',
            'NamespaceLevel',
            'ParamTable',
            'SyntaxDescr',
            'BodyStrNames'
           ]
        obs = direct.columns.tolist()
        self.assertSequenceEqual(exp, obs)
        self.assertGreater(data.shape[0], 0)
