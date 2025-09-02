import pandas as pd
from mongodb_controller import COLLECTION_8186

pipeline = [
    {
        "$sort": {"일자": 1, "_id": -1} 
    },
    {
        "$group": {
            "_id": "$일자",
            "KOSPI지수": {"$first": "$KOSPI지수"},
            "KOSDAQ지수": {"$first": "$KOSDAQ지수"},
            "KOSPI200지수": {"$first": "$KOSPI200지수"}
        }
    },
    {
        "$project": {
            "_id": 0,
            "date": "$_id",  
            "KOSPI": "$KOSPI지수", 
            "KOSDAQ": "$KOSDAQ지수", 
            "KOSPI200": "$KOSPI200지수" 
        }
    },
    {
        "$sort": {"date": 1}
    }
]

def fetch_data_korea_benchmarks():
    cursor = COLLECTION_8186.aggregate(pipeline)
    data = list(cursor)
    return data

def get_timeseries_korea_benchmarks():
    data = fetch_data_korea_benchmarks()
    df = pd.DataFrame(data).set_index('date')
    return df

def get_timeseries_kospi():
    df = get_timeseries_korea_benchmarks()
    return df[['KOSPI']]

def get_timeseries_kosdaq():
    df = get_timeseries_korea_benchmarks()
    return df[['KOSDAQ']]       

def get_timeseries_kospi200():
    df = get_timeseries_korea_benchmarks()
    return df[['KOSPI200']]