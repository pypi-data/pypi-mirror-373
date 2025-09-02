from mongodb_controller import COLLECTION_8186
from string_date_controller import get_yesterday
from fund_insight_engine.fund_data_retriever.fund_dates.initial_and_final import get_date_f_by_fund, get_date_i_by_fund

def create_pipeline_point_menu8186(key, fund_code, date):
    return [
        {
            '$match': {
                '펀드코드': fund_code,
                '일자': date
            }
        },
        {
            '$project': {
                '_id': 0,
                key: 1
            }
        }
    ]

def get_point_menu8186(key, fund_code, date):
    pipeline = create_pipeline_point_menu8186(key, fund_code, date)
    cursor = COLLECTION_8186.aggregate(pipeline)
    data = list(cursor)
    return data[0][key]

def set_dates_for_points_by_kernel(kernel, fund_code: str, date_ref=None):
    date_ref = date_ref if date_ref else get_yesterday()
    date_latest = get_date_f_by_fund(fund_code)
    date_oldest = get_date_i_by_fund(fund_code)
    date_f = date_ref if date_ref else date_latest
    date_i = kernel(date_ref)
    if date_i < date_oldest:
        date_i = date_oldest
    return date_i, date_f

def get_two_points(key: str, fund_code: str, date_i, date_f):
    price_i = get_point_menu8186(key, fund_code, date_i)
    price_f = get_point_menu8186(key, fund_code, date_f)
    return price_i, price_f

def get_two_points_return(price_i, price_f):
    return (price_f / price_i - 1) * 100