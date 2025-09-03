import pandas as pd


def flatten(df,column): 
    return pd.concat([df.drop(columns=column), pd.json_normalize(df[column]) ], axis=1)

def apply_flattened(df, func):
    column_name = "adsdasd32131312324234"
    df[column_name] = df.apply(func , axis = 1)
    df = flatten(df, column_name)
    return df