from .utils import get_data_timeseries_manager, get_df_timeseries_manager, slice_timeseries

class TimeseriesManager:
    def __init__(self, fund_code, start_date=None, end_date=None):
        self.fund_code = fund_code
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.df = None
        self._load_pipeline()

    def get_data(self):
        if self.data is None:
            self.data = get_data_timeseries_manager(self.fund_code)
        return self.data

    def get_df(self):
        if self.df is None:
            df = get_df_timeseries_manager(self.fund_code)
            self.df = slice_timeseries(df, self.start_date, self.end_date)
        return self.df
        
    def _load_pipeline(self):
        try:
            self.get_data()
            self.get_df()
            return True
        except Exception as e:
            print(f'Timeseries _load_pipeline error: {e}')
            return False
