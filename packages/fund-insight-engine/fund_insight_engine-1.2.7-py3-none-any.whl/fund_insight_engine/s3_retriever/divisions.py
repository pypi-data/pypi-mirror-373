from typing import Dict, Optional
from functools import partial
from financial_dataset_preprocessor import get_preprocessed_menu8186_snapshot, filter_df_by_fund_codes_main
from .general_utils import get_mapping_fund_names_filtered_by_fund_codes
from .consts import LIFE_MANAGERS_OF_DIVISION_01, LIFE_MANAGERS_OF_DIVISION_02

def get_fund_codes_by_managers(managers, date_ref=None, option_main=True):
    df = get_preprocessed_menu8186_snapshot(date_ref=date_ref)
    managers_pattern = '|'.join(managers)    
    df = df[df['운용역'].str.contains(managers_pattern, na=False)]
    if option_main:
        df = filter_df_by_fund_codes_main(df)
    fund_codes = list(df.index)
    return fund_codes

get_fund_codes_of_division_01 = partial(get_fund_codes_by_managers, LIFE_MANAGERS_OF_DIVISION_01)
get_fund_codes_of_division_02 = partial(get_fund_codes_by_managers, LIFE_MANAGERS_OF_DIVISION_02)
get_mapping_fund_names_of_division_01 = partial(get_mapping_fund_names_filtered_by_fund_codes, fund_codes_kernel=get_fund_codes_of_division_01)
get_mapping_fund_names_of_division_02 = partial(get_mapping_fund_names_filtered_by_fund_codes, fund_codes_kernel=get_fund_codes_of_division_02)

def get_mapping_by_division(keyword_division: str, date_ref: Optional[str] = None, option_main: bool = True) -> Dict[str, str]:
    return {
        '운용1본부': get_mapping_fund_names_of_division_01,
        '운용2본부': get_mapping_fund_names_of_division_02
    }.get(keyword_division)(date_ref=date_ref, option_main=option_main)
