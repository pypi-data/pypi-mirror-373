from functools import partial
from typing import Callable
from string_date_controller import get_today
from shining_pebbles import scan_files_including_regex
from mongodb_controller import COLLECTION_2110
from canonical_transformer.morphisms import map_data_to_json, map_json_to_data
from fund_insight_engine.fund_data_retriever.fund_codes import (
    get_fund_codes_all,
    get_fund_codes_main, 
    get_fund_codes_division_01_main, 
    get_fund_codes_division_02_main, 
    get_fund_codes_equity_main, 
    get_fund_codes_equity_mixed_main, 
    get_fund_codes_bond_mixed_main, 
    get_fund_codes_multi_asset_main, 
    get_fund_codes_variable_main, 
    get_fund_codes_mothers, 
    get_fund_codes_class, 
    get_fund_codes_generals, 
    get_fund_codes_nonclassified, 
    get_fund_codes_aum,
)
from fund_insight_engine.fund_data_retriever.fund_dates import get_all_existent_dates_in_collection
from fund_insight_engine.path_director import FILE_FOLDER

def get_historical_fund_codes(fund_codes_kernel: Callable):
    dates = get_all_existent_dates_in_collection(COLLECTION_2110, 'date_ref')
    sets = []
    for date in dates:
        try:
            set_fund_codes = set(fund_codes_kernel(date_ref=date))
            sets = [*sets, *set_fund_codes]
        except Exception as e:
            print(date, e)
    sets = set(sets)
    return sorted(list(sets))

get_historical_fund_codes_all = partial(get_historical_fund_codes, get_fund_codes_all)
get_historical_fund_codes_total = get_historical_fund_codes_all
get_historical_fund_codes_main = partial(get_historical_fund_codes, get_fund_codes_main)
get_historical_fund_codes_division_01 = partial(get_historical_fund_codes, get_fund_codes_division_01_main)
get_historical_fund_codes_division_02 = partial(get_historical_fund_codes, get_fund_codes_division_02_main)
get_historical_fund_codes_equity = partial(get_historical_fund_codes, get_fund_codes_equity_main)
get_historical_fund_codes_equity_mixed = partial(get_historical_fund_codes, get_fund_codes_equity_mixed_main)
get_historical_fund_codes_bond_mixed = partial(get_historical_fund_codes, get_fund_codes_bond_mixed_main)
get_historical_fund_codes_multi_asset = partial(get_historical_fund_codes, get_fund_codes_multi_asset_main)
get_historical_fund_codes_variable = partial(get_historical_fund_codes, get_fund_codes_variable_main)
get_historical_fund_codes_mothers = partial(get_historical_fund_codes, get_fund_codes_mothers)
get_historical_fund_codes_class = partial(get_historical_fund_codes, get_fund_codes_class)
get_historical_fund_codes_generals = partial(get_historical_fund_codes, get_fund_codes_generals)
get_historical_fund_codes_nonclassified = partial(get_historical_fund_codes, get_fund_codes_nonclassified)
get_historical_fund_codes_aum = partial(get_historical_fund_codes, get_fund_codes_aum)

def get_data_historical_fund_codes(option_save: bool = True)->dict[str, list[str]]:
    data = {
        'all': get_historical_fund_codes_all(),
        'main': get_historical_fund_codes_main(),
        'division_01': get_historical_fund_codes_division_01(),
        'division_02': get_historical_fund_codes_division_02(),
        'equity': get_historical_fund_codes_equity(),
        'equity_mixed': get_historical_fund_codes_equity_mixed(),
        'bond_mixed': get_historical_fund_codes_bond_mixed(),
        'multi_asset': get_historical_fund_codes_multi_asset(),
        'variable': get_historical_fund_codes_variable(),
        'mothers': get_historical_fund_codes_mothers(),
        'class': get_historical_fund_codes_class(),
        'generals': get_historical_fund_codes_generals(),
        'nonclassified': get_historical_fund_codes_nonclassified(),
        'aum': get_historical_fund_codes_aum(),
        'aum_division_01': get_historical_fund_codes_aum_division_01(),
        'aum_division_02': get_historical_fund_codes_aum_division_02(),
    }
    if option_save:
        map_data_to_json(data, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-historical_fund_codes-save{get_today().replace("-", "")}.json')
    return data

def load_data_historical_fund_codes(file_folder: str = FILE_FOLDER['fund_code'])->dict[str, list[str]]:
    regex = f'json-historical_fund_codes-.*save{get_today().replace("-", "")}'
    file_names = scan_files_including_regex(file_folder=file_folder, regex=regex)
    file_name = file_names[-1]
    data = map_json_to_data(file_folder=file_folder, file_name=file_name)
    return data

def map_label_to_historical_fund_codes_in_local(label: str):
    data = map_json_to_data(file_folder=FILE_FOLDER['fund_code'], file_name=f'json-historical_fund_codes-save{get_today().replace("-", "")}.json')
    return data[label]

def map_label_to_historical_fund_codes(label: str):
    data = get_data_historical_fund_codes()
    return data[label]

def get_historical_fund_codes_aum_division_01():
    dates = get_all_existent_dates_in_collection(COLLECTION_2110, 'date_ref')
    sets = []
    for date in dates:
        fund_codes_aum_division_01 = get_fund_codes_aum_division_01(date_ref=date)
        sets = [*sets, *fund_codes_aum_division_01]
    sets = set(sets)
    return sorted(list(sets))

def get_historical_fund_codes_aum_division_02():
    dates = get_all_existent_dates_in_collection(COLLECTION_2110, 'date_ref')
    sets = []
    for date in dates:
        fund_codes_aum_division_02 = get_fund_codes_aum_division_02(date_ref=date)
        sets = [*sets, *fund_codes_aum_division_02]
    sets = set(sets)
    return sorted(list(sets))

