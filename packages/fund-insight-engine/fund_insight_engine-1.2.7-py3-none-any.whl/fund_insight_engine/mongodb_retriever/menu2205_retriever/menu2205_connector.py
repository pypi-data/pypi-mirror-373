from mongodb_controller import client

# MongoDB Database and Collection Constants
DATABASE_NAME_RPA = 'database-rpa'
COLLECTION_NAME_MENU2205 = 'dataset-menu2205'
COLLECTION_NAME_MENU2205_SNAPSHOT = 'dataset-menu2205-snapshot'

collection_menu2205 = client[DATABASE_NAME_RPA][COLLECTION_NAME_MENU2205]
collection_menu2205_snapshot = client[DATABASE_NAME_RPA][COLLECTION_NAME_MENU2205_SNAPSHOT]

def test_menu2205():
    return collection_menu2205.find_one()

def test_menu2205_snapshot():
    return collection_menu2205_snapshot.find_one()
