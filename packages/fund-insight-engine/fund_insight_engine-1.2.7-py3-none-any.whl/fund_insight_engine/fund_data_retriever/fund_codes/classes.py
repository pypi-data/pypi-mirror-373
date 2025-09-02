from canonical_transformer.morphisms import map_data_to_json
from fund_insight_engine.path_director import FILE_FOLDER
from string_date_controller import get_today
from fund_insight_engine.fund_data_retriever.fund_dates.latest import get_latest_date_ref_in_2110
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_utils import get_df_menu2110
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_consts import KEY_FOR_FUND_CODE_IN_MENU2110
from .classes_consts import KEY_FOR_CLASS

def get_dfs_funds_by_class(date_ref=None):
    df = get_df_menu2110(date_ref=date_ref)
    df_code_class = df[[KEY_FOR_FUND_CODE_IN_MENU2110, KEY_FOR_CLASS]]
    dfs = dict(tuple(df_code_class.groupby(KEY_FOR_CLASS)))
    return dfs

def get_df_funds_by_class(key_for_class, date_ref=None):
    dfs = get_dfs_funds_by_class(date_ref=date_ref)
    df = dfs[key_for_class].set_index(KEY_FOR_FUND_CODE_IN_MENU2110)
    return df

def get_df_funds_mothers(date_ref=None):
    return get_df_funds_by_class('운용펀드', date_ref=date_ref)

def get_df_funds_generals(date_ref=None):
    return get_df_funds_by_class('일반', date_ref=date_ref)

def get_df_funds_class(date_ref=None):
    return get_df_funds_by_class('클래스펀드', date_ref=date_ref)

def get_df_funds_nonclassified(date_ref=None):
    return get_df_funds_by_class('-', date_ref=date_ref)

def get_fund_codes_by_class(key_for_class, date_ref=None):
    df = get_df_funds_by_class(key_for_class, date_ref=date_ref)
    return df.index.tolist()

def get_fund_codes_mothers(date_ref=None):
    return get_fund_codes_by_class('운용펀드', date_ref=date_ref)

def get_fund_codes_generals(date_ref=None):
    return get_fund_codes_by_class('일반', date_ref=date_ref)

def get_fund_codes_class(date_ref=None):
    return get_fund_codes_by_class('클래스펀드', date_ref=date_ref)

def get_fund_codes_nonclassified(date_ref=None):
    return get_fund_codes_by_class('-', date_ref=date_ref)

def get_fund_class_categories_by_date(date_ref=None):
    df = get_df_menu2110(date_ref=date_ref)
    return sorted(list(df['클래스구분'].unique()))

def get_fund_codes_by_class_category(category_name: str, date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    condition = (df['클래스구분']==category_name)
    try:
        lst = df[condition]['펀드코드'].tolist()
    except:
        lst = []
    return lst

def get_data_fund_codes_by_class_category(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    class_categories = get_fund_class_categories_by_date(date_ref=date_ref)
    dct = {}
    for class_category in class_categories:
        fund_codes =get_fund_codes_by_class_category(category_name=class_category, date_ref=date_ref)
        dct[class_category] = fund_codes
    data = {'date_ref': date_ref, 'data': dct}
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_by_class_category-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data