

from dataframe_helpers.generic import to_array


def group_iter(df, group_cols):
    for _, group in df.groupby(group_cols, group_keys=False):
        yield group


def chunk_data(df, columns, output , compr):
    columns = to_array(columns)
    for g in group_iter(df, columns ):
        g_idx = g.index
        
        
        
        c = compr()
        
        for i in g_idx:
            x = df.loc[i]
            df.at[i, output]  = c(x)
            
    return df