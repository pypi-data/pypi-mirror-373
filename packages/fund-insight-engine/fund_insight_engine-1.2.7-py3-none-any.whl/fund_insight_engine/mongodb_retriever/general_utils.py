import pandas as pd

def get_latest_date_in_collection(collection, key_for_date):
    data = (
        collection.
        find({}, {key_for_date: 1})
        .sort(key_for_date, -1)
        .limit(1)
    )
    return data[0][key_for_date]

def fetch_data_for_snapshot_menu_by_date(collection, date_ref=None):
    latest_date = get_latest_date_in_collection(collection, 'date_ref')
    date_ref = date_ref if date_ref else latest_date
    pipeline = [
        {'$match': {'date_ref': date_ref}},
        {'$project': {'_id': 0, 'data': 1}}
    ]
    cursor = collection.aggregate(pipeline)
    data = list(cursor)[0]['data']
    return data

def get_df_for_snapshot_menu_by_date(collection, date_ref=None):
    data = fetch_data_for_snapshot_menu_by_date(collection, date_ref=date_ref)
    df = pd.DataFrame(data)
    return df