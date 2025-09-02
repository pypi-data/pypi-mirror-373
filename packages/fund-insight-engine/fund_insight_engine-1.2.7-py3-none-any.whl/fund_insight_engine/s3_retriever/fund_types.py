from functools import partial
from typing import Dict, List, Optional, Callable
from financial_dataset_preprocessor import (
    get_preprocessed_funds_by_fund_type,
    filter_df_by_fund_codes_main
)
from .general_utils import get_fund_codes_from_df, get_mapping_fund_names_filtered_by_fund_codes

def get_fund_codes_by_fund_type(fund_type: str, date_ref: Optional[str] = None, option_main: bool = True) -> List[str]:
    df = get_preprocessed_funds_by_fund_type(fund_type=fund_type, date_ref=date_ref)
    if option_main:
        df = filter_df_by_fund_codes_main(df)
    return get_fund_codes_from_df(df)

def get_mapping_fund_names_by_fund_type(fund_type: str, date_ref: Optional[str] = None, option_main: bool = True) -> Dict[str, str]:
    fund_codes = get_fund_codes_by_fund_type(fund_type=fund_type, date_ref=date_ref, option_main=option_main)
    return get_mapping_fund_names_filtered_by_fund_codes(fund_codes=fund_codes, date_ref=date_ref)

MAPPING_FUND_TYPES = {
    'equity': '주식형',
    'equity_mixed': '주식혼합',
    'bond_mixed': '채권혼합',
    'multi_asset': '혼합자산', 
    'variable': '변액'
}

def create_fund_code_getter(fund_type_key: str) -> Callable[[Optional[str], bool], List[str]]:
    return partial(get_fund_codes_by_fund_type, fund_type=MAPPING_FUND_TYPES[fund_type_key])

def create_fund_name_mapping_getter(fund_type_key: str) -> Callable[[Optional[str], bool], Dict[str, str]]:
    return partial(get_mapping_fund_names_by_fund_type, fund_type=MAPPING_FUND_TYPES[fund_type_key])

get_fund_codes_equity_type = create_fund_code_getter('equity')
get_mapping_fund_names_equity_type = create_fund_name_mapping_getter('equity')

get_fund_codes_equity_mixed_type = create_fund_code_getter('equity_mixed')
get_mapping_fund_names_equity_mixed_type = create_fund_name_mapping_getter('equity_mixed')

get_fund_codes_bond_mixed_type = create_fund_code_getter('bond_mixed')
get_mapping_fund_names_bond_mixed_type = create_fund_name_mapping_getter('bond_mixed')

get_fund_codes_multi_asset_type = create_fund_code_getter('multi_asset')
get_mapping_fund_names_multi_asset_type = create_fund_name_mapping_getter('multi_asset')

get_fund_codes_variable_type = create_fund_code_getter('variable')
get_mapping_fund_names_variable_type = create_fund_name_mapping_getter('variable')


def get_mapping_by_fund_type(keyword_type: str, date_ref: Optional[str] = None, option_main: bool = True) -> Dict[str, str]:
    mapping = {
        '주식형': get_mapping_fund_names_equity_type,
        '주식혼합': get_mapping_fund_names_equity_mixed_type,
        '채권혼합': get_mapping_fund_names_bond_mixed_type,
        '혼합자산': get_mapping_fund_names_multi_asset_type,
        '변액': get_mapping_fund_names_variable_type
    }
    return mapping.get(keyword_type)(date_ref=date_ref, option_main=option_main)
