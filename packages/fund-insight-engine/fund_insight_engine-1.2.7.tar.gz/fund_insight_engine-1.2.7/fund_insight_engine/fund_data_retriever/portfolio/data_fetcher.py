from .portfolio_fetcher import get_latest_date_ref_of_menu2205_by_fund_code, fetch_data_menu2205, fetch_df_menu2205
import pandas as pd

class DataFetcher:
    def __init__(self, fund_code, date_ref=None, option_verbose=False):
        self.fund_code = fund_code
        self.date_ref = date_ref
        self.option_verbose = option_verbose
        self.data = None
        self.df = None
        self._load_pipeline()
    
    def fetch_date_ref(self):
        if self.date_ref is None:
            self.date_ref = get_latest_date_ref_of_menu2205_by_fund_code(self.fund_code)
        return self.date_ref

    def fetch_data(self):
        if self.data is None:
            self.data = fetch_data_menu2205(self.fund_code, self.fetch_date_ref(), option_verbose=self.option_verbose)
        return self.data
        
    def fetch_df(self):
        if self.df is None:
            self.df = pd.DataFrame(self.data)
        return self.df
        
    def _load_pipeline(self):
        lst_of_methods = [self.fetch_date_ref, self.fetch_data, self.fetch_df]
        for method in lst_of_methods:
            try:
                if self.option_verbose:
                    print(f'load: {method.__name__} ...')
                method()
            except Exception as e:
                print(f'DataFetcher _load_pipeline error: {e}')
                return False
        return True