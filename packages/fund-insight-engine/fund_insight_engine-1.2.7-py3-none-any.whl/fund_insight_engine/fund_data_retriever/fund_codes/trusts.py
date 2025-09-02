from canonical_transformer.morphisms import map_data_to_json
from fund_insight_engine.path_director import FILE_FOLDER
from string_date_controller import get_today
from fund_insight_engine.fund_data_retriever.fund_dates.latest import get_latest_date_ref_in_2110
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_utils import get_df_menu2110

def get_df_funds_trust(date_ref=None):
    df = get_df_menu2110(date_ref)
    df = df[df['펀드구분']=='투자신탁']
    return df

def get_df_funds_discretionary(date_ref=None):
    df = get_df_menu2110(date_ref)
    df = df[df['펀드구분']=='투자일임']
    return df

def get_fund_codes_trust(date_ref=None):
    df = get_df_funds_trust(date_ref)
    return list(df['펀드코드'])

def get_fund_codes_discretionary(date_ref=None):
    df = get_df_menu2110(date_ref)
    df = df[df['펀드구분']=='투자일임']
    return list(df['펀드코드'])


def get_fund_trust_categories_by_date(date_ref=None):
    df = get_df_menu2110(date_ref=date_ref)
    return sorted(list(df['펀드구분'].unique()))

def get_fund_codes_aum_by_trust(trust_name: list[str], date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    condition = ((df['펀드구분'].isin([trust_name])) & (df['클래스구분'].isin(['일반', '클래스펀드'])))
    try:
        lst = df[condition]['펀드코드'].tolist()
    except:
        lst = []
    return lst

def get_data_fund_codes_aum_by_trust(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    trust_names =get_fund_trust_categories_by_date(date_ref=date_ref)
    dct = {}
    for trust_name in trust_names:
        fund_codes =get_fund_codes_aum_by_trust(trust_name=trust_name, date_ref=date_ref)
        dct[trust_name] = fund_codes
    data = {'date_ref': date_ref, 'data': dct}
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_by_trust-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data

def get_fund_codes_by_trust(trust_name: list[str], date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    condition = (df['펀드구분'].isin([trust_name]))
    try:
        lst = df[condition]['펀드코드'].tolist()
    except:
        lst = []
    return lst

def get_data_fund_codes_by_trust(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    trust_names =get_fund_trust_categories_by_date(date_ref=date_ref)
    dct = {}
    for trust_name in trust_names:
        fund_codes =get_fund_codes_by_trust(trust_name=trust_name, date_ref=date_ref)
        dct[trust_name] = fund_codes
    data = {'date_ref': date_ref, 'data': dct}
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_by_trust-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data

def get_fund_codes_main_by_trust(trust_name: list[str], date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    condition = (df['펀드구분'].isin([trust_name])) & (df['클래스구분'].isin(['운용펀드', '-']))
    try:
        lst = df[condition]['펀드코드'].tolist()
    except:
        lst = []
    return lst

def get_data_fund_codes_main_by_trust(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    trust_names =get_fund_trust_categories_by_date(date_ref=date_ref)
    dct = {}
    for trust_name in trust_names:
        fund_codes =get_fund_codes_main_by_trust(trust_name=trust_name, date_ref=date_ref)
        dct[trust_name] = fund_codes
    data = {'date_ref': date_ref, 'data': dct}
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_by_trust-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data