from fund_insight_engine.fund_data_retriever.fund_mappings.mappings import get_mapping_fund_names_mongodb

def get_fund_codes_all(date_ref=None):
    mapping_fund_names = get_mapping_fund_names_mongodb(date_ref=date_ref)
    return sorted(list(mapping_fund_names.keys()))
    
get_fund_codes_total = get_fund_codes_all