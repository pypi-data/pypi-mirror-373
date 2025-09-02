from functools import partial
from .basis import get_menu1100_indices, get_menu1100_index
from .consts import TICKER_COLLECTION_ASIA_INDEX

get_asia_indices = partial(get_menu1100_indices, ticker_collection=TICKER_COLLECTION_ASIA_INDEX)
get_asia_index = partial(get_menu1100_index, ticker_collection=TICKER_COLLECTION_ASIA_INDEX)
