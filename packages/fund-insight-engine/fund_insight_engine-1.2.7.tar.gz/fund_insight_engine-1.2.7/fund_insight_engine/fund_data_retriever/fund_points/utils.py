from functools import partial
from mongodb_controller import COLLECTION_8186
from string_date_controller import get_first_date_of_year, get_date_n_days_ago
from canonical_transformer.functionals import pipe
from .basis import set_dates_for_points_by_kernel, get_two_points, get_two_points_return

set_dates_for_ytd_points = partial(set_dates_for_points_by_kernel, get_first_date_of_year)

get_two_prices = partial(get_two_points, '수정기준가')

def get_fund_ytd_return(fund_code, date_ref=None):
    dates = set_dates_for_ytd_points(fund_code, date_ref)
    prices = get_two_prices(fund_code, *dates)
    return get_two_points_return(*prices)

def get_fund_n_days_return(fund_code, n, date_ref=None):
    kernel = partial(get_date_n_days_ago, n=n)
    dates = set_dates_for_points_by_kernel(kernel, fund_code, date_ref)
    prices = get_two_prices(fund_code, *dates)
    return get_two_points_return(*prices)