from fund_insight_engine import *
from mongodb_controller import COLLECTION_CONFIGURATION, COLLECTION_2110, COLLECTION_8186

def get_inception_date(fund_code):    
    pipeline = [
        {
            '$match': {'펀드코드': fund_code}
        },
        {
            '$sort': {'일자': -1}
        },
        {
            '$limit': 1
        },
        {
            '$project': {'_id': 0, '설정일': 1}
        }
    ]
    cursor = COLLECTION_8186.aggregate(pipeline=pipeline)
    data = list(cursor)
    return data[0]['설정일']

