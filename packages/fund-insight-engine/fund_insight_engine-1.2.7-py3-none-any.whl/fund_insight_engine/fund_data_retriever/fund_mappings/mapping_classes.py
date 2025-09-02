from functools import partial
from fund_insight_engine.fund_data_retriever.fund_mappings.mappings import get_mapping_fund_names_mongodb
from fund_insight_engine.fund_data_retriever.fund_codes.classes import (
    get_fund_codes_mothers,
    get_fund_codes_generals,
    get_fund_codes_class,
    get_fund_codes_nonclassified,
)
from .mapping_utils import exclude_keywords_from_mapping

def filter_mappings(mapping_fund_names, fund_codes, keywords_to_exclude=None):
    filtered_mapping = {k: v for k, v in mapping_fund_names.items() if k in fund_codes}
    return (exclude_keywords_from_mapping(filtered_mapping, keywords_to_exclude) 
            if keywords_to_exclude else filtered_mapping)

def create_mapping_getter(get_fund_codes_func):
    def get_mapping(date_ref=None, keywords_to_exclude=None):
        mapping_fund_names = get_mapping_fund_names_mongodb(date_ref=date_ref)
        fund_codes = get_fund_codes_func(date_ref=date_ref)
        return filter_mappings(mapping_fund_names, fund_codes, keywords_to_exclude)
    return get_mapping

get_mapping_fund_names_mothers = create_mapping_getter(get_fund_codes_mothers)
get_mapping_fund_names_generals = create_mapping_getter(get_fund_codes_generals)
get_mapping_fund_names_class = create_mapping_getter(get_fund_codes_class)
get_mapping_fund_names_nonclassified = create_mapping_getter(get_fund_codes_nonclassified)