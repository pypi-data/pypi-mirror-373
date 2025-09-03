import pandas as pd


def make_dataframe(frame_axis :dict ):
    merge_column = "IND121231312312312321"
    df = pd.DataFrame({ merge_column: [1]})
    #df[merge_column] = 1
    for k in frame_axis.keys():
        df1 = pd.DataFrame()
        df1[k] = frame_axis[k]
        df1[merge_column] =1
        df = df.merge(df1, on=merge_column)

    df = df.drop(merge_column,axis=1)
    return df

def expand_dataframe(df , frame_axis :dict ):
    merge_column = "IND121231312312312321"
    
    df[merge_column] = 1
    for k in frame_axis.keys():
        df1 = pd.DataFrame()
        df1[k] = frame_axis[k]
        df1[merge_column] =1
        df = df.merge(df1, on=merge_column)

    df = df.drop(merge_column,axis=1)
    return df