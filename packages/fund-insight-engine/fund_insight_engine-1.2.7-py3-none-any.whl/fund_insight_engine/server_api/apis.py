from mongodb_controller import COLLECTION_2110
from fund_insight_engine.mongodb_retriever.general_utils import get_latest_date_in_collection
from fund_insight_engine.fund_data_retriever.fund_configuration.fund_info import fetch_data_fund_info
from fund_insight_engine.fund_data_retriever.fund_configuration.fund_numbers import fetch_data_fund_numbers
from .api_utils import set_default_benchmarks, transform_name_title, transform_name_review, transform_to_date_ref_text, transform_to_korean_unit, transform_to_usd_unit
from fund_insight_engine.fund.fund import Fund

def get_legacy_fund_info(fund_code, end_date=None, option_language='KR'):
    end_date = end_date or get_latest_date_in_collection(COLLECTION_2110, 'date_ref')
    f = Fund(fund_code=fund_code, end_date=end_date)
    info = f.info
    numbers = f.numbers
    name_review = transform_name_review(numbers.loc['펀드명'].iloc[0])
    name_title = transform_name_title(numbers.loc['펀드명'].iloc[0])
    manager = numbers.loc['운용역'].iloc[0]
    nav_num = numbers.loc['순자산'].iloc[0]
    nav_total = transform_to_korean_unit(nav_num)
    nav_total_usd_en = transform_to_usd_unit(nav_num, f.end_date)
    price_ref_num = numbers.loc['수정기준가'].iloc[0]
    price_ref = f"{price_ref_num:,.2f}"
    price_start_num = float(f.price.iloc[0, -1])
    price_start = f"{price_start_num:,.2f}"
    inception_date = numbers.loc['설정일'].iloc[0]
    maturity_date = info.loc['결산일'].iloc[0]
    benchmark = info.loc['BM1: 기준'].iloc[0]
    benchmarks = set_default_benchmarks(benchmark)

    MAPPIING_MANAGER_NAMES = {
            '강대권': 'Darren Kang',
            '이대상': 'DaeSang Lee',
            '남두우': 'DuWoo Nam',
            '이시우': 'SiWoo Lee',
    }
    manager = manager if option_language == 'KR' else MAPPIING_MANAGER_NAMES.get(manager, manager) 

    return {
        'name_review': name_review,
        'name_title': name_title,
        'manager': manager,
        'nav_num': nav_num,
        'nav_total': nav_total,
        'nav_total_usd_en': nav_total_usd_en,
        'price_ref': price_ref,
        'price_ref_num': price_ref_num,
        'price_start': price_start,
        'price_start_num': price_start_num,
        'inception_date': inception_date,
        'input_date': f.end_date,
        'maturity_date': maturity_date,
        'benchmark': benchmark,
        'benchmarks': benchmarks,
    }


def endpoint__api__review__fund_code__end_date__language(fund_code, end_date=None, lang='KR'):
    dct = get_legacy_fund_info(fund_code=fund_code, end_date=end_date, option_language=lang)

    def transform_date(date):
        yyyy = date.split('-')[0]
        mm = date.split('-')[1] 
        dd = date.split('-')[2]
        m = mm[1] if mm[0] == '0' else mm
        d = dd[1] if dd[0] == '0' else dd
        return f"'{yyyy[2:]}.{m}.{d}"

    return {"펀드명": dct['name_review'], "운용규모 (NAV)": dct['nav_total'], "설정일": dct['inception_date'], "기준가": f"{dct['price_ref']} ({transform_date(dct['input_date'])} 수정기준가 기준)"}


def endpoint__api__title__fund_code__end_date__language(fund_code, end_date=None, lang='KR'):
    dct = get_legacy_fund_info(fund_code=fund_code, end_date=end_date, option_language=lang)
    return {"code": fund_code, "name_title": dct['name_title'], "name_review": dct['name_review'], "name_index": "Fund", "manager": dct['manager'], "inception_date": dct['inception_date'], "reference_date": dct['input_date']}