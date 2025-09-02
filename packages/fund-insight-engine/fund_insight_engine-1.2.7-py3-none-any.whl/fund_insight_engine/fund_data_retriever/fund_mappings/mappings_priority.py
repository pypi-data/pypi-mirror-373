from .mappings_divisions import get_mapping_fund_names_division_01, get_mapping_fund_names_division_02
from .mappings import get_mapping_fund_names_mongodb

def get_mapping_fund_names_with_priority_1(date_ref=None):
    mapping_fund_names_division_01 = get_mapping_fund_names_division_01(date_ref=date_ref)
    return mapping_fund_names_division_01

def get_mapping_fund_names_with_priority_2(date_ref=None):
    mapping_fund_names_division_02 = get_mapping_fund_names_division_02(date_ref=date_ref)
    return mapping_fund_names_division_02

def get_mapping_fund_names_with_non_priority(date_ref=None):
    mapping_fund_names = get_mapping_fund_names_mongodb(date_ref=date_ref)
    mapping_fund_names_priority_1 = get_mapping_fund_names_with_priority_1(date_ref=date_ref)
    mapping_fund_names_priority_2 = get_mapping_fund_names_with_priority_2(date_ref=date_ref)
    mapping_fund_names_non_priority = {k: v for k, v in mapping_fund_names.items() if k not in mapping_fund_names_priority_1 and k not in mapping_fund_names_priority_2}
    return mapping_fund_names_non_priority
