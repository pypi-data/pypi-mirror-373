from canonical_transformer import map_data_to_df
from fund_insight_engine.mongodb_retriever.menu8186_retriever.menu8186_utils import (
    fetch_data_menu8186_by_fund
)
from .timeseries_utils import (
    project_timeseries
)

class Timeseries:
    def __init__(self, fund_code, start_date=None, end_date=None):
        self.fund_code = fund_code
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.raw = None
        self.df = None
        self._load_pipeline()

    def get_data(self):
        if self.data is None:
            self.data = fetch_data_menu8186_by_fund(self.fund_code, self.start_date, self.end_date)
        return self.data

    def get_raw(self):
        if self.raw is None:
            self.raw = map_data_to_df(self.data).set_index('일자')
        return self.raw

    def get_df(self):
        if self.df is None:
            self.df = project_timeseries(self.get_raw())
        return self.df
    
    def _load_pipeline(self):
        try:
            self.get_data()
            self.get_raw()
            self.get_df()
            return True
        except Exception as e:
            print(f'Timeseries _load_pipeline error: {e}')
            return False
