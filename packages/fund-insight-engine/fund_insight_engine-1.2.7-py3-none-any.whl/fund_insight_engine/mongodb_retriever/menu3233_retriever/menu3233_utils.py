from .menu3233_retriever import fetch_data_menu3233
import pandas as pd

def get_df_menu3233(date_ref=None):
    data = fetch_data_menu3233(date_ref=date_ref)
    df = pd.DataFrame(data)
    return df