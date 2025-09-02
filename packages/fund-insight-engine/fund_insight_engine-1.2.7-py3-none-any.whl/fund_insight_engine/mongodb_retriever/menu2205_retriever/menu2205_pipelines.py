from typing import List, Dict, Any, Optional
from shining_pebbles import get_yesterday
from .menu2205_consts import DATE_REF_FIELD_NAME, FUND_CODE_FIELD_NAME, MONGODB_ID_FIELD_NAME, DATA_FIELD_NAME

def create_pipeline_for_preprocessed_menu2205(fund_code: str, date_ref: Optional[str] = None) -> List[Dict[str, Any]]:
    if not fund_code:
        raise ValueError("required: fund_code")
    date_ref = date_ref or get_yesterday()
    return [
        {'$match': {DATE_REF_FIELD_NAME: date_ref, FUND_CODE_FIELD_NAME: fund_code}},
        {'$project': {MONGODB_ID_FIELD_NAME: 0, DATA_FIELD_NAME: 1}}
    ]

def create_pipeline_for_preprocessed_menu2205_snapshot(date_ref: Optional[str] = None) -> List[Dict[str, Any]]:
    date_ref = date_ref or get_yesterday()
    return [
        {'$match': {DATE_REF_FIELD_NAME: date_ref}},
        {'$project': {MONGODB_ID_FIELD_NAME: 0, DATA_FIELD_NAME: 1}}
    ]