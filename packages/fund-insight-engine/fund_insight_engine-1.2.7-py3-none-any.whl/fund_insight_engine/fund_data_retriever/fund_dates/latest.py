from functools import partial
from mongodb_controller import (
    COLLECTION_CONFIGURATION, 
    COLLECTION_2110, 
    COLLECTION_2160, 
    COLLECTION_8186
)

def get_latest_date_ref_in_collection(collection, key_for_date):
    pipeline = [
        {
            '$sort': {key_for_date: -1}
        },
        {
            '$limit': 1
        },
    ]
    cursor = collection.aggregate(pipeline=pipeline)
    data = list(cursor)
    return data[0][key_for_date]

get_latest_date_ref_in_configuration = partial(get_latest_date_ref_in_collection, COLLECTION_CONFIGURATION, 'date_ref')
get_latest_date_ref_in_2110 = partial(get_latest_date_ref_in_collection, COLLECTION_2110, 'date_ref')
get_latest_date_ref_in_2160 = partial(get_latest_date_ref_in_collection, COLLECTION_2160, '일자')
get_latest_date_ref_in_8186 = partial(get_latest_date_ref_in_collection, COLLECTION_8186, '일자')
