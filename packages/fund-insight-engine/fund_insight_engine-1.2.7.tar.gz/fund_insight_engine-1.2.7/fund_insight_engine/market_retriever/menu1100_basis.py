from mongodb_controller import client

def get_collection(ticker_collection):
    return client['database-rpa'][f'dataset-menu1100-{ticker_collection}']

def get_date_range(collection):
    dates_in_db = sorted(collection.distinct('일자'))
    return dates_in_db[0], dates_in_db[-1]

def create_aggregation_pipeline(start_date, end_date, ticker_pseudo=None):
    project_stage = {'$project': {'_id': 0}} if not ticker_pseudo else {'$project': {'_id': 0, '일자': 1, ticker_pseudo: 1}}
    return [
        {'$match': {'일자': {'$gte': start_date, '$lte': end_date}}},
        {'$sort': {'일자': 1}},
        project_stage
    ]

def execute_aggregation(collection, pipeline):
    return list(collection.aggregate(pipeline))

def fetch_data_menu1100(ticker_collection, ticker_pseudo=None, start_date=None, end_date=None):
    collection = get_collection(ticker_collection)
    date_i, date_f = get_date_range(collection)
    start_date = start_date or date_i
    end_date = end_date or date_f
    pipeline = create_aggregation_pipeline(start_date, end_date, ticker_pseudo)
    return execute_aggregation(collection, pipeline)
