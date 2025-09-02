from shining_pebbles import get_yesterday

def get_mapping_of_fund_conjugate(collection, conjugate, date_ref=None):
    date_ref = date_ref or get_yesterday()
    key, value = conjugate
    pipeline = [
        {'$match': {'일자': date_ref}},
        {'$project': {'_id': 0, key: 1, value: 1}}
    ]
    cursor = collection.aggregate(pipeline)
    data = list(cursor)
    mapping = {datum[key]: datum[value] for datum in data}
    return mapping
