from string_date_controller import get_today
from canonical_transformer.morphisms import map_data_to_json
from fund_insight_engine.fund_data_retriever.fund_dates.latest import get_latest_date_ref_in_2110
# from fund_insight_engine.fund_data_retriever.fund_codes import (
#     get_fund_codes_all,
#     get_fund_codes_main,
#     get_fund_codes_division_01_main,
#     get_fund_codes_division_02_main,
#     get_fund_codes_equity_main,
#     get_fund_codes_equity_mixed_main,
#     get_fund_codes_bond_mixed_main,
#     get_fund_codes_multi_asset_main,
#     get_fund_codes_variable_main,
#     get_fund_codes_mothers,
#     get_fund_codes_class,
#     get_fund_codes_generals,
#     get_fund_codes_nonclassified,
#     get_fund_codes_aum,
#     get_fund_codes_aum_division_01,
#     get_fund_codes_aum_division_02,
# )
from fund_insight_engine.path_director import FILE_FOLDER
from fund_insight_engine.fund_data_retriever.fund_codes import (
    get_data_fund_codes_by_type,
    get_data_fund_codes_aum_by_type,
    get_data_fund_codes_main_by_type,
    get_data_fund_codes_by_division,
    get_data_fund_codes_aum_by_division,
    get_data_fund_codes_main_by_division,
    get_data_fund_codes_by_trust,
    get_data_fund_codes_main_by_trust,
    get_data_fund_codes_aum_by_trust,
    get_data_fund_codes_by_aum_filter,
    get_data_fund_codes_by_main_filter,
    get_data_fund_codes_by_class_category,
    get_fund_codes_all,
)

# def get_data_fund_codes_snapshot(date_ref=None, option_save: bool = True):
#     date_ref = date_ref or get_latest_date_ref_in_2110()
#     data = {
#         'total': get_fund_codes_all(date_ref=date_ref),
#         'main': get_fund_codes_main(date_ref=date_ref),
#         'division_01': get_fund_codes_division_01_main(date_ref=date_ref),
#         'division_02': get_fund_codes_division_02_main(date_ref=date_ref),
#         'equity': get_fund_codes_equity_main(date_ref=date_ref),
#         'equity_mixed': get_fund_codes_equity_mixed_main(date_ref=date_ref),
#         'bond_mixed': get_fund_codes_bond_mixed_main(date_ref=date_ref),
#         'multi_asset': get_fund_codes_multi_asset_main(date_ref=date_ref),
#         'variable': get_fund_codes_variable_main(date_ref=date_ref),
#         'mothers': get_fund_codes_mothers(date_ref=date_ref),
#         'class': get_fund_codes_class(date_ref=date_ref),
#         'generals': get_fund_codes_generals(date_ref=date_ref),
#         'nonclassified': get_fund_codes_nonclassified(date_ref=date_ref),
#         'aum': get_fund_codes_aum(date_ref=date_ref),
#         'aum_division_01': get_fund_codes_aum_division_01(date_ref=date_ref),
#         'aum_division_02': get_fund_codes_aum_division_02(date_ref=date_ref),
#     }
#     data_snapshot = {'date_ref': date_ref, 'data': data}
#     if option_save:
#         map_data_to_json(data_snapshot, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_snapshot-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
#     return data_snapshot

def get_data_fund_codes_snapshot(date_ref=None, option_save: bool = True):
    date_ref = date_ref or get_latest_date_ref_in_2110()
    fund_codes_total = get_fund_codes_all(date_ref=date_ref)
    data_by_type = get_data_fund_codes_by_type(date_ref=date_ref, option_save=False)['data']
    data_by_type_aum = get_data_fund_codes_aum_by_type(date_ref=date_ref, option_save=False)['data']
    data_by_type_main = get_data_fund_codes_main_by_type(date_ref=date_ref, option_save=False)['data']
    data_by_division = get_data_fund_codes_by_division(date_ref=date_ref, option_save=False)['data']
    data_by_division_aum = get_data_fund_codes_aum_by_division(date_ref=date_ref, option_save=False)['data']
    data_by_division_main = get_data_fund_codes_main_by_division(date_ref=date_ref, option_save=False)['data']
    data_by_trust = get_data_fund_codes_by_trust(date_ref=date_ref, option_save=False)['data']
    data_by_trust_aum = get_data_fund_codes_aum_by_trust(date_ref=date_ref, option_save=False)['data']
    data_by_trust_main = get_data_fund_codes_main_by_trust(date_ref=date_ref, option_save=False)['data']
    data_by_class = get_data_fund_codes_by_class_category(date_ref=date_ref, option_save=False)['data']
    data_by_aum_filter = get_data_fund_codes_by_aum_filter(date_ref=date_ref, option_save=False)['data']
    data_by_main_filter = get_data_fund_codes_by_main_filter(date_ref=date_ref, option_save=False)['data']

    data_snapshot = {
        'date_ref': date_ref,
        'total': fund_codes_total,
        'type: total': data_by_type,
        'type: aum': data_by_type_aum,
        'type: main': data_by_type_main,
        'division: total': data_by_division,
        'division: aum': data_by_division_aum,
        'division: main': data_by_division_main,
        'trust: total': data_by_trust,
        'trust: aum': data_by_trust_aum,
        'trust: main': data_by_trust_main,
        'class': data_by_class,
        'aum': data_by_aum_filter,
        'main': data_by_main_filter,
    }
    if option_save:
        map_data_to_json(data_snapshot, file_folder=FILE_FOLDER['fund_code'], file_name=f'json-fund_codes_snapshot-at{date_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')
    return data_snapshot
