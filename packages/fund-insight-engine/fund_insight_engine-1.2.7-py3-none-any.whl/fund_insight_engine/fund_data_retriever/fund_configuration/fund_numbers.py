import pandas as pd
from mongodb_controller import COLLECTION_8186
from .pipeline import create_pipeline_for_fund_numbers

def fetch_data_fund_numbers(fund_code, date_ref=None):
    if not date_ref:
        date_ref = sorted(COLLECTION_8186.distinct('일자', {'펀드코드': fund_code}), reverse=True)[0]
    pipeline = create_pipeline_for_fund_numbers(fund_code, date_ref)
    cursor = COLLECTION_8186.aggregate(pipeline=pipeline)
    data = list(cursor)[0]
    return data

def get_df_fund_numbers(fund_code, date_ref=None):
    data = fetch_data_fund_numbers(fund_code, date_ref)
    return (
        pd.DataFrame([data])
        .set_index('펀드코드')
        .T
    )
