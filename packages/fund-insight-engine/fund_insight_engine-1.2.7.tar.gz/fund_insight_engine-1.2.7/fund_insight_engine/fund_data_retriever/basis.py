from functools import reduce
from typing import Callable
import pandas as pd
from mongodb_controller import COLLECTION_8186
from fund_insight_engine.fund_data_retriever.fund_dates import get_all_existent_dates_in_collection

def get_row_of_fund_data(key: str, fund_codes_kernel: Callable, date_ref: str):
    pipeline = [
        {'$match': {'일자': date_ref,'펀드코드': {'$in': fund_codes_kernel(date_ref=date_ref)}}},
        {'$project': {'_id': 0, '일자': 1, '펀드코드': 1, key: 1}},
    ]
    cursor = COLLECTION_8186.aggregate(pipeline)
    data = list(cursor)
    df = pd.DataFrame(data)
    row = df.pivot(index='일자', columns='펀드코드', values=key)
    return row

def get_all_rows_of_fund_data(key: str, fund_codes_kernel: Callable, dates: list[str]):
    return [get_row_of_fund_data(key, fund_codes_kernel, date) for date in dates]

def get_df_fund_data(key: str, fund_codes_kernel: Callable, dates: list[str] = None):
    dates = dates if dates else get_all_existent_dates_in_collection(COLLECTION_8186, '일자')
    rows = get_all_rows_of_fund_data(key, fund_codes_kernel, dates)
    df = reduce(lambda row_i, row_j: row_i.join(row_j, how='outer'), [row.T for row in rows]).T
    return df