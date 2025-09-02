import pandas as pd
from .korea_index import get_korea_index, get_korea_indices
from .us_index import get_us_index, get_us_indices
from .global_currency import get_currencies
from .asia_index import get_asia_indices
from .etc1_index import get_etc1_indices
from .korea_bond import get_korea_bonds


def get_default_indices(start_date=None, end_date=None):
    korea_index = get_korea_indices(start_date=start_date, end_date=end_date)
    us_index = get_us_index(ticker_bbg_index='SPX Index', start_date=start_date, end_date=end_date)
    return korea_index.join(us_index, how='outer', on='date')

def get_compound_indices(start_date=None, end_date=None):
    korea_index = get_korea_indices(start_date=start_date, end_date=end_date)
    us_index = get_us_indices(start_date=start_date, end_date=end_date)
    global_currency = get_currencies(start_date=start_date, end_date=end_date)
    asia_index = get_asia_indices(start_date=start_date, end_date=end_date)
    etc1_index = get_etc1_indices(start_date=start_date, end_date=end_date)
    korea_bond = get_korea_bonds(start_date=start_date, end_date=end_date)
    return (
        korea_index
        .join(us_index, how='outer', on='date')
        .join(global_currency, how='outer', on='date')
        .join(asia_index, how='outer', on='date')
        .join(etc1_index, how='outer', on='date')
        .join(korea_bond, how='outer', on='date')
    )