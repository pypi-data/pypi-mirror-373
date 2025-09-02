from canonical_transformer import get_mapping_of_column_pairs
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_utils import get_df_menu2110
from .mapping_utils import exclude_keywords_from_mapping
from .mapping_consts import KEYWORDS_FOR_MAIN, MAPPING_DIVISION

def get_mapping_fund_names_by_division(key_for_division, date_ref=None):
    df = get_df_menu2110(date_ref=date_ref)
    managers = MAPPING_DIVISION[key_for_division]
    df = df[df['매니저'].isin(managers)]
    COLS_TO_KEEP = ['펀드코드', '펀드명']
    df = df[COLS_TO_KEEP]
    return get_mapping_of_column_pairs(df, key_col='펀드코드', value_col='펀드명')

def get_mapping_fund_names_division_01(date_ref=None, keywords_to_exclude=None, option_main=True):
    mapping_fund_names_division_01 = get_mapping_fund_names_by_division('division_01', date_ref=date_ref)
    if option_main:
        mapping_fund_names_division_01 = exclude_keywords_from_mapping(mapping_fund_names_division_01, KEYWORDS_FOR_MAIN)
    if keywords_to_exclude:
        mapping_fund_names_division_01 = exclude_keywords_from_mapping(mapping_fund_names_division_01, keywords_to_exclude)
    return mapping_fund_names_division_01

def get_mapping_fund_names_division_02(date_ref=None, keywords_to_exclude=None):
    mapping_fund_names_division_02 = get_mapping_fund_names_by_division('division_02', date_ref=date_ref)
    mapping_fund_names_division_02 = exclude_keywords_from_mapping(mapping_fund_names_division_02, KEYWORDS_FOR_MAIN)
    if keywords_to_exclude:
        mapping_fund_names_division_02 = exclude_keywords_from_mapping(mapping_fund_names_division_02, keywords_to_exclude)
    return mapping_fund_names_division_02
