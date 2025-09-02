from canonical_transformer import map_data_to_df
from universal_timeseries_transformer import extend_timeseries_by_all_dates
from .menu1100_basis import fetch_data_menu1100
from .consts import MAPPING_TICKER_BBG_CURNCY, INVERSE_MAPPING_TICKER_BBG_CURNCY, TICKER_COLLECTION_GLOBAL_CURRENCY


def rename_columns(df):
    cols = df.columns
    df.columns = [INVERSE_MAPPING_TICKER_BBG_CURNCY.get(col) for col in cols]
    df.index.name = 'date'
    return df
        
def get_currencies(start_date=None, end_date=None):
    data = fetch_data_menu1100(
        ticker_collection=TICKER_COLLECTION_GLOBAL_CURRENCY,
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

def get_currency(ticker_bbg_curncy, start_date=None, end_date=None):
    ticker_pseudo = MAPPING_TICKER_BBG_CURNCY.get(ticker_bbg_curncy)
    data = fetch_data_menu1100(
        ticker_collection=TICKER_COLLECTION_GLOBAL_CURRENCY,
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

get_timeseries_currency = get_currency