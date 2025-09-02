from .menu2110_retriever import fetch_data_menu2110
import pandas as pd

def get_df_menu2110(date_ref=None):
    data = fetch_data_menu2110(date_ref=date_ref)
    df = pd.DataFrame(data)
    return df