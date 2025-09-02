from fund_insight_engine.mongodb_retriever.menu8186_retriever.menu8186_connector import collection_menu8186 as COLLECTION_8186
from fund_insight_engine.mongodb_retriever.menu8186_retriever.menu8186_date import get_latest_date_in_menu8186

def get_fund_price(fund_code, date_ref=None):
    date_ref = date_ref or get_latest_date_in_menu8186()
    pipeline_price = [
        {'$match': {'일자': date_ref, '펀드코드': fund_code}},
        {'$project': {'_id': 0, '수정기준가': 1}},
    ] 
    cursor = COLLECTION_8186.aggregate(pipeline_price)
    data_list = list(cursor)
    if not data_list:
        return {'수정기준가': None}
    return data_list[-1]

def get_fund_nav(fund_code, date_ref=None):
    date_ref = date_ref or get_latest_date_in_menu8186()
    pipeline_nav = [
        {'$match': {'일자': date_ref, '펀드코드': fund_code}},
        {'$project': {'_id': 0, '순자산': 1}},
    ]
    cursor = COLLECTION_8186.aggregate(pipeline_nav)
    data_list = list(cursor)
    if not data_list:
        return {'순자산': None}
    return data_list[-1]

def get_fund_capital(fund_code, date_ref=None):
    date_ref = date_ref or get_latest_date_in_menu8186()
    pipeline_capital = [
        {'$match': {'일자': date_ref, '펀드코드': fund_code}},
        {'$project': {'_id': 0, '설정액': 1}},
    ]
    cursor = COLLECTION_8186.aggregate(pipeline_capital)
    data = list(cursor)[-1]
    return data
    