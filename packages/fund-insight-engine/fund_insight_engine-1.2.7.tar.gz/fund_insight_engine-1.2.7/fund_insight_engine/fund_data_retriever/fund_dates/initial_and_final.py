from functools import partial
from mongodb_controller import COLLECTION_8186

def get_date_boundary(fund_code, option_ascending):
    pipeline = [
        {'$match': {'펀드코드': fund_code}},
        {'$project': {'_id': 0, '일자': 1}},
        {'$sort': {'일자': option_ascending}},
        {'$limit': 1}
    ]
    cursor = COLLECTION_8186.aggregate(pipeline)
    data = list(cursor)
    date = data[0]['일자']
    return date

get_date_i_by_fund = partial(get_date_boundary, option_ascending=1)
get_date_f_by_fund = partial(get_date_boundary, option_ascending=-1)