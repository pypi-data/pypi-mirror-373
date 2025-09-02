import pandas as pd
from .menu2206_fetcher import fetch_data_menu2206_by_fund, fetch_data_menu2206_snapshot

def get_df_menu2206_by_fund(fund_code, date_ref=None, keys_to_project=None):
    data = fetch_data_menu2206_by_fund(fund_code=fund_code, date_ref=date_ref, keys_to_project=keys_to_project)
    df = pd.DataFrame(data)
    return df

def get_df_menu2206_snapshot(date_ref=None):
    data = fetch_data_menu2206_snapshot(date_ref)
    df = pd.DataFrame(data)
    return df