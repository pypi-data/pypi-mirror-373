from canonical_transformer import get_mapping_of_column_pairs
from canonical_transformer.morphisms import map_data_to_json
from fund_insight_engine.path_director import FILE_FOLDER
from string_date_controller import get_today
from fund_insight_engine.fund_data_retriever.fund_dates.latest import get_latest_date_ref_in_2110
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_utils import get_df_menu2110
from fund_insight_engine.mongodb_retriever.menu2110_retriever.menu2110_consts import KEY_FOR_FUND_CODE_IN_MENU2110, KEY_FOR_FUND_NAME_IN_MENU2110
from .classes_consts import KEY_FOR_CLASS

KEYWORDS_TO_EXCLUDE = ['1종', '2종', '3종']

def get_df_funds_main(date_ref=None):
    df = get_df_menu2110(date_ref=date_ref)
    condition_main = (df[KEY_FOR_CLASS]!='클래스펀드') & (~df[KEY_FOR_FUND_NAME_IN_MENU2110].str.contains('|'.join(KEYWORDS_TO_EXCLUDE), na=False))
    df = df[condition_main]
    return df

def get_mapping_fund_names_main(date_ref=None):
    df = get_df_funds_main(date_ref=date_ref)
    return get_mapping_of_column_pairs(df, key_col=KEY_FOR_FUND_CODE_IN_MENU2110, value_col=KEY_FOR_FUND_NAME_IN_MENU2110)

def get_fund_codes_main(date_ref=None):
    return list(get_mapping_fund_names_main(date_ref=date_ref).keys())

def filter_fund_codes_by_main_filter(fund_codes, date_ref=None):
    fund_codes_main = get_fund_codes_main(date_ref=date_ref)
    fund_codes = list(set(fund_codes_main) & set(fund_codes))
    fund_codes_sorted = sorted(fund_codes)
    return fund_codes_sorted


def get_fund_codes_by_main_filter(keyword: str, date_ref: str=None):
    df = get_df_menu2110(date_ref=date_ref)
    condition_main = (df[KEY_FOR_CLASS]!='클래스펀드') & (~df[KEY_FOR_FUND_NAME_IN_MENU2110].str.contains('|'.join(KEYWORDS_TO_EXCLUDE), na=False))
    condition_sub = ~(condition_main)

    mapping_keyword = {
        'main': condition_main,
        'sub': condition_sub,
    }

    try:
        lst = df[mapping_keyword[keyword]]['펀드코드'].tolist()
    except:
        lst = []
    return lst


def get_data_fund_codes_by_main_filter(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    keywords = ['main', 'sub']
    dct = {}
    for keyword in keywords:
        fund_codes =get_fund_codes_by_main_filter(keyword=keyword, date_ref=date_ref)
        dct[keyword] = fund_codes
    data = {'date_ref': date_ref, 'data': dct}
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_by_main_filter-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data
