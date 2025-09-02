import pandas as pd
import re
from fund_insight_engine.market_retriever.global_currency import get_currency

usdkrw_of_date = lambda date_ref: get_currency('USDKRW Curncy').loc[date_ref].iloc[-1]

def transform_name_title(fund_name):
    fund_name_title = (
        fund_name
        .replace(' ', '')
        .replace('라이프', '라이프 ')
        .replace('일반사모투자신탁', '')
        .replace('전문투자형사모투자신탁', ' ')
        .replace('일반사모증권투자신탁', ' ')
        .replace('목표달성형', ' ')
        .replace('(주식_라이프_일반)', ' ')
        .replace('(채권혼합)', ' ')
    )   
    fund_name_title = re.sub(r'제(\d+)호', r' 제\1호', fund_name_title)
    fund_name_title = re.sub(r'제(\d+)종', r' 제\1종', fund_name_title)
    return fund_name_title


def transform_name_review(fund_name):
    fund_name_title = (
        fund_name
        .replace(' ', '')
        .replace('라이프', '라이프 ')
        .replace('일반사모투자신탁', ' 일반사모투자신탁')
        .replace('전문투자형사모투자신탁', ' 전문투자형사모투자신탁')
        .replace('일반사모증권투자신탁', ' 일반사모증권투자신탁')
        .replace('목표달성형', ' 목표달성형')
        .replace('(주식_라이프_일반)', ' (주식_라이프_일반)')
        .replace('(채권혼합)', ' (채권혼합)')

    )   
    fund_name_title = re.sub(r'제(\d+)호', r' 제\1호', fund_name_title)

    return fund_name_title

def transform_to_korean_unit(s):
    if pd.isna(s) or s == "NaN":
        return s
    else:
        s = s.replace(',', '') if isinstance(s, str) else s
        n = int(s)
        if n >= 1e14:  # 천조 이상
            return "{:,.0f}조".format(n / 1e12)
        elif n >= 1e12:  # 조
            return "{:,.1f}조".format(n / 1e12).rstrip('.0')
        elif n >= 1e10:  # 억
            return "{:,.0f}억".format(n / 1e8)
        elif len(str(n)) >= 9:
            return "{:,.1f}억".format(n / 1e8).rstrip('.0')
        elif n == 0:
            return '-'
        else:
            return "{:,.0f}".format(n)

def transform_to_english_unit(s):
    if pd.isna(s) or s == "NaN":
        return s
    else:
        s = s.replace(',', '') if isinstance(s, str) else s
        n = int(s)
        if n >= 1e12:  # Trillion
            return "{:,.1f}T".format(n / 1e12).rstrip('.0')
        elif n >= 1e9:  # Billion
            return "{:,.1f}B".format(n / 1e9).rstrip('.0')
        elif n >= 1e6:  # Million
            return "{:,.1f}M".format(n / 1e6).rstrip('.0')
        elif n >= 1e3:  # Thousand
            return "{:,.1f}K".format(n / 1e3).rstrip('.0')
        elif n == 0:
            return '-'
        else:  # Less than thousand, just the number
            return "{:,.0f}".format(n)

def transform_to_usd_unit(number_in_krw, date_ref):
    return transform_to_english_unit(number_in_krw / usdkrw_of_date(date_ref))


def transform_to_date_ref_text(date_ref):
    year, month, day = date_ref.split('-')
    month = month[0] if month[0]==0 else month
    return f"'{year[-2:]}.{month}.{day}"


def set_default_benchmarks(benchmark):
    if benchmark == 'KOSPI':
        benchmarks = [benchmark, 'KOSPI200', 'KOSDAQ']
    elif benchmark == 'KOSDAQ':
        benchmarks = [benchmark, 'KOSPI', 'KOSPI200']
    return benchmarks

def concatenate_benchmark_names(benchmark_names):
    benchmark_names = [benchmark_name.replace(' ', '_') for benchmark_name in benchmark_names]
    return '&'.join(benchmark_names)

invese_parse_benchmark_names = concatenate_benchmark_names

def parse_benchmark_names(benchmark_names_with_ampersand):
    if benchmark_names_with_ampersand == None:
        return None
    benchmark_names = benchmark_names_with_ampersand.split('&')
    benchmark_names = [benchmark_name.replace('_', ' ') for benchmark_name in benchmark_names]
    return benchmark_names