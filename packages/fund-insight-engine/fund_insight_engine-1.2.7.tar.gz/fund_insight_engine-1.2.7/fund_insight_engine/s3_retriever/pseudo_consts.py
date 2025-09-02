from .divisions import get_mapping_by_division
from .fund_class import get_mapping_by_fund_class
from .fund_types import get_mapping_by_fund_type


MAPPING_FUNDS_DIVISION_01 = get_mapping_by_division('운용1본부')
MAPPING_FUNDS_DIVISION_02 = get_mapping_by_division('운용2본부')

MAPPING_FUNDS_MAIN = get_mapping_by_fund_class('주요')
MAPPING_FUNDS_MOTHER = get_mapping_by_fund_class('운용펀드')
MAPPING_FUNDS_GENERAL = get_mapping_by_fund_class('일반')
MAPPING_FUNDS_NONCLASSIFIED = get_mapping_by_fund_class('-')
MAPPING_FUNDS_CLASS = get_mapping_by_fund_class('클래스펀드')

MAPPING_FUNDS_EQUITY = get_mapping_by_fund_type('주식형')
MAPPING_FUNDS_EQUITY_MIXED = get_mapping_by_fund_type('주식혼합')
MAPPING_FUNDS_BOND_MIXED = get_mapping_by_fund_type('채권혼합')
MAPPING_FUNDS_MULTI_ASSET = get_mapping_by_fund_type('혼합자산')
MAPPING_FUNDS_VARIABLE = get_mapping_by_fund_type('변액')