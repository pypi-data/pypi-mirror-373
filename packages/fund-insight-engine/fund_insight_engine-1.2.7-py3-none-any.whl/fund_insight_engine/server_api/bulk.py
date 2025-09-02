import pandas as pd
from fund_insight_engine.fund import Fund
from canonical_transformer.morphisms import *
from fund_insight_engine.path_director import FILE_FOLDER
from string_date_controller import get_today, get_date_n_days_ago

def get_bulk_data_of_fund(fund_code: str, start_date: str=None, end_date: str=None, index_ref: str=None, option_save: bool=True) -> pd.DataFrame:
    if start_date and end_date:
        f = Fund(fund_code=fund_code, start_date=start_date, end_date=end_date)
    elif start_date and not end_date:
        f = Fund(fund_code=fund_code, start_date=start_date)
        end_date = f.pm.date_f
    elif not start_date and end_date:
        f = Fund(fund_code=fund_code, end_date=end_date)
        start_date = f.pm.date_i
    else:
        f = Fund(fund_code=fund_code)
        start_date = f.pm.date_i
        end_date= f.pm.date_f
    
    prices = map_df_to_data(f.prices)
    returns = map_df_to_data(f.returns)
    cumreturns = map_df_to_data(f.cumreturns)
    prices_and_proportions = map_df_to_data(f.prices_and_proportions)
    info = map_df_to_data(f.info)
    info_concise = map_df_to_data(f.info_concise)
    fee = map_df_to_data(f.fee)
    numbers = map_df_to_data(f.numbers)
    period_returns = map_df_to_data(f.period_returns)
    yearly_returns = map_df_to_data(f.yearly_returns)
    monthly_returns = map_df_to_data(f.monthly_returns)
    monthly_relative = [map_df_to_data(df) for df in f.monthly_relative]
    dfs_relative = {year: map_df_to_data(df) for year, df in f.dfs_relative.items()}
    TEMP_COLS_TO_KEEP = ['annualized_return_cagr', 'annualized_return_days', 'annualized_volatility', 'beta', 'maxdrawdown', 'sharpe_ratio', 'winning_ratio']
    total_performance = map_df_to_data(f.total_performance[TEMP_COLS_TO_KEEP])
    portfolio = map_df_to_data(f.portfolio.df)
    dfs_portfolio = {asset: map_df_to_data(df) for asset, df in f.dfs_portfolio.items()}
    sector = map_df_to_data(f.portfolio.sector)
    cumreturns_ref = map_df_to_data(f.get_cumreturns_ref(index_ref=index_ref))
    
    bulk_data = {
        'prices': prices,
        'returns': returns,
        'cumreturns': cumreturns,
        'prices_and_proportions': prices_and_proportions,
        'info': info,
        'info_concise': info_concise,
        'fee': fee,
        'numbers': numbers,
        'period_returns': period_returns,
        'yearly_returns': yearly_returns,
        'monthly_returns': monthly_returns,
        'monthly_relative': monthly_relative,
        'dfs_relative': dfs_relative,
        'total_performance': total_performance,
        'portfolio': portfolio,
        'dfs_portfolio': dfs_portfolio,
        'sector': sector,
        'cumreturns_ref': cumreturns_ref
    }

    if option_save:
        index_ref = index_ref if index_ref else f.default_inputs['index_ref']
        map_data_to_json(bulk_data, file_folder=FILE_FOLDER['bulk'], file_name=f'json-code{fund_code}-from{start_date.replace("-", "")}-to{end_date.replace("-", "")}-at{index_ref.replace("-", "")}-save{get_today().replace("-", "")}.json')

    return bulk_data