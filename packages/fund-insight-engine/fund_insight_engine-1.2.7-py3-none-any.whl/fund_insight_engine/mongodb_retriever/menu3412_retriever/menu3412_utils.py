from .menu3412_retriever import fetch_data_menu3412
import pandas as pd

def get_df_menu3412(date_ref=None):
    data = fetch_data_menu3412(date_ref=date_ref)
    df = pd.DataFrame(data)
    return df