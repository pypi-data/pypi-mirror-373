import pandas as pd
from mongodb_controller import COLLECTION_2205

# 2205: individual portfolio
def create_pipeline_for_latest_date_of_menu2205(fund_code):
    pipeline = [
        {'$match': {'fund_code': fund_code}},
        {'$sort': {'date_ref': -1}},
        {'$project': {'_id': 0, 'date_ref': 1}},
        {'$limit': 1}
    ]
    return pipeline

def get_latest_date_ref_of_menu2205_by_fund_code(fund_code):
    pipeline = create_pipeline_for_latest_date_of_menu2205(fund_code)
    cursor = COLLECTION_2205.aggregate(pipeline)
    return list(cursor)[0]['date_ref']

def create_pipeline_for_menu2205(fund_code, date_ref=None):
    pipeline = [
        {'$match': {'fund_code': fund_code, 'date_ref': date_ref}},
        {'$project': {'_id': 0, 'data': 1}}
    ]
    return pipeline

def fetch_data_menu2205(fund_code, date_ref=None, option_verbose=False):
    date_ref = date_ref if date_ref else get_latest_date_ref_of_menu2205_by_fund_code(fund_code)
    if option_verbose:
        print(f'(fund_code, date_ref): {fund_code, date_ref}')
    pipeline = create_pipeline_for_menu2205(fund_code, date_ref)
    cursor = COLLECTION_2205.aggregate(pipeline)
    return list(cursor)[0]['data']

def fetch_df_menu2205(fund_code, date_ref=None, option_verbose=False):
    data = fetch_data_menu2205(fund_code, date_ref, option_verbose=option_verbose)
    df = pd.DataFrame(data)
    return df