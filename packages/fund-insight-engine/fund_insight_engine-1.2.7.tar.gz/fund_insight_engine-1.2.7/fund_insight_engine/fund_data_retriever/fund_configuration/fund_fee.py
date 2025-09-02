import pandas as pd
from .fund_info import fetch_data_fund_configuration

def fetch_data_fund_fee(fund_code, date_ref=None):
    configuration = fetch_data_fund_configuration(fund_code, date_ref)
    return configuration['data']['fee']

def get_df_fund_fee(fund_code, date_ref=None):
    data = fetch_data_fund_fee(fund_code, date_ref)
    return (
        pd.DataFrame(data)
        .set_index('판매사코드')
        .T    
    )