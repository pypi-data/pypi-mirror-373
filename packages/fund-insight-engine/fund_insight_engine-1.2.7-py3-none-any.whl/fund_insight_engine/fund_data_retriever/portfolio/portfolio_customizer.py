
def customize_df_portfolio(df):
    df = df.copy()
    df.loc[:,"코드"]=df.종목.str[3:9]
    df=df[df["비중"]>0][["코드","자산","종목명","수량","장부가","평가액","비중","시장비중"]]
    df["장부가"]=(df["장부가"]/1000000).astype(int)
    df["평가액"]=(df["평가액"]/1000000).astype(int)    
    return df