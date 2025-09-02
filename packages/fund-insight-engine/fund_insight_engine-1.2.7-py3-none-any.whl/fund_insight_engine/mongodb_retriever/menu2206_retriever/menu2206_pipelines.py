
def create_pipeline_menu2206_by_fund(fund_code, date_ref=None, keys_to_project=None):
    dct_project = {'_id': 0}
    if keys_to_project:
        for key in keys_to_project:
            dct_project[key] = 1
    pipeline = [
        {'$match': {'일자': date_ref, '펀드코드': fund_code}},
        {'$project': dct_project}
    ]   
    return pipeline