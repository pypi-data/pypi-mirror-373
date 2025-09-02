from canonical_transformer import map_data_to_df
from universal_timeseries_transformer import extend_timeseries_by_all_dates
from .menu1100_basis import fetch_data_menu1100
from .consts import TICKER_COLLECTION_KOREA_BOND

def get_korea_bonds(start_date=None, end_date=None):
    data = fetch_data_menu1100(
        ticker_collection=TICKER_COLLECTION_KOREA_BOND,
        start_date=start_date,
        end_date=end_date
    )
    df = map_data_to_df(data)
    df = (
        df
        .copy()
        .set_index('일자')
        .pipe(extend_timeseries_by_all_dates)
    )
    return df    

def get_korea_bond(ticker_pseudo, start_date=None, end_date=None):
    data = fetch_data_menu1100(
        ticker_collection=TICKER_COLLECTION_KOREA_BOND,
        ticker_pseudo=ticker_pseudo,
        start_date=start_date,
        end_date=end_date
    )
    df = map_data_to_df(data)
    df = (
        df
        .copy()
        .set_index('일자')
        .pipe(extend_timeseries_by_all_dates)
    )
    return df

get_timeseries_korea_bond = get_korea_bond