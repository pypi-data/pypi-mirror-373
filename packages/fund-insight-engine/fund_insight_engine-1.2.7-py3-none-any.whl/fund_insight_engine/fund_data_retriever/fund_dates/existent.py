from mongodb_controller import COLLECTION_8186

def get_all_existent_dates_in_collection(collection, key_for_date):
    return sorted(collection.distinct(key_for_date))
