from string_date_controller import get_today
from canonical_transformer import get_mapping_of_column_pairs
from canonical_transformer.morphisms import map_data_to_json
from mongodb_controller import COLLECTION_2110
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_consts import KEY_FOR_FUND_CODE_IN_MENU2110, KEY_FOR_FUND_NAME_IN_MENU2110
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_utils import get_df_menu2110
from fund_insight_engine.fund_data_retriever.fund_dates.latest import get_latest_date_ref_in_2110
from fund_insight_engine.fund_data_retriever.fund_dates import get_all_existent_dates_in_collection
from fund_insight_engine.path_director import FILE_FOLDER

from .types_consts import VALUES_FOR_TYPE, KEY_FOR_FUND_TYPE
from .main_fund_filter import filter_fund_codes_by_main_filter

def get_dfs_funds_by_type(date_ref=None):
    df = get_df_menu2110(date_ref=date_ref)
    dfs = dict(tuple(df.groupby(KEY_FOR_FUND_TYPE)))
    return dfs

def get_df_funds_by_type(key_for_type, date_ref=None):
    dfs = get_dfs_funds_by_type(date_ref=date_ref)
    COLS_TO_KEEP = [KEY_FOR_FUND_CODE_IN_MENU2110, KEY_FOR_FUND_NAME_IN_MENU2110, KEY_FOR_FUND_TYPE]
    df = dfs[key_for_type][COLS_TO_KEEP].set_index(KEY_FOR_FUND_CODE_IN_MENU2110)
    return df

    # VALUES_FOR_TYPE = ['주식혼합', '혼합자산', '채권혼합', '주식형', '변액']

def get_df_funds_equity_mixed(date_ref=None):
    return get_df_funds_by_type('주식혼합', date_ref=date_ref)

def get_df_funds_bond_mixed(date_ref=None):
    return get_df_funds_by_type('채권혼합', date_ref=date_ref)

def get_df_funds_multi_asset(date_ref=None):
    return get_df_funds_by_type('혼합자산', date_ref=date_ref)

def get_df_funds_equity(date_ref=None):
    return get_df_funds_by_type('주식형', date_ref=date_ref)

def get_df_funds_variable(date_ref=None):
    return get_df_funds_by_type('변액', date_ref=date_ref)

def get_mapping_fund_names_by_type(key_for_type, date_ref=None):
    df = get_df_funds_by_type(key_for_type, date_ref=date_ref)
    return get_mapping_of_column_pairs(df.reset_index(), key_col=KEY_FOR_FUND_CODE_IN_MENU2110, value_col=KEY_FOR_FUND_NAME_IN_MENU2110)

def get_mapping_fund_names_equity_mixed(date_ref=None):
    return get_mapping_fund_names_by_type('주식혼합', date_ref=date_ref)

def get_mapping_fund_names_bond_mixed(date_ref=None):
    return get_mapping_fund_names_by_type('채권혼합', date_ref=date_ref)

def get_mapping_fund_names_multi_asset(date_ref=None):
    return get_mapping_fund_names_by_type('혼합자산', date_ref=date_ref)

def get_mapping_fund_names_equity(date_ref=None):
    return get_mapping_fund_names_by_type('주식형', date_ref=date_ref)

def get_mapping_fund_names_variable(date_ref=None):
    return get_mapping_fund_names_by_type('변액', date_ref=date_ref)

def get_fund_codes_equity_mixed(date_ref=None):
    return list(get_mapping_fund_names_equity_mixed(date_ref=date_ref).keys())

def get_fund_codes_bond_mixed(date_ref=None):
    return list(get_mapping_fund_names_bond_mixed(date_ref=date_ref).keys())

def get_fund_codes_multi_asset(date_ref=None):
    return list(get_mapping_fund_names_multi_asset(date_ref=date_ref).keys())

def get_fund_codes_equity(date_ref=None):
    return list(get_mapping_fund_names_equity(date_ref=date_ref).keys())

def get_fund_codes_variable(date_ref=None):
    return list(get_mapping_fund_names_variable(date_ref=date_ref).keys())

def get_fund_codes_equity_mixed_main(date_ref=None):
    fund_codes_equity_mixed = get_fund_codes_equity_mixed(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_equity_mixed, date_ref=date_ref)
    return fund_codes

def get_fund_codes_bond_mixed_main(date_ref=None):
    fund_codes_bond_mixed = get_fund_codes_bond_mixed(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_bond_mixed, date_ref=date_ref)
    return fund_codes

def get_fund_codes_multi_asset_main(date_ref=None):
    fund_codes_multi_asset = get_fund_codes_multi_asset(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_multi_asset, date_ref=date_ref)
    return fund_codes

def get_fund_codes_equity_main(date_ref=None):
    fund_codes_equity = get_fund_codes_equity(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_equity, date_ref=date_ref)
    return fund_codes

def get_fund_codes_variable_main(date_ref=None):
    fund_codes_variable = get_fund_codes_variable(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_variable, date_ref=date_ref)
    return fund_codes

def get_all_fund_types():
    dates = get_all_existent_dates_in_collection(COLLECTION_2110, 'date_ref')
    sets = []
    for date in dates:
        lst = list(get_df_menu2110(date_ref=date)['펀드분류'].unique())
        sets = [*sets, *lst] 
    all_types = sorted(list(set(sets)))
    return all_types

def get_fund_types_by_date(date_ref=None):
    df = get_df_menu2110(date_ref=date_ref)
    return sorted(list(df['펀드분류'].unique()))

def get_fund_codes_aum_by_type(type_name: list[str], date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    condition = (df['펀드분류'].isin([type_name])) & (df['클래스구분'].isin(['일반', '클래스펀드']))
    try:
        lst = df[condition]['펀드코드'].tolist()
    except:
        lst = []
    return lst

def get_data_fund_codes_aum_by_type(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    type_names =get_fund_types_by_date(date_ref=date_ref)
    dct = {}
    for type_name in type_names:
        fund_codes =get_fund_codes_aum_by_type(type_name=type_name, date_ref=date_ref)
        dct[type_name] = fund_codes
    data = {'date_ref': date_ref, 'data': dct}
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_by_type-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data


def get_fund_codes_by_type(type_name: list[str], date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    condition = (df['펀드분류'].isin([type_name]))
    try:
        lst = df[condition]['펀드코드'].tolist()
    except:
        lst = []
    return lst

def get_data_fund_codes_by_type(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    type_names =get_fund_types_by_date(date_ref=date_ref)
    dct = {}
    for type_name in type_names:
        fund_codes =get_fund_codes_by_type(type_name=type_name, date_ref=date_ref)
        dct[type_name] = fund_codes
    data = {'date_ref': date_ref, 'data': dct}
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_by_type-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data


def get_fund_codes_main_by_type(type_name: list[str], date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    condition = (df['펀드분류'].isin([type_name])) & (df['클래스구분'].isin(['운용펀드', '-']))
    try:
        lst = df[condition]['펀드코드'].tolist()
    except:
        lst = []
    return lst

def get_data_fund_codes_main_by_type(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    type_names =get_fund_types_by_date(date_ref=date_ref)
    dct = {}
    for type_name in type_names:
        fund_codes =get_fund_codes_main_by_type(type_name=type_name, date_ref=date_ref)
        dct[type_name] = fund_codes
    data = {'date_ref': date_ref, 'data': dct}
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_by_type-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data
