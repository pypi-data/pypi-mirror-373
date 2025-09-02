from mongodb_controller.mongodb_collections import COLLECTION_8186
import pandas as pd
from string_date_controller import get_date_n_days_ago

def get_timeseries_fund_price(fund_code):
    pipeline = [
    {
        "$match": {
            "펀드코드": fund_code 
        }
    },
    {
        "$project": {
            "_id": 0,
            "date": "$일자",
            fund_code: "$수정기준가" 
        }
    },
    {
        "$sort": {"date": 1}  
    }
]
    cursor = COLLECTION_8186.aggregate(pipeline)
    data = list(cursor)
    df = pd.DataFrame(data)
    if len(df) == 0:
        return pd.DataFrame()
    df = df.set_index('date')
    return df

def get_corrected_timeseries_fund_price(fund_code):
    df = get_timeseries_fund_price(fund_code)
    dates = df.index 
    date_i = dates[0]
    corrected_date_i = get_date_n_days_ago(date_i, 1)
    df.loc[corrected_date_i, fund_code] = 1000.0
    df = df.sort_index()
    return df