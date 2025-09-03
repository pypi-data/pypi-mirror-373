import pandas as pd
import dataframe_helpers as dfh


def chunk(df, bins):
    
    central_labels = (bins[:-1] + bins[1:]) / 2  # Calculate central values of bins


    return  pd.cut(df, bins=bins, labels=central_labels, right=False).astype(float)


def calculate_efficiency(df_in, axis , condition):
    df = df_in.copy()
    df[axis["name"]+"_cunked"] = chunk(df[axis["name"]], axis["bin"])
    df1 = dfh.group_apply(df, 
                [axis["name"]+"_cunked"], ["efficiency" ], 
                lambda x: 
                    sum(
                    condition(x)  
                )/(len(x)+0.000000000001)
                         )
    return df1
                    
            