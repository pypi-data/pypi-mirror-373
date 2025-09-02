import pandas as pd
from mongodb_controller.mongodb_collections import COLLECTION_8186
from universal_timeseries_transformer import transform_timeseries

def slice_timeseries(df, start_date, end_date):
    if start_date is None and end_date is None:
        return df
    if start_date is None:
        return df[:end_date]
    if end_date is None:
        return df[start_date:]
    return df[start_date:end_date]

def create_pipeline_for_timeseries_manager(fund_code):
    pipeline = [
        {'$match': {'펀드코드': fund_code}},
        {'$project': {'_id': 0, '일자': 1, '수정기준가': 1, '순자산': 1, '설정액': 1, 'KOSPI지수': 1, 'KOSDAQ지수': 1, 'KOSPI200지수': 1,
                     '기준가격': 1, '과표기준가': 1, '해외비과세과표기준가': 1, '비거주자과표기준가': 1,
                     '주식비율': 1, '채권비율': 1, '주식순비율': 1, '채권순비율': 1, '지수선물순비율': 1, '설정좌수': 1}},
        {'$sort': {'일자': 1}},
    ]
    return pipeline

def get_data_timeseries_manager(fund_code):
    pipeline = create_pipeline_for_timeseries_manager(fund_code)
    cursor = COLLECTION_8186.aggregate(pipeline)
    data = list(cursor)
    return data

def get_df_timeseries_manager(fund_code):
    data = get_data_timeseries_manager(fund_code)
    df = pd.DataFrame(data)
    COLS_ORDERED = ['일자', '기준가격', '과표기준가', '수정기준가', '순자산', '설정액', '설정좌수', 'KOSPI지수', 'KOSDAQ지수', 'KOSPI200지수',
                    '주식비율', '채권비율', '주식순비율', '채권순비율', '지수선물순비율']
    df = df[COLS_ORDERED]
    df = df.set_index('일자')
    df = transform_timeseries(df, option_type='datetime')
    return df