from functools import cached_property
from fund_insight_engine.price_retriever import get_timeserieses_price
from fund_insight_engine.market_retriever.free_returns import get_timeseries_free_returns
from timeseries_performance_calculator import Performance

class Cluster:
    def __init__(self, tickers, benchmark_name=None, benchmark_index=-1, free_returns=get_timeseries_free_returns()):
        self.tickers = tickers
        self.benchmark_name = benchmark_name
        self.benchmark_index = benchmark_index
        self.free_returns = free_returns
        self.prices = get_timeserieses_price(tickers)
        self.performance = Performance(timeseries=self.prices, benchmark_index=self.benchmark_index, benchmark_name=self.benchmark_name, free_returns=self.free_returns)

    @cached_property
    def prices(self):
        return self.performance.prices

    @cached_property
    def returns(self):
        return self.performance.returns
    
    @cached_property
    def cumreturns(self):
        return self.performance.cumreturns
    
    @cached_property
    def total_performance(self):
        return self.performance.total_performance
    
    @cached_property
    def period_returns(self):
        return self.performance.period_returns
    
    @cached_property
    def monthly_returns(self):
        return self.performance.monthly_returns
    
    @cached_property
    def yearly_returns(self):
        return self.performance.yearly_returns
    
    @cached_property
    def yearly_relative(self):
        return self.performance.yearly_relative
    
    @cached_property
    def annualized_return_cagr(self):
        return self.performance.annualized_return_cagr
    
    @cached_property
    def annualized_return_days(self):
        return self.performance.annualized_return_days
    
    @cached_property
    def annualized_volatility(self):
        return self.performance.annualized_volatility
    
    @cached_property
    def maxdrawdown(self):
        return self.performance.maxdrawdown
    
    @cached_property
    def sharpe_ratio(self):
        return self.performance.sharpe_ratio
    
    @cached_property
    def beta(self):
        return self.performance.beta
    
    
    def plot_cumreturns(
            self,
            title=None, 
            option_last_name=False, 
            option_last_value=True, 
            option_main=False, 
            option_num_to_show=None,
            figsize=None
            ):
        return self.performance.plot_cumreturns(      
            title=title, 
            option_last_name=option_last_name, 
            option_last_value=option_last_value, 
            option_main=option_main, 
            option_num_to_show=option_num_to_show,
            figsize=figsize
            )
    