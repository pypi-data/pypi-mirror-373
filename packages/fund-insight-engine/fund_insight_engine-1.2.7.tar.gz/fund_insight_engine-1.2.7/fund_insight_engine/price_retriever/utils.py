from functools import reduce
import re
from fund_insight_engine.market_retriever.consts import TICKERS_MARKET_INDEX, TICKERS_MARKET_CURRENCY, TICKERS_MARKET_BOND
from fund_insight_engine.bbg_retriever import COLLECTION_BBG_PRICE
from fund_insight_engine.fund_data_retriever.fund_price.price import get_corrected_timeseries_fund_price
from fund_insight_engine.market_retriever.universal_index import get_timeseries_index
from fund_insight_engine.market_retriever.global_currency import get_timeseries_currency
from fund_insight_engine.market_retriever.korea_bond import get_timeseries_korea_bond
from fund_insight_engine.bbg_retriever.bbg_price import get_timeseries_bbg_price


def determinate_ticker_type(ticker):
    if len(ticker) == 6 and re.match(r'^[A-Z0-9]{6}$', ticker):
        return 'fund'
    elif ticker in TICKERS_MARKET_INDEX:
        return 'index'
    elif ticker in TICKERS_MARKET_CURRENCY:
        return 'currency'
    elif ticker in TICKERS_MARKET_BOND:
        return 'bond'
    elif ticker in COLLECTION_BBG_PRICE.distinct('ticker_bbg'):
        return 'bbg'
    else:
        raise ValueError(f'Unknown ticker: {ticker}')

def select_price_kernel(ticker):
    mapping_kernel = {
        'fund': get_corrected_timeseries_fund_price,
        'index': get_timeseries_index,
        'currency': get_timeseries_currency,
        'bond': get_timeseries_korea_bond,
        'bbg': get_timeseries_bbg_price
    }
    return mapping_kernel[determinate_ticker_type(ticker)]

def get_timeseries_price(ticker):
    return select_price_kernel(ticker)(ticker)

def get_list_of_timeserieses_price(tickers):
    def get_timeseries_price_with_exception(ticker):
        try:
            return get_timeseries_price(ticker=ticker)
        except Exception as e:
            return None
    dfs = [get_timeseries_price_with_exception(ticker=ticker) for ticker in tickers]
    dfs = [df for df in dfs if df is not None]
    return dfs

def get_timeserieses_price(tickers, option_dropna=False):
    dfs = get_list_of_timeserieses_price(tickers)
    df = reduce(lambda left, right: left.join(right, how='left'), dfs)
    return df.dropna() if option_dropna else df