import pandas as pd


def merge(df_dict, df1_str, df2_str, on, **kwargs):
    def add_prefix(df, prefix, exclude=[]):
        return df.rename(columns=lambda x: f'{prefix}{x}' if x not in exclude else x)
    
    df1 = add_prefix(df_dict[df1_str].copy(), df1_str + ".", exclude=on)
    df2 = add_prefix(df_dict[df2_str].copy(), df2_str + ".", exclude=on)

    merged_df = pd.merge(df1, df2, on=on, **kwargs)
    
    return merged_df