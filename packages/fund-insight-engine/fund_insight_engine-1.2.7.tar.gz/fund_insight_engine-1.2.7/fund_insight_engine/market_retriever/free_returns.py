import pandas as pd
from mongodb_controller import client
from shining_pebbles import get_today
from universal_timeseries_transformer import transform_timeseries
from canonical_transformer.morphisms import map_data_to_df
from canonical_transformer.functionals import pipe

collection = client['database-rpa']['dataset-menu5105']

def fetch_memnu5105():
    pipeline = [
        {'$project': {'_id': 0, '구간초일': 1, 'Rf': 1}},
    ]
    cursor = collection.aggregate(pipeline)
    data = list(cursor)
    return data

def get_timeseries_free_returns():
    data = fetch_memnu5105()
    return pipe(
        map_data_to_df,
        lambda df: df.rename_axis('date').rename(columns={'Rf': 'return: free'}),
    )(data)

def get_timeseries_zero_returns():
    df = pd.DataFrame(index=pd.date_range(start_date='2020-01-01', end_date=get_today(), freq='D'), data=0)
    df = transform_timeseries(df, 'str')
    return df