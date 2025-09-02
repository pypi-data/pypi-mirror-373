from functools import partial
import pandas as pd
from fund_insight_engine.mongodb_retriever.menu2206_retriever.menu2206_utils import get_df_menu2206_snapshot
from fund_insight_engine.fund_data_retriever.fund_codes.main_fund_filter import get_fund_codes_main
from fund_insight_engine.fund_data_retriever.portfolio.portfolio_consts import VALID_ASSETS

def get_ranked_holdings(rank_by: str, option_ascending: bool = False, date_ref: str = None):
    MAPPING_RANK_BY = {
        'pnl': '원화 보유정보: 총평가손익',
        'return': '원화 보유정보: 총평가손익률',
        'valuation': '원화 보유정보: 평가액',
    }
    COLS_TO_KEEP = ['종목명', '원화 보유정보: 취득액', '원화 보유정보: 평가액', '원화 보유정보: 총평가손익', '원화 보유정보: 총평가손익률']
    COLS_RENAMED = ['종목명', '취득액', '평가액', '총평가손익', '총평가손익률']
    MAPPING_RENAMED = dict(zip(COLS_TO_KEEP, COLS_RENAMED))

    df = get_df_menu2206_snapshot(date_ref=date_ref)
    df = df[df['펀드코드'].isin(get_fund_codes_main(date_ref=date_ref))]
    df['종목: 펀드코드'] = df.apply(lambda row: f"{row['종목']}: {row['펀드코드']}", axis=1)
    df = df.set_index('종목: 펀드코드').drop(columns=['종목', '펀드코드'])
    df = df[df['자산'].isin(VALID_ASSETS)]
    df = df[COLS_TO_KEEP]
    df[MAPPING_RANK_BY[rank_by]] = pd.to_numeric(df[MAPPING_RANK_BY[rank_by]], errors='coerce').fillna(0)
    df = df.sort_values(by=MAPPING_RANK_BY[rank_by], ascending=option_ascending)
    df = df.rename(columns=MAPPING_RENAMED)
    return df

get_pnl_ranking = partial(get_ranked_holdings, rank_by='pnl')
get_return_ranking = partial(get_ranked_holdings, rank_by='return')
get_valuation_ranking = partial(get_ranked_holdings, rank_by='valuation')