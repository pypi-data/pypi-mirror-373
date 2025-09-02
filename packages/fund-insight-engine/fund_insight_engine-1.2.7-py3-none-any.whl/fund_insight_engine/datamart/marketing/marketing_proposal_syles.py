import numpy as np

MAPPING_INDEX_NAME = {
    'KOSPI Index': 'KOSPI',
    'KOSPI2 Index': 'KOSPI 200', 
    'KOSDAQ Index': 'KOSDAQ',
    'SPX Index': 'S&P 500',
    'relative': '초과수익'
}


def update_index(df):
    df.index = df.index.map(lambda x: MAPPING_INDEX_NAME.get(x, x))
    df.index = ['펀드'] + list(df.index[1:])
    return df
    

def style_total_performance(df_total_performance, metrics=None, option_round=2):
    DEFAULT_METRICS = ['annualized_return_days', 'annualized_volatility', 'sharpe_ratio', 'beta', 'winning_ratio', 'maxdrawdown']

    MAPPING_PERFORMANCE_KEYS = {
        'annualized_return_cagr': '연환산 수익률 (CAGR)',
        'annualized_return_days': '연환산 수익률',
        'annualized_volatility': '변동성', 
        'sharpe_ratio': '샤프 비율',
        'beta': '베타',
        'winning_ratio': 'Winning Ratio',
        'maxdrawdown': 'MDD'
    }

    metrics = metrics if metrics else DEFAULT_METRICS

    def process_dataframe(df):
        return (df
                .copy()
                .iloc[:2, :]
                .loc[:, metrics]
                .rename(columns=MAPPING_PERFORMANCE_KEYS)
                .round(option_round))
    
    def correct_winning_ratio(df):
        winning_ratio_col = df.columns.get_loc('Winning Ratio')
        df.iloc[-1, winning_ratio_col] = (1 - df.iloc[0, winning_ratio_col])
        return df
    
    def fillna_beta(df):
        if '베타' in df.columns:
            df['베타'] = df['베타'].fillna('-')
        return df
    
    return (
        df_total_performance
        .pipe(process_dataframe)
        .pipe(update_index)
        .pipe(correct_winning_ratio)
        .pipe(fillna_beta)
    )


def style_period_returns(df_period_returns, option_round=2):
    def map_period_column(column):
        return (column
                .replace('-month', '개월')
                .replace('-year', '년')
                .replace('YTD', 'YTD')
                .replace('Since Inception', '설정 이후'))
    
    return (df_period_returns
            .copy()
            .pipe(update_index)
            .rename(columns=map_period_column)
            .T
            .round(option_round))


def style_monthly_relative(df_monthly_relative, option_round=2):
    def map_month_name(column):
        MAPPING_MONTH_NAMES = {
            'Jan': '1월',
            'Feb': '2월',
            'Mar': '3월',
            'Apr': '4월',
            'May': '5월',
            'Jun': '6월',
            'Jul': '7월',
            'Aug': '8월',
            'Sep': '9월',
            'Oct': '10월',
            'Nov': '11월',
            'Dec': '12월',
        }
        
        # 연도 형식 체크 (20XX)
        if column.isdigit() and len(column) == 4 and column.startswith('20'):
            return 'YTD'
        
        return MAPPING_MONTH_NAMES.get(column, column)

    def correct_relative_value(df):
        df = df.map(lambda x: x if x != '-' else np.nan)
        df.loc['초과수익', :] = df.iloc[0, :] - df.iloc[1, :]
        df = df.fillna('-')
        return df

    df = df_monthly_relative.copy()
    df = update_index(df)
    df.columns = df.columns.map(map_month_name)
    df = df.round(option_round)
    df = correct_relative_value(df)
    return df