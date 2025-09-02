from mongodb_controller.mongodb_collections import COLLECTION_RPA
from fund_insight_engine.mongodb_retriever.general_utils import fetch_data_for_snapshot_menu_by_date

def fetch_data_menu3412(date_ref=None):
    collection = COLLECTION_RPA['3412']
    return fetch_data_for_snapshot_menu_by_date(collection, date_ref=date_ref)
