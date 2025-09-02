
def create_pipeline_for_latest_date(key_for_date):
    pipeline = [
        {'$sort': {key_for_date: -1}},
        {'$limit': 1},
        {'$project': {'_id': 0, key_for_date: 1}}
    ]
    return pipeline
