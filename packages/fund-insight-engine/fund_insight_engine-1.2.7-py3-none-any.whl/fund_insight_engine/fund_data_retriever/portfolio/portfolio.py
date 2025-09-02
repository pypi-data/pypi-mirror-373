from functools import cached_property
import numpy as np
from canonical_transformer import map_data_to_df
from fund_insight_engine.mongodb_retriever.menu2206_retriever.menu2206_utils import fetch_data_menu2206_by_fund
from .portfolio_utils import run_pipeline_from_raw_to_portfolio, get_dfs_by_asset
from .portfolio_customizer import customize_df_portfolio

class Portfolio:
    def __init__(self, fund_code, date_ref=None):
        self.fund_code = fund_code
        self.date_ref = date_ref

    @cached_property
    def data(self):
        return fetch_data_menu2206_by_fund(self.fund_code, self.date_ref)

    @cached_property
    def raw(self):
        return map_data_to_df(self.data)

    @cached_property
    def df(self):
        return run_pipeline_from_raw_to_portfolio(self.raw)

    @cached_property
    def port(self):
        return customize_df_portfolio(self.df)
    
    @cached_property
    def dfs(self):
        return get_dfs_by_asset(self.raw)
    
    @cached_property
    def sector(self):
        df = self.df.copy()
        df = df[df['평가액'] != '']
        df['업종구분/보증기관'] = df['업종구분/보증기관'].replace('', '미분류')
        return df.groupby('업종구분/보증기관').agg({
            '비중': 'sum',
            '평가액': 'sum', 
            '장부가': 'sum',
            '종목': 'count'
        })