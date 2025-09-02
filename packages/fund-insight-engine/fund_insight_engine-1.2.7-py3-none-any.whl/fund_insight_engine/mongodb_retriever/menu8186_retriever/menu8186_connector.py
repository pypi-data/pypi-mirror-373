from mongodb_controller import COLLECTION_8186

collection_menu8186 = COLLECTION_8186

def test_menu8186():
    return collection_menu8186.find_one()
