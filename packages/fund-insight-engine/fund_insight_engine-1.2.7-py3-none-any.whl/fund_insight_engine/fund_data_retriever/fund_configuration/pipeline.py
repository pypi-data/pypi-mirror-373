def create_pipeline_for_fund_configuration(fund_code, date_ref):
    pipeline = [
        {'$match': {'fund_code': fund_code, 'date_ref': date_ref}},
        {'$project': {'_id': 0}}
    ]
    return pipeline

def create_pipeline_for_fund_numbers(fund_code, date_ref):
    pipeline = [
        {'$match': {'펀드코드': fund_code, '일자': date_ref}},
        {'$project': {'_id': 0}}
    ]
    return pipeline