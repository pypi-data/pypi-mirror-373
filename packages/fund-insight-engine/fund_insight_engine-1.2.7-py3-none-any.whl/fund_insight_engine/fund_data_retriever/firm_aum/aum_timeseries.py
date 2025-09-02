import pandas as pd
from fund_insight_engine.market_retriever.global_currency import get_currency
from .aum_retriever import fetch_firm_aum, fetch_exact_firm_aum

def get_timeseries_firm_aum() -> pd.DataFrame:
    data = fetch_firm_aum()
    aum = (
        pd.DataFrame(data)
        .rename(columns={'일자': 'Date', '순자산': 'Firm AUM: KRW'})
        .set_index('Date')
    )
    usdkrw = get_currency(ticker_bbg_curncy='USDKRW Curncy')

    aum = aum.join(usdkrw)
    aum['Firm AUM: USD'] = aum['Firm AUM: KRW'] / aum['USDKRW Curncy']

    return aum

def get_timeseries_exact_firm_aum():
    data = fetch_exact_firm_aum()
    aum = (
        pd.DataFrame(data)
        .rename(columns={'일자': 'Date', '순자산': 'Firm AUM: KRW'})
        .set_index('Date')
    )
    usdkrw = get_currency(ticker_bbg_curncy='USDKRW Curncy')

    aum = aum.join(usdkrw)
    aum['Firm AUM: USD'] = aum['Firm AUM: KRW'] / aum['USDKRW Curncy']

    return aum
