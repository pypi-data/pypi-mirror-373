from canonical_transformer import map_data_to_df
from .menu8186_fetcher import fetch_data_menu8186_by_fund, fetch_data_menu8186_snapshot

def get_df_menu8186_by_fund(fund_code, start_date=None, end_date=None, keys_to_project=None):
    data = fetch_data_menu8186_by_fund(fund_code=fund_code, start_date=start_date, end_date=end_date, keys_to_project=keys_to_project)
    df = map_data_to_df(data)
    return df

def get_df_menu8186_snapshot(date_ref=None, keys_to_project=None):
    data = fetch_data_menu8186_snapshot(date_ref=date_ref, keys_to_project=keys_to_project)
    df = map_data_to_df(data)
    return df