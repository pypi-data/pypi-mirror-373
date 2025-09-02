from functools import cached_property
from fund_insight_engine.fund import Fund
from .marketing_proposal_syles import (
    style_total_performance,
    style_period_returns,
    style_monthly_relative,
)
from canonical_transformer.morphisms import map_df_to_data

class MarketingProposal:
    def __init__(self, fund_code, start_date=None, end_date=None, benchmark_names=None, metrics=None, option_round=2):
        self.fund_code = fund_code
        self.benchmark_names = benchmark_names
        self.metrics = metrics
        self.option_round = option_round
        self.f = Fund(fund_code=fund_code, start_date=start_date, end_date=end_date, benchmark_names=benchmark_names)
        self.start_date = self.set_start_date(start_date)
        self.end_date = self.set_end_date(end_date)

    def set_start_date(self, start_date):
        return start_date if start_date else self.f.pm.date_i

    def set_end_date(self, end_date):
        return end_date if end_date else self.f.pm.date_f
    
    def set_benchmark_names(self, benchmark_names):
        return benchmark_names if benchmark_names else self.benchmark_names
    
    @cached_property
    def cumreturns(self):
        return self.f.cumreturns
    
    @cached_property
    def proportions(self):
        return self.f.proportions

    @cached_property
    def total_performance(self):
        TEMP_COLS_TO_KEEP = ['annualized_return_cagr', 'annualized_return_days', 'annualized_volatility', 'beta', 'maxdrawdown', 'sharpe_ratio', 'winning_ratio']
        return style_total_performance(self.f.total_performance[TEMP_COLS_TO_KEEP], self.metrics, self.option_round)
    
    @cached_property
    def period_returns(self):
        return style_period_returns(self.f.period_returns, self.option_round)
    
    @cached_property
    def dfs_monthly_relative(self):
        return {year: style_monthly_relative(df, self.option_round) for year, df in self.f.dfs_relative.items()}

    @cached_property
    def data_cumreturns(self):
        return map_df_to_data(self.cumreturns)
    
    @cached_property
    def data_proportions(self):
        return map_df_to_data(self.proportions)

    @cached_property
    def data_total_performance(self):
        return map_df_to_data(self.total_performance)

    @cached_property
    def data_period_returns(self):
        return map_df_to_data(self.period_returns)

    @cached_property
    def data_monthly_relative(self):
        return {year: map_df_to_data(df) for year, df in self.dfs_monthly_relative.items()}

    @cached_property
    def nav(self):
        return self.f.numbers.loc['순자산'].iloc[0]

    @cached_property
    def fund_name(self):
        return self.f.numbers.loc['펀드명'].iloc[0]

    @cached_property
    def date_inception(self):
        return self.f.numbers.loc['설정일'].iloc[0]
    
    @cached_property
    def benchmark_name(self):
        return self.total_performance.index[1]
    
    @cached_property
    def bulk(self):
        return {
            'fund_code': self.fund_code,
            'fund_name': self.fund_name,
            'date_inception': self.date_inception,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'nav': self.nav,
            'cumreturns': self.data_cumreturns,
            'proportions': self.data_proportions,
            'total_performance': self.data_total_performance,
            'period_returns': self.data_period_returns,
            'monthly_relative': self.data_monthly_relative,
            'benchmark_name': self.benchmark_name,
        }
    