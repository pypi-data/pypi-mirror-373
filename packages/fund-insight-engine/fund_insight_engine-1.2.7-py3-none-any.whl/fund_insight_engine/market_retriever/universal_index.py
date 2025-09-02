from .us_index import get_us_index, get_us_indices
from .korea_index import get_korea_index, get_korea_indices
from .global_currency import get_currency, get_currencies
from .consts import KOREA_BBG_TICKERS_INDEX, US_BBG_TICKERS_INDEX, GLOBAL_BBG_TICKERS_CURNCY
import pandas as pd


def get_index(ticker_bbg_index, start_date=None, end_date=None):
    if ticker_bbg_index in KOREA_BBG_TICKERS_INDEX:
        return get_korea_index(ticker_bbg_index, start_date, end_date)
    elif ticker_bbg_index in US_BBG_TICKERS_INDEX:
        return get_us_index(ticker_bbg_index, start_date, end_date)
    elif ticker_bbg_index in GLOBAL_BBG_TICKERS_CURNCY:
        return get_currency(ticker_bbg_index, start_date, end_date)
    else:
        raise ValueError(f"Invalid ticker_bbg_index: {ticker_bbg_index}")

get_timeseries_index = get_index
get_bm = get_index    

def get_indices(start_date=None, end_date=None):
    korea_indices = get_korea_indices(start_date, end_date)
    us_indices = get_us_indices(start_date, end_date)
    global_currencies = get_currencies(start_date, end_date)
    return pd.concat([korea_indices, us_indices, global_currencies], axis=1)

get_bms = get_indices
