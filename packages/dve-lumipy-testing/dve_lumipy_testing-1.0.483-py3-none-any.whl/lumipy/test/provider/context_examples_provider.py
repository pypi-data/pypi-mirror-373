import os
from pathlib import Path

from pandas import DataFrame, read_csv, to_datetime

from lumipy.provider import PandasProvider, Context
from lumipy.provider.metadata import ParamMeta, DType


class ContextExamplesProvider(PandasProvider):

    def __init__(self, source, name, record_to):

        self.record_to = Path(record_to) / 'context_examples'
        self.record_to.mkdir(parents=True, exist_ok=True)

        super().__init__(source, name, 'test')
        self.parameters['TestCaseName'] = ParamMeta(
            'TestCaseName',
            DType.Text,
            "File name to save test case data against."
        )

    def get_data(self, context: Context) -> DataFrame:

        name = self.name.replace('.', '_') + f'_{context.get("TestCaseName")}.json'

        with open(self.record_to / name, 'w') as f:
            context.identity = None
            f.write(context.json(indent=2))

        return context.pandas.apply(self.df, False)


file_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = file_dir + '/../data/'

iris = ContextExamplesProvider(
    'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv',
    'iris',
    data_dir
)

mpg = ContextExamplesProvider(
    'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv',
    'mpg',
    data_dir
)

penguins = ContextExamplesProvider(
    'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv',
    'penguins',
    data_dir
)

planets = ContextExamplesProvider(
    'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/planets.csv',
    'planets',
    data_dir
)

taxis = ContextExamplesProvider(
    'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/taxis.csv',
    'taxis',
    data_dir
)

tips = ContextExamplesProvider(
    'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv',
    'tips',
    data_dir
)

titanic = ContextExamplesProvider(
    'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv',
    'titanic',
    data_dir
)

prices_df = read_csv(data_dir + 'prices.csv')
prices_df['Date'] = to_datetime(prices_df.Date).dt.tz_localize(tz='utc')
prices = ContextExamplesProvider(prices_df, 'prices', data_dir)
