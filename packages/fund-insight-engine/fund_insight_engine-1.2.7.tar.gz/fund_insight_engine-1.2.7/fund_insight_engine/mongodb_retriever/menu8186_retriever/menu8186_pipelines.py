from shining_pebbles import get_yesterday

def create_pipeline_menu8186_by_fund(fund_code, start_date, end_date, keys_to_project=None):
    dct_project = {'_id': 0}
    if keys_to_project:
        for key in keys_to_project:
            dct_project[key] = 1
    pipeline = [
        {'$match': {'일자': {'$gte': start_date, '$lte': end_date}, '펀드코드': fund_code}},
        {'$project': dct_project}
    ]   
    return pipeline

def create_pipeline_menu8186_snapshot(date_ref=None, keys_to_project=None):
    dct_project = {'_id': 0}
    if keys_to_project:
        for key in keys_to_project:
            dct_project[key] = 1
    pipeline = [
        {'$match': {'일자': date_ref}},
        {'$project': dct_project}
    ]   
    return pipeline

def create_pipeline_fund_codes_and_fund_names(date_ref=None):
    date_ref = date_ref or get_yesterday()
    return [
        {'$match': {'일자': date_ref}},
        {'$project': {'_id': 0, '펀드코드': 1, '펀드명': 1}}
    ]

def create_pipeline_fund_codes_and_inception_dates(date_ref=None):
    date_ref = date_ref or get_yesterday()
    return [
        {'$match': {'일자': date_ref}},
        {'$project': {'_id': 0, '펀드코드': 1, '설정일': 1}}
    ]

def create_pipeline_of_something(something,date_ref=None):
    date_ref = date_ref or get_yesterday()
    return [
        {'$match': {'일자': date_ref}},
        {'$project': {'_id': 0, '펀드코드': 1, something: 1}}
    ]
