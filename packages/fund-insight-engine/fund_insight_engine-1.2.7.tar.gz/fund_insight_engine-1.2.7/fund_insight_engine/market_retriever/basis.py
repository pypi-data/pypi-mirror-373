from functools import partial
from canonical_transformer import map_data_to_df
from universal_timeseries_transformer import extend_timeseries_by_all_dates
from .menu1100_basis import fetch_data_menu1100
from .consts import MAPPING_TICKER_BBG_INDEX, INVERSE_MAPPING_TICKER_BBG_INDEX, TICKER_COLLECTION_ASIA_INDEX

def rename_columns(df):
    cols = df.columns
    df.columns = [INVERSE_MAPPING_TICKER_BBG_INDEX.get(col) for col in cols]
    df.index.name = 'date'
    return df
        
def get_menu1100_indices(ticker_collection, start_date=None, end_date=None):
    data = fetch_data_menu1100(
        ticker_collection=ticker_collection,
        start_date=start_date,
        end_date=end_date
    )
    df = map_data_to_df(data)
    df = (
        df
        .copy()
        .set_index('일자')
        .pipe(extend_timeseries_by_all_dates)
        .pipe(rename_columns)
    )
    return df   

def get_menu1100_index(ticker_collection, ticker_bbg_index, start_date=None, end_date=None):
    ticker_pseudo = MAPPING_TICKER_BBG_INDEX.get(ticker_bbg_index)
    data = fetch_data_menu1100(
        ticker_collection=ticker_collection,
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
        .pipe(rename_columns)
    )
    return df 