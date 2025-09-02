from fund_insight_engine.fund_data_retriever.fund_codes import (
    get_fund_codes_generals,
    get_fund_codes_class
)
from mongodb_controller import COLLECTION_8186

def fetch_firm_aum():
    fund_codes_general = get_fund_codes_generals()
    fund_codes_class = get_fund_codes_class()

    pipeline = [
        {'$match': {'펀드코드': {'$in': fund_codes_general+fund_codes_class}}},
        {'$group': {
            '_id': '$일자',
            '순자산': {'$sum': '$순자산'}
        }},
        {'$project': {
            '_id': 0,
            '일자': '$_id',
            '순자산': 1
        }},
        {'$sort': {'일자': 1}}
    ]
    cursor = COLLECTION_8186.aggregate(pipeline)
    data = list(cursor)
    return data


def fetch_firm_aum_by_date(date_ref):
    fund_codes_general = get_fund_codes_generals(date_ref=date_ref)
    fund_codes_class = get_fund_codes_class(date_ref=date_ref)

    aggregation_pipeline = [
        {'$match': {'펀드코드': {'$in': fund_codes_general+fund_codes_class}, '일자': date_ref}},
        {'$group': {
            '_id': '$일자',
            '순자산': {'$sum': '$순자산'}
        }},
        {'$project': {
            '_id': 0,
            '일자': '$_id',
            '순자산': 1
        }},
        {'$sort': {'일자': 1}}
    ]

    cursor = COLLECTION_8186.aggregate(aggregation_pipeline)
    data = list(cursor)
    return data

def fetch_exact_firm_aum():
    dates_ref = COLLECTION_8186.distinct('일자')
    data = [fetch_firm_aum_by_date(date_ref)[0] for date_ref in dates_ref]
    data