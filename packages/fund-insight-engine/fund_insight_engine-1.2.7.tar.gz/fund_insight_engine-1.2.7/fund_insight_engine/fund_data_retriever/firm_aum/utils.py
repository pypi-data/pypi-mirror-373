from functools import partial
import numpy as np
import pandas as pd
from string_date_controller import get_today, get_date_n_days_ago
from shining_pebbles import scan_files_including_regex
from canonical_transformer.morphisms import map_df_to_csv, map_csv_to_df, map_json_to_data
from fund_insight_engine.fund_data_retriever.fund_codes import get_fund_codes_total
from fund_insight_engine.fund_data_retriever.fund_codes.historical import map_label_to_historical_fund_codes, map_label_to_historical_fund_codes_in_local
from fund_insight_engine.path_director import FILE_FOLDER
from fund_insight_engine.fund_data_retriever.basis import get_df_fund_data

get_df_firm_aum = partial(get_df_fund_data, key='순자산')

def get_firm_aum_total(option_save: bool = True)->pd.DataFrame:
    df_firm_aum_total = get_df_firm_aum(fund_codes_kernel=get_fund_codes_total)
    if option_save:
        map_df_to_csv(df_firm_aum_total, file_folder=FILE_FOLDER['firm_aum'], file_name=f'dataset-firm_aum_total-save{get_today().replace("-", "")}.csv')
    return df_firm_aum_total

def load_firm_aum_by_label(label: str, file_folder: str = FILE_FOLDER['firm_aum'])->pd.DataFrame:
    file_names = scan_files_including_regex(file_folder=file_folder, regex=f'dataset-firm_aum_{label}-')
    file_name = file_names[-1]
    df = map_csv_to_df(file_folder=file_folder, file_name=file_name)
    return df
 
def get_firm_aum_by_label(label: str, option_save: bool = True)->pd.DataFrame:
    df_firm_aum_total = load_firm_aum_total()
    try:
        fund_codes_by_label = map_label_to_historical_fund_codes_in_local(label)
    except:
        fund_codes_by_label = map_label_to_historical_fund_codes(label)
    fund_codes_in_df = list(df_firm_aum_total.columns)
    fund_codes = [fund_code for fund_code in fund_codes_by_label if fund_code in fund_codes_in_df]
    df_firm_aum_by_label = df_firm_aum_total[fund_codes]
    if option_save:
        map_df_to_csv(df_firm_aum_by_label, file_folder=FILE_FOLDER['firm_aum'], file_name=f'dataset-firm_aum_{label}-save{get_today().replace("-", "")}.csv')
    return df_firm_aum_by_label


get_firm_aum_main = partial(get_firm_aum_by_label, label='main')
get_firm_aum_division_01 = partial(get_firm_aum_by_label, label='division_01')
get_firm_aum_division_02 = partial(get_firm_aum_by_label, label='division_02')
get_firm_aum_equity = partial(get_firm_aum_by_label, label='equity')
get_firm_aum_equity_mixed = partial(get_firm_aum_by_label, label='equity_mixed')
get_firm_aum_bond_mixed = partial(get_firm_aum_by_label, label='bond_mixed')
get_firm_aum_multi_asset = partial(get_firm_aum_by_label, label='multi_asset')
get_firm_aum_variable = partial(get_firm_aum_by_label, label='variable')
get_firm_aum_mothers = partial(get_firm_aum_by_label, label='mothers')
get_firm_aum_class = partial(get_firm_aum_by_label, label='class')
get_firm_aum_generals = partial(get_firm_aum_by_label, label='generals')
get_firm_aum_nonclassified = partial(get_firm_aum_by_label, label='nonclassified')
get_firm_aum = partial(get_firm_aum_by_label, label='aum')

load_firm_aum_total = partial(load_firm_aum_by_label, label='total')
load_firm_aum_main = partial(load_firm_aum_by_label, label='main')
load_firm_aum_division_01 = partial(load_firm_aum_by_label, label='division_01')
load_firm_aum_division_02 = partial(load_firm_aum_by_label, label='division_02')
load_firm_aum_equity = partial(load_firm_aum_by_label, label='equity')
load_firm_aum_equity_mixed = partial(load_firm_aum_by_label, label='equity_mixed')
load_firm_aum_bond_mixed = partial(load_firm_aum_by_label, label='bond_mixed')
load_firm_aum_multi_asset = partial(load_firm_aum_by_label, label='multi_asset')
load_firm_aum_variable = partial(load_firm_aum_by_label, label='variable')
load_firm_aum_mothers = partial(load_firm_aum_by_label, label='mothers')