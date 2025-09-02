from canonical_transformer import get_inverse_mapping


MAPPING_TICKER_BBG_INDEX = {
    'KOSPI Index':  'KOSPI',
    'KOSDAQ Index': 'KOSDAQ',
    'KOSPI2 Index': 'KOSPI200',
    'SPX Index': 'S_P500',
    'CCMP Index': 'NASDAQ',
    'INDU Index': 'DOW',
    'NKY Index': 'NIKKEI',
    'SHCOMP Index': 'SHANGHAI',
    'HSI Index': 'HANGSENG',
    'DAX Index': 'DAX',
    'UKX Index': 'FTSE',
    'RTSI$ Index': 'RTS',
    'IBOV Index': 'BOVESPA',
    'SENSEX Index': 'SENSEX'
    # 'GVSK3YR Index': '국고채(3년)',
}

MAPPING_TICKER_BBG_CURNCY = {
    'USDKRW Curncy': 'USD',
    'CNYKRW Curncy': 'CNY',
    'EURKRW Curncy': 'EUR',
    'JPYKRW Curncy': 'JPY',    
    'HKDKRW Curncy': 'HKD',
}

MAPPING_PSEUDO_TICKER = {
    '회사채(AA-,3년)': '회사채(AA-,3년)',
    '국고채(3년)': '국고채(3년)',
    'CD': 'CD',
    'CP': 'CP',
    'CALL': 'CALL',
}


INVERSE_MAPPING_TICKER_BBG_INDEX = get_inverse_mapping(MAPPING_TICKER_BBG_INDEX)
INVERSE_MAPPING_TICKER_BBG_CURNCY = get_inverse_mapping(MAPPING_TICKER_BBG_CURNCY)

TICKER_COLLECTION_GLOBAL_CURRENCY = 'GLOBAL Curncy'
TICKER_COLLECTION_KOREA_BOND = 'KR Bond'
TICKER_COLLECTION_KOREA_INDEX = 'KR Index'
TICKER_COLLECTION_US_INDEX = 'US Index'
TICKER_COLLECTION_ASIA_INDEX = 'ASIA Index'
TICKER_COLLECTION_ETC1_INDEX = 'ETC1 Index'

KOREA_BBG_TICKERS_INDEX = ['KOSPI Index', 'KOSDAQ Index', 'KOSPI2 Index', 'KOSPI200 Index']
US_BBG_TICKERS_INDEX = ['SPX Index', 'CCMP Index', 'INDU Index']
GLOBAL_BBG_TICKERS_CURNCY = ['USDKRW Curncy', 'CNYKRW Curncy', 'EURKRW Curncy', 'JPYKRW Curncy', 'HKDKRW Curncy']

TICKERS_MARKET_INDEX = list(MAPPING_TICKER_BBG_INDEX.keys())
TICKERS_MARKET_CURRENCY = list(MAPPING_TICKER_BBG_CURNCY.keys())
TICKERS_MARKET_BOND = list(MAPPING_PSEUDO_TICKER.keys())