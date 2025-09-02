from mongodb_controller import COLLECTION_8186
from fund_insight_engine.mongodb_retriever.general_utils import get_latest_date_in_collection
from .menu8186_pipelines import create_pipeline_menu8186_by_fund, create_pipeline_menu8186_snapshot

def fetch_data_menu8186_by_fund(fund_code, start_date=None, end_date=None, keys_to_project=None):
    dates_in_db = sorted(COLLECTION_8186.distinct('일자'))
    start_date = start_date or dates_in_db[0]
    end_date = end_date or dates_in_db[-1]
    pipeline = create_pipeline_menu8186_by_fund(fund_code=fund_code, start_date=start_date, end_date=end_date, keys_to_project=keys_to_project)
    cursor = COLLECTION_8186.aggregate(pipeline)
    data = list(cursor)
    return data

def fetch_data_menu8186_snapshot(date_ref=None, keys_to_project=None):
    date_ref = date_ref or get_latest_date_in_collection(COLLECTION_8186, '일자')
    pipeline = create_pipeline_menu8186_snapshot(date_ref=date_ref, keys_to_project=keys_to_project)
    cursor = COLLECTION_8186.aggregate(pipeline)
    data = list(cursor)
    return data
