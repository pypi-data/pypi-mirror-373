from mongodb_controller import COLLECTION_2206
from .menu2206_pipelines import create_pipeline_menu2206_by_fund

def fetch_data_menu2206_by_fund(fund_code, date_ref=None, keys_to_project=None):
    collection = COLLECTION_2206
    dates_in_db = sorted(collection.distinct('일자'))
    date_ref = date_ref or dates_in_db[-1]
    pipeline = create_pipeline_menu2206_by_fund(fund_code=fund_code, date_ref=date_ref, keys_to_project=keys_to_project)
    cursor = collection.aggregate(pipeline)
    data = list(cursor)
    return data

def fetch_data_menu2206_snapshot(date_ref=None):
    dates_in_db = sorted(COLLECTION_2206.distinct('일자'))
    date_ref = date_ref if date_ref else dates_in_db[-1]
    pipeline = [
        {'$match': {'일자': date_ref}},
        {'$project': {'_id': 0}}
    ]
    cursor = COLLECTION_2206.aggregate(pipeline)
    data = list(cursor)
    return data
