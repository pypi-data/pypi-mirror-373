from aws_s3_controller import load_csv_in_bucket, scan_files_in_bucket_by_regex
from financial_dataset_preprocessor import force_float
from fund_insight_engine.fund_data_retriever.portfolio.portfolio_consts import VALID_ASSETS
from fund_insight_engine.mongodb_retriever.menu2206_retriever.menu2206_utils import get_df_menu2206_snapshot

def filter_valid_assets(df):
    df = df[df['자산'].isin(VALID_ASSETS)]
    return df

def rename_columns_menu2206_snapshot(df):
    COLS_TO_KEEP = ['펀드코드', '종목', '종목명', '원화 보유정보: 장부가액', '원화 보유정보: 평가액', '원화 보유정보: 수량', '종목정보: 상장구분']
    COLS_RENAMED = ['펀드코드', '종목코드', '종목명', '장부가', '평가액', '수량', '상장구분']
    MAPPING_RENAME = dict(zip(COLS_TO_KEEP, COLS_RENAMED))
    df = df[COLS_TO_KEEP].rename(columns=MAPPING_RENAME)
    return df

def parse_stock_code(df):
    df['종목코드'] = df['종목코드'].map(lambda x: x[3:-3])
    return df

def map_listed_or_unlisted(listed_or_unlisted):
    # if listed_or_unlisted == '상장':
    #     return True
    # else:
    #     return False
    if listed_or_unlisted == '상장':
        return '상장'
    elif listed_or_unlisted == '비상':
        return '비상장'
    elif listed_or_unlisted == '미상':
        return '미상'
    else:
        return None

def parse_listed_or_unlisted(df):
    df['상장구분'] = df['상장구분'].map(map_listed_or_unlisted)
    return df

def map_buy_or_sell(buy_or_sell):
    if '매수' in buy_or_sell:
        return 1
    elif '매도' in buy_or_sell:
        return 2
    else:
        return None

def get_full_holdings(date_ref=None):
    df = get_df_menu2206_snapshot(date_ref=date_ref)
    return (
        df
        .copy()
        .pipe(filter_valid_assets)
        .pipe(rename_columns_menu2206_snapshot)
        .pipe(parse_stock_code)
        .pipe(parse_listed_or_unlisted)
        .reset_index(drop=True)
    )

def load_menu2820_snapshot(date_ref=None):
    regex = f'code000000-at{date_ref.replace("-", "")}' if date_ref else 'code000000'
    file_name = scan_files_in_bucket_by_regex(bucket='dataset-system', bucket_prefix='dataset-menu2820-snapshot', regex=regex)[-1]
    df = load_csv_in_bucket(bucket='dataset-system', bucket_prefix='dataset-menu2820-snapshot', regex=file_name)
    return df

def transform_number_columns(df):
    COLS_NUMBERS = ['수량', '취득액', '수수료', '매매손익']
    df['종목'] = df['종목'].astype(str).str.zfill(6)
    for col in COLS_NUMBERS:
        df[col] = df[col].map(force_float)
    return df

def rename_columns_menu2820_snapshot(df):
    COLS_TO_KEEP = ['펀드', '종목', '종목명', '매매처', '매매구분', '수량', '취득액', '수수료', '매매손익']
    COLS_RENAMED = ['펀드코드', '종목코드', '종목명', '매매처', '매매구분', '체결수량', '체결액', '수수료', '매매손익']
    MAPPING_RENAME = dict(zip(COLS_TO_KEEP, COLS_RENAMED))
    df = df[COLS_TO_KEEP].rename(columns=MAPPING_RENAME)
    return df

def aggregate_menu2820_snapshot_by_fund(df):
    df_agg = df.groupby(['펀드코드', '종목코드', '매매구분'], as_index=False).agg({
        '종목명': 'first',
        '체결수량': 'sum',
        '체결액': 'sum',
        '수수료': 'sum',
        '매매손익': 'sum'
    })
    return df_agg

def aggregate_menu2820_snapshot(df):
    df_agg = df.groupby(['종목코드', '매매구분'], as_index=False).agg({
        '종목명': 'first',
        '체결수량': 'sum',
        '체결액': 'sum',
        '수수료': 'sum',
        '매매손익': 'sum'
    })
    return df_agg

def order_columns_df_agg(df):
    COLS_ORDERED = ['종목코드', '종목명', '매매구분', '체결수량', '체결액', '수수료', '매매손익', '매매손익률']
    df = df[COLS_ORDERED]
    return df

def order_columns_df_agg_by_fund(df):
    COLS_ORDERED = ['펀드코드', '종목코드', '종목명', '매매구분', '체결수량', '체결액', '수수료', '매매손익', '매매손익률']
    df = df[COLS_ORDERED]
    return df

def calculate_pnl_ratio(df):
    df['매매손익률'] = df['매매손익'] / df['체결액'] * 100
    return df

def binarize_buy_or_sell(df):
    df['매매구분'] = df['매매구분'].map(map_buy_or_sell)
    return df

def get_trade_executions(date_ref=None):
    df = load_menu2820_snapshot(date_ref=date_ref)
    return (
        df
        .copy()
        .pipe(transform_number_columns)
        .pipe(rename_columns_menu2820_snapshot)
        .pipe(aggregate_menu2820_snapshot)
        .pipe(calculate_pnl_ratio)
        .pipe(order_columns_df_agg)
        .pipe(binarize_buy_or_sell)
    )

def get_trade_executions_by_fund(date_ref=None):
    df = load_menu2820_snapshot(date_ref=date_ref)
    return (
        df
        .copy()
        .pipe(transform_number_columns)
        .pipe(rename_columns_menu2820_snapshot)
        .pipe(aggregate_menu2820_snapshot_by_fund)
        .pipe(calculate_pnl_ratio)
        .pipe(order_columns_df_agg_by_fund)
        .pipe(binarize_buy_or_sell)
    )
