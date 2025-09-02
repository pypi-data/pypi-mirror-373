from string_date_controller import get_date_n_years_ago

def get_default_date_ref(date_start, date_end):
    if '-01-01' in date_end:
        date_end = get_date_n_years_ago(date_end, 1)
    date_ref = f'{date_end[:4]}-01-01' 
    if date_ref < date_start:
        date_ref = date_start
    return date_ref