from fund_insight_engine.fund_data_retriever.fund_codes.types import (
    get_mapping_fund_names_equity as get_mapping_equity,
    get_mapping_fund_names_bond_mixed as get_mapping_bond_mixed,
    get_mapping_fund_names_multi_asset as get_mapping_multi_asset,
    get_mapping_fund_names_equity_mixed as get_mapping_equity_mixed,
    get_mapping_fund_names_variable as get_mapping_variable,
)
from .mapping_utils import exclude_keywords_from_mapping
from .mapping_consts import KEYWORDS_FOR_MAIN

def get_mapping_fund_names_equity(date_ref=None, keywords_to_exclude=None, option_main=True):
    mapping_fund_names_equity = get_mapping_equity(date_ref=date_ref)
    if option_main:
        mapping_fund_names_equity = exclude_keywords_from_mapping(mapping_fund_names_equity, KEYWORDS_FOR_MAIN)
    if keywords_to_exclude:
        mapping_fund_names_equity = exclude_keywords_from_mapping(mapping_fund_names_equity, keywords_to_exclude)
    return mapping_fund_names_equity
    
def get_mapping_fund_names_bond_mixed(date_ref=None, keywords_to_exclude=None, option_main=True):
    mapping_fund_names_bond_mixed = get_mapping_bond_mixed(date_ref=date_ref)
    if option_main:
        mapping_fund_names_bond_mixed = exclude_keywords_from_mapping(mapping_fund_names_bond_mixed, KEYWORDS_FOR_MAIN)
    if keywords_to_exclude:
        mapping_fund_names_bond_mixed = exclude_keywords_from_mapping(mapping_fund_names_bond_mixed, keywords_to_exclude)
    return mapping_fund_names_bond_mixed
    
def get_mapping_fund_names_multi_asset(date_ref=None, keywords_to_exclude=None, option_main=True):
    mapping_fund_names_multi_asset = get_mapping_multi_asset(date_ref=date_ref)
    if option_main:
        mapping_fund_names_multi_asset = exclude_keywords_from_mapping(mapping_fund_names_multi_asset, KEYWORDS_FOR_MAIN)
    if keywords_to_exclude:
        mapping_fund_names_multi_asset = exclude_keywords_from_mapping(mapping_fund_names_multi_asset, keywords_to_exclude)
    return mapping_fund_names_multi_asset       
    
def get_mapping_fund_names_equity_mixed(date_ref=None, keywords_to_exclude=None, option_main=True):
    mapping_fund_names_equity_mixed = get_mapping_equity_mixed(date_ref=date_ref)
    if option_main:
        mapping_fund_names_equity_mixed = exclude_keywords_from_mapping(mapping_fund_names_equity_mixed, KEYWORDS_FOR_MAIN)
    if keywords_to_exclude:
        mapping_fund_names_equity_mixed = exclude_keywords_from_mapping(mapping_fund_names_equity_mixed, keywords_to_exclude)
    return mapping_fund_names_equity_mixed
    
def get_mapping_fund_names_variable(date_ref=None, keywords_to_exclude=None, option_main=True):
    mapping_fund_names_variable = get_mapping_variable(date_ref=date_ref)
    if option_main:
        mapping_fund_names_variable = exclude_keywords_from_mapping(mapping_fund_names_variable, KEYWORDS_FOR_MAIN)
    if keywords_to_exclude:
        mapping_fund_names_variable = exclude_keywords_from_mapping(mapping_fund_names_variable, keywords_to_exclude)
    return mapping_fund_names_variable