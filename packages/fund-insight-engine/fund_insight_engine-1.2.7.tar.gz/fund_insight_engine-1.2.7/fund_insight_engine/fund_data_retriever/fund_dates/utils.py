from .inception import get_inception_date
from .latest import get_latest_date_ref_in_configuration
from .default import get_default_date_ref

def get_default_dates(fund_code):
    date_inception = get_inception_date(fund_code)                   
    date_latest = get_latest_date_ref_in_configuration()
    index_ref = get_default_date_ref(date_inception, date_latest)
    return {
        'date_inception': date_inception,
        'date_latest': date_latest,
        'index_ref': index_ref,
    }