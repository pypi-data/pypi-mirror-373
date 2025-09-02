import pandas as pd
from fund_insight_engine.mongodb_retriever.menu2206_retriever.menu2206_utils import get_df_menu2206_by_fund, get_df_menu2206_snapshot
from .portfolio_consts import (
    COLUMNS_FOR_PORTFOLIO, 
    MAPPING_COLS, VALID_ASSETS, 
    COLUMNS_FOR_PORTFOLIO_SNAPSHOT, 
    COLUMNS_FOR_BOND, MAPPING_COLS_BOND, 
    COLUMNS_FOR_STOCK, MAPPING_COLS_STOCK,
    COLUMNS_FOR_FUTURES, MAPPING_COLS_FUTURES,
    COLUMNS_FOR_TRS, MAPPING_COLS_TRS,
    COLUMNS_FOR_ETF, MAPPING_COLS_ETF
)

get_raw_portfolio_by_fund = get_df_menu2206_by_fund

def filter_df_by_valid_assets(df):    
    if df.empty:
        return df
    df_filtered = df[df['자산'].isin(VALID_ASSETS)].copy()    
    df_filtered['자산'] = pd.Categorical(df_filtered['자산'], categories=VALID_ASSETS, ordered=True)
    df_sorted = df_filtered.sort_values('자산')
    return df_sorted

def project_df_by_columns(df, columns=COLUMNS_FOR_PORTFOLIO):
    return df[columns]

def rename_df_by_columns(df, columns=MAPPING_COLS):
    return df.rename(columns=columns)

def run_pipeline_from_raw_to_portfolio(raw):
    df = (
        raw
        .set_index('일자')
        .pipe(filter_df_by_valid_assets)
        .pipe(project_df_by_columns)
        .pipe(rename_df_by_columns)
    )
    return df

def get_df_portfolio_by_fund(fund_code, date_ref=None, keys_to_project=None):
    raw = get_df_menu2206_by_fund(fund_code=fund_code, date_ref=date_ref, keys_to_project=keys_to_project)
    return run_pipeline_from_raw_to_portfolio(raw)

get_raw_portfolio_snapshot = get_df_menu2206_snapshot

def get_fund_portfolio_snapshot(date_ref=None):
    raw = get_raw_portfolio_snapshot(date_ref)
    df = (
        raw
        .set_index('일자')
        .pipe(filter_df_by_valid_assets)
        .pipe(lambda df: project_df_by_columns(df, COLUMNS_FOR_PORTFOLIO_SNAPSHOT))
        .pipe(rename_df_by_columns)
    )
    return df

def get_df_asset(df, cols_to_show, mapping_cols):
    return (df
            .pipe(lambda df: project_df_by_columns(df, cols_to_show))
            .pipe(lambda df: rename_df_by_columns(df, mapping_cols)))


def get_dfs_by_asset(df):
    asset_groups = dict(tuple(df.groupby('자산')))
    dfs_asset = {}
    for asset, df_asset in asset_groups.items():
        if asset not in VALID_ASSETS:
            continue        
        if asset == '국내주식':
            df_asset = get_df_asset(df_asset, COLUMNS_FOR_STOCK, MAPPING_COLS_STOCK)
        elif asset == '국내채권':
            df_asset = get_df_asset(df_asset, COLUMNS_FOR_BOND, MAPPING_COLS_BOND)
        elif '선물' in asset:
            df_asset = get_df_asset(df_asset, COLUMNS_FOR_FUTURES, MAPPING_COLS_FUTURES)
        elif '스왑' in asset:
            df_asset = get_df_asset(df_asset, COLUMNS_FOR_TRS, MAPPING_COLS_TRS)
        elif 'ETF' in asset:
            df_asset = get_df_asset(df_asset, COLUMNS_FOR_ETF, MAPPING_COLS_ETF)
        else:
            df_asset = get_df_asset(df_asset, COLUMNS_FOR_PORTFOLIO, MAPPING_COLS)
        dfs_asset[asset] = df_asset.reset_index(drop=True)
    return dfs_asset