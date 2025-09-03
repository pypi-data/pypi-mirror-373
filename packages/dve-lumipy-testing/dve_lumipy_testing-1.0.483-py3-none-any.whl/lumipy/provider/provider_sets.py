import lumipy.provider as lp
from lumipy.provider.common import available
from lumipy.provider.implementation.test_providers import (
    TestProvider, TestFilterProvider, TestTableParamProvider, IdentityContextTestProvider
)

base_path = 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master'


def demo_set():
    csvs = ['iris', 'mpg', 'penguins', 'planets', 'taxis', 'tips', 'titanic']
    return [lp.PandasProvider(f'{base_path}/{n}.csv', n, 'demo') for n in csvs]


def int_test():
    titanic = lp.PandasProvider(f'{base_path}/titanic.csv', 'titanic')
    return [titanic, TestProvider.variant1(), TestFilterProvider(), TestTableParamProvider(), IdentityContextTestProvider()]


def int_test_with_proxy():
    titanic = lp.PandasProvider(f'{base_path}/titanic.csv', 'titanicproxy')
    return [titanic, TestProvider.variant1('Test.PyProvider.Variant1proxy')]


def world_bank():
    return [lp.WorldBankDataSources(), lp.WorldBankEconomies(), lp.WorldBankSeriesMetadata(), lp.WorldBankSeriesData()]


def yfinance():
    return [lp.YFinanceProvider()]


def portfolio_opt():
    return [lp.YFinanceProvider(), lp.QuadraticProgram()]


provider_sets = {'int_test': int_test, 'int_test_with_proxy': int_test_with_proxy, 'demo': demo_set}

if available('yfinance'):
    provider_sets['yfinance'] = yfinance

if available('cvxopt', 'yfinance'):
    provider_sets['portfolio_opt'] = portfolio_opt

if available('wbgapi'):
    provider_sets['world_bank'] = world_bank
