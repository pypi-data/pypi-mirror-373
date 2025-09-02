from .mappings import get_mapping_fund_names_mongodb
from fund_insight_engine.fund_data_retriever.fund_codes.aum_fund_filter import get_fund_codes_aum
from fund_insight_engine.fund_data_retriever.fund_codes.divisions import get_fund_codes_division_01_aum, get_fund_codes_division_02_aum

def get_mapping_fund_names_aum(date_ref=None):
    mapping_fund_names = get_mapping_fund_names_mongodb(date_ref=date_ref)
    fund_codes_aum = get_fund_codes_aum(date_ref=date_ref)
    mapping_fund_names_aum = {k: v for k, v in mapping_fund_names.items() if k in fund_codes_aum}
    return mapping_fund_names_aum

def get_mapping_fund_names_division_01_aum(date_ref=None):
    mapping_fund_names = get_mapping_fund_names_mongodb(date_ref=date_ref)
    fund_codes_division_01_aum = get_fund_codes_division_01_aum(date_ref=date_ref)
    mapping_fund_names_division_01_aum = {k: v for k, v in mapping_fund_names.items() if k in fund_codes_division_01_aum}
    return mapping_fund_names_division_01_aum

def get_mapping_fund_names_division_02_aum(date_ref=None):
    mapping_fund_names = get_mapping_fund_names_mongodb(date_ref=date_ref)
    fund_codes_division_02_aum = get_fund_codes_division_02_aum(date_ref=date_ref)
    mapping_fund_names_division_02_aum = {k: v for k, v in mapping_fund_names.items() if k in fund_codes_division_02_aum}
    return mapping_fund_names_division_02_aum

