from .menu2205_connector import collection_menu2205, collection_menu2205_snapshot
from .menu2205_pipelines import create_pipeline_for_preprocessed_menu2205, create_pipeline_for_preprocessed_menu2205_snapshot
from .menu2205_consts import DATA_FIELD_NAME
from typing import Dict, Any, Optional
import pandas as pd

def get_data_preprocessed_menu2205(fund_code: str, date_ref: Optional[str] = None) -> Dict[str, Any]:
    pipeline = create_pipeline_for_preprocessed_menu2205(fund_code=fund_code, date_ref=date_ref)
    cursor = collection_menu2205.aggregate(pipeline)
    data = list(cursor)[0][DATA_FIELD_NAME]
    return data

def get_data_preprocessed_menu2205_snapshot(date_ref: Optional[str] = None) -> Dict[str, Any]:
    pipeline = create_pipeline_for_preprocessed_menu2205_snapshot(date_ref=date_ref)
    cursor = collection_menu2205_snapshot.aggregate(pipeline)
    data = list(cursor)[0][DATA_FIELD_NAME]
    return data

def get_preprocessed_menu2205(fund_code: str, date_ref: Optional[str] = None) -> pd.DataFrame:
    data = get_data_preprocessed_menu2205(fund_code=fund_code, date_ref=date_ref)
    df = pd.DataFrame(data).set_index('일자')
    return df

def get_preprocessed_menu2205_snapshot(date_ref: Optional[str] = None) -> pd.DataFrame:
    data = get_data_preprocessed_menu2205_snapshot(date_ref=date_ref)
    df = pd.DataFrame(data).set_index('일자')
    return df