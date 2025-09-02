from canonical_transformer import get_mapping_of_column_pairs
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_utils import get_df_menu2110

def get_mapping_fund_names_mongodb(date_ref=None):
    mapping_codes_and_names = get_mapping_of_column_pairs(get_df_menu2110(date_ref=date_ref), key_col='펀드코드', value_col='펀드명')
    return mapping_codes_and_names

def get_mapping_fund_inception_dates_mongodb(date_ref=None):
    mapping_codes_and_dates = get_mapping_of_column_pairs(get_df_menu2110(date_ref=date_ref), key_col='펀드코드', value_col='설정일')
    return mapping_codes_and_dates
