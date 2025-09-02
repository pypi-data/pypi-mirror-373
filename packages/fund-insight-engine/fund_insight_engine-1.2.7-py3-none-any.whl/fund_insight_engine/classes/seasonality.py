from functools import cached_property
from timeseries_performance_calculator import Seasonality
from fund_insight_engine.price_retriever import get_timeseries_price

class SeasonalityLoader:
    def __init__(self, ticker: str, benchmark_ticker: str=None):
        self.ticker = ticker
        self.benchmark_ticker = benchmark_ticker if benchmark_ticker else None
        self.prices = get_timeseries_price(ticker=self.ticker)
        self.benchmark_prices = get_timeseries_price(ticker=self.benchmark_ticker) if self.benchmark_ticker else None
        self.loader = Seasonality(timeseries=self.prices, benchmark_timeseries=self.benchmark_prices)

    @cached_property
    def seasonality(self):
        return self.loader.seasonality
    
    @cached_property
    def benchmark_seasonality(self):
        return self.loader.benchmark_seasonality
    
    @cached_property
    def relative_seasonality(self):
        return self.loader.relative_seasonality
    