from pandas import DataFrame
from yfinance import Ticker

from lumipy.lumiflex import DType
from lumipy.provider.base_provider import BaseProvider
from lumipy.provider.context import Context
from lumipy.provider.metadata import ColumnMeta, ParamMeta


class YFinanceProvider(BaseProvider):
    """Provider that extracts historical price data from yahoo finance using the yfinance package.

    """

    def __init__(self):

        columns = [
            ColumnMeta('Ticker', DType.Text, 'The stock ticker'),
            ColumnMeta('Date', DType.DateTime, 'The date'),
            ColumnMeta('Open', DType.Double, 'Opening price'),
            ColumnMeta('High', DType.Double, 'High price'),
            ColumnMeta('Low', DType.Double, 'Log price'),
            ColumnMeta('Close', DType.Double, 'Closing price'),
            ColumnMeta('Volume', DType.Double, 'Daily volume'),
            ColumnMeta('Dividends', DType.Double, 'Dividend payment on the date.'),
            ColumnMeta('StockSplits', DType.Double, 'Stock split factor on the date'),
        ]
        params = [
            ParamMeta(
                'Tickers',
                DType.Text,
                'The ticker/tickers to get data for. To specify multiple tickers separate them by a "+"',
                is_required=True
            ),
            ParamMeta('Range', DType.Text, 'How far back to get data for.', 'max'),
        ]

        super().__init__(
            'YFinance.Data.PriceHistory',
            columns,
            params,
            description='Price data from Yahoo finance for a given ticker'
        )

    def get_data(self, context: Context) -> DataFrame:

        tickers = context.get('Tickers').strip('+').split('+')

        for i, ticker in enumerate(tickers):

            df = Ticker(ticker).history(period=context.get('Range')).reset_index()

            if df.shape[0] == 0:
                yield self.progress_line(f'Result for {ticker} was empty! It may not exist or has been delisted.')
                continue

            df.columns = [c.replace(' ', '') for c in df.columns]
            df['Ticker'] = ticker
            yield self.progress_line(f'Processed ticker ({i+1}/{len(tickers)}) [{ticker}]')

            yield context.pandas.apply(df, yield_mode=True)
