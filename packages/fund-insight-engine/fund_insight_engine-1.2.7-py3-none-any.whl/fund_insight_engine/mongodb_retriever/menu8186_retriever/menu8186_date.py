from fund_insight_engine.mongodb_retriever.general_utils import get_latest_date_in_collection
from mongodb_controller import COLLECTION_8186

def get_latest_date_in_menu8186():
    return get_latest_date_in_collection(COLLECTION_8186, '일자')