from functools import partial
from string_date_controller import get_today
from canonical_transformer.morphisms import map_data_to_json
from fund_insight_engine.path_director import FILE_FOLDER
from fund_insight_engine.fund_data_retriever.fund_dates.latest import get_latest_date_ref_in_2110
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_utils import get_df_menu2110
from fund_insight_engine.fund_data_retriever.fund_mappings.mappings_divisions import get_mapping_fund_names_by_division
from .main_fund_filter import filter_fund_codes_by_main_filter
from .aum_fund_filter import filter_fund_codes_by_aum_filter

def get_fund_codes_division_01(date_ref=None):
    return list(get_mapping_fund_names_by_division('division_01', date_ref=date_ref).keys())

def get_fund_codes_division_02(date_ref=None):
    return list(get_mapping_fund_names_by_division('division_02', date_ref=date_ref).keys())

def get_fund_codes_division_01_main(date_ref=None):
    fund_codes_division_01 = get_fund_codes_division_01(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_division_01, date_ref=date_ref)
    return fund_codes

def get_fund_codes_division_02_main(date_ref=None):
    fund_codes_division_02 = get_fund_codes_division_02(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_main_filter(fund_codes_division_02, date_ref=date_ref)
    return fund_codes

def get_fund_codes_division_01_aum(date_ref=None):
    fund_codes_division_01 = get_fund_codes_division_01(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_aum_filter(fund_codes_division_01, date_ref=date_ref)
    return fund_codes

def get_fund_codes_division_02_aum(date_ref=None):
    fund_codes_division_02 = get_fund_codes_division_02(date_ref=date_ref)
    fund_codes = filter_fund_codes_by_aum_filter(fund_codes_division_02, date_ref=date_ref)
    return fund_codes

def get_fund_codes_by_division(manager_names: list[str], date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    condition = (df['매니저'].isin(manager_names))
    return df[condition]['펀드코드'].tolist()

# def get_fund_codes_aum_by_division(manager_names: list[str], date_ref: str=None):
#     df = get_df_menu2110(date_ref=date_ref)
#     condition = (df['매니저'].isin(manager_names)) & (df['클래스구분'].isin(['일반', '클래스펀드']))
#     return df[condition]['펀드코드'].tolist()

# get_fund_codes_aum_division_01 = partial(get_fund_codes_aum_by_division, manager_names=['강대권', '이대상'])
# get_fund_codes_aum_division_02 = partial(get_fund_codes_aum_by_division, manager_names=['남두우', '이시우'])


def get_fund_codes_by_division(division_name: str, date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    MANAGER_NAMES_DIVISION_02 = ['남두우', '이시우']

    condition_division_01 = (~df['매니저'].isin(MANAGER_NAMES_DIVISION_02)) 
    condition_division_02 = (df['매니저'].isin(MANAGER_NAMES_DIVISION_02))

    mapping_division = {
        '운용1본부': condition_division_01,
        '운용2본부': condition_division_02,
    }

    try:
        lst = df[mapping_division[division_name]]['펀드코드'].tolist()
    except:
        lst = []
    return lst


def get_data_fund_codes_by_division(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    division_names = ['운용1본부', '운용2본부']
    dct = {}
    for division_name in division_names:
        fund_codes =get_fund_codes_by_division(division_name=division_name, date_ref=date_ref)
        dct[division_name] = fund_codes
    data = {'date_ref': date_ref, 'data': dct}
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_by_division-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data


def get_fund_codes_aum_by_division(division_name: str, date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    MANAGER_NAMES_DIVISION_02 = ['남두우', '이시우']

    condition_division_01 = (~df['매니저'].isin(MANAGER_NAMES_DIVISION_02)) & (df['클래스구분'].isin(['일반', '클래스펀드']))
    condition_division_02 = (df['매니저'].isin(MANAGER_NAMES_DIVISION_02)) & (df['클래스구분'].isin(['일반', '클래스펀드']))

    mapping_division = {
        '운용1본부': condition_division_01,
        '운용2본부': condition_division_02,
    }

    try:
        lst = df[mapping_division[division_name]]['펀드코드'].tolist()
    except:
        lst = []
    return lst


def get_data_fund_codes_aum_by_division(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    division_names = ['운용1본부', '운용2본부']
    dct = {}
    for division_name in division_names:
        fund_codes =get_fund_codes_aum_by_division(division_name=division_name, date_ref=date_ref)
        dct[division_name] = fund_codes
    data = {'date_ref': date_ref, 'data': dct}
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_by_division-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data



def get_fund_codes_main_by_division(division_name: str, date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    MANAGER_NAMES_DIVISION_02 = ['남두우', '이시우']

    condition_division_01 = (~df['매니저'].isin(MANAGER_NAMES_DIVISION_02)) & (df['클래스구분'].isin(['운용펀드', '-']))
    condition_division_02 = (df['매니저'].isin(MANAGER_NAMES_DIVISION_02)) & (df['클래스구분'].isin(['운용펀드', '-']))

    mapping_division = {
        '운용1본부': condition_division_01,
        '운용2본부': condition_division_02,
    }

    try:
        lst = df[mapping_division[division_name]]['펀드코드'].tolist()
    except:
        lst = []
    return lst

def get_data_fund_codes_main_by_division(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    division_names = ['운용1본부', '운용2본부']
    dct = {}
    for division_name in division_names:
        fund_codes =get_fund_codes_aum_by_division(division_name=division_name, date_ref=date_ref)
        dct[division_name] = fund_codes
    data = {'date_ref': date_ref, 'data': dct}
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_by_division-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data

