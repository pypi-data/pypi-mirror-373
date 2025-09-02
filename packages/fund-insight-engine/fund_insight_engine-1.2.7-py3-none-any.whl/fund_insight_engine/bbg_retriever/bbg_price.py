from mongodb_controller import client
from canonical_transformer.morphisms import map_data_to_df

COLLECTION_BBG_PRICE = client['database-bbg']['dataset-PX_LAST']

def fetch_bbg_price_data(ticker_bbg: str):
    pipeline = [
        {
            '$match': {'ticker_bbg': ticker_bbg}
        },
        {
            '$project': {
                '_id': 0, 
                'date_ref': 1, 
                'value': 1, 
                }
        }
    ]

    cursor = COLLECTION_BBG_PRICE.aggregate(pipeline=pipeline)
    data = list(cursor)
    return data

def get_timeseries_bbg_price(ticker_bbg: str):
    data = fetch_bbg_price_data(ticker_bbg=ticker_bbg)
    df = map_data_to_df(data)
    df = (
        df
        .reset_index()
        .drop_duplicates(subset=['date_ref'])
        .set_index('date_ref')
        .sort_index()
        .rename(columns={'value': ticker_bbg})
        .rename_axis('date')
    )
    return df

